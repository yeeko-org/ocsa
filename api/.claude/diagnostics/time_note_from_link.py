"""Cronometra el pipeline «nota desde enlace» (`source/note_from_link.py`
y `source/link_match.py`).

Gasta: golpea el proxy, PressReader y Gemini (las pasadas que el
artículo no tenga, más el cotejo de títulos cuando hace falta). Corre la
cadena que el hilo de la vista lanza (sin hilo y sin escribir el
comentario) sobre una nota desechable que borra al terminar. No
sobrescribe nada: la clasificación que el lote ya dejó en el `Article` se
reutiliza, y lo que se corre aquí se queda en el artículo, ya sin nota.
Sí crea artículos: si hubo que raspar el listado (días o meses sin
lote), los del listado se quedan en el registro sintético de la fuente
hasta que un lote real los reclame. Imprime el comentario que el hilo
habría dejado.

    python api/.claude/diagnostics/time_note_from_link.py   # casos fijos
    python api/.claude/diagnostics/time_note_from_link.py \\
        --link URL --date YYYY-MM-DD --title "..." [--user EMAIL]
    ... [--no-gemini] [--keep]

`--no-gemini` se detiene antes de la primera pasada, pero no es gratis:
el cotejo por Gemini dentro de `prepare_article` (cuando URL, título
exacto, contención y similitud no bastan) sí se llama. `--keep` conserva
la nota creada.
"""
import argparse
import os
import sys
from datetime import date
from unittest import mock

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from profile_auth.models import User  # noqa: E402
from source import note_from_link  # noqa: E402
from source.models import Note  # noqa: E402

CASES = [
    ("https://www.jornada.com.mx/2025/01/12/politica/009n2pol",
     "2025-01-12",
     "Semar edifica 4 mil viviendas para reubicar a familias asentadas "
     "cerca del Tren Interoceánico"),
    ("https://www.jornada.com.mx/2025/01/07/estados/021n3est",
     "2025-01-07",
     "Defensores de bosques en Tlaxiaco respaldan protesta en El Milagro"),
    ("https://www.reforma.com/cuestiona-filme-densificacion-de-sac-"
     "granaditas/ar3053228",
     "2025-08-10", "Cuestiona filme densificación de SAC Granaditas"),
    ("https://www.reforma.com/policia-en-frontera-sur-obedece-al-crimen/"
     "ar2948665",
     "2025-02-05", "Policía en frontera sur obedece ¡al crimen!"),
    ("https://proceso.pressreader.com/proceso/20251201/page/38/textview",
     "2025-12-15",
     "El Segundo Piso de la 4T adopta la bomba hídrica de Carlos Salinas"),
]
STAGES = ("listing", "match", "scrape", "attachment",
          "first", "second", "precapture")


def run_case(link: str, date_str: str, title: str, user: User | None,
             no_gemini: bool, keep: bool) -> dict:
    day = date.fromisoformat(date_str)
    try:
        source = note_from_link.resolve_source(link)
    except note_from_link.NoteFromLinkError as exc:
        return {"link": link, "failed": exc.as_response()}
    note = Note.objects.create(
        title=title, link=link, date=day, source=source)
    try:
        if no_gemini:
            with mock.patch.object(note_from_link, "run_gemini_chain"):
                report = note_from_link.fetch_note_from_link(note, user)
        else:
            report = note_from_link.fetch_note_from_link(note, user)
    except note_from_link.NoteFromLinkError as exc:
        note.delete()
        return {"link": link, "failed": exc.as_response(),
                "comment": note_from_link.failure_comment(
                    exc.reason, exc.extra.get("match"))}
    article = note.articles.first()
    result = {"link": link, "note": note.id,
              "comment": note_from_link.outcome_comment(report),
              **report.summary(article),
              "files": note.files.count()}
    if not keep:
        note.delete()
    return result


def print_table(results: list) -> None:
    header = "caso | " + " | ".join(STAGES) + " | total | 1ª | 2ª"
    print("\n" + header)
    for idx, res in enumerate(results, start=1):
        if "failed" in res:
            print(f"{idx} | FALLÓ: {res['failed']}")
            continue
        timings = res["timings"]
        cells = [f"{timings[s]:.2f}" if s in timings else "-"
                 for s in STAGES]
        total = sum(timings.values())
        print(f"{idx} | " + " | ".join(cells) + f" | {total:.2f} | "
              f"{res['certainty_degree']} | "
              f"{res['second_certainty_degree']}")
    for idx, res in enumerate(results, start=1):
        print(f"\n[{idx}] {res}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--link")
    parser.add_argument("--date")
    parser.add_argument("--title")
    parser.add_argument("--user")
    parser.add_argument("--no-gemini", action="store_true")
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args()

    user = User.objects.get(email=args.user) if args.user else None
    if args.link:
        cases = [(args.link, args.date, args.title)]
    else:
        cases = CASES
    results = []
    for link, date_str, title in cases:
        print(f"\n=== {link}")
        results.append(run_case(
            link, date_str, title, user, args.no_gemini, args.keep))
    print_table(results)


if __name__ == "__main__":
    main()
