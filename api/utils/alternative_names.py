"""Nombres alternativos en texto separado por comas (Actor, Project,
IndigenousGroup): comparación plegada y alta sin duplicados.

Un alternativo solo lleva información nueva: nunca repite el nombre ni,
en «Ñomndaa (Amuzgo)», ninguna de sus dos partes, que la búsqueda ya
encuentra en el nombre.
"""
import re
import unicodedata

# Los apóstrofos tipográficos y el diacrítico suelto valen lo mismo que el
# recto: «Me´phaa» y «Me'phaa» son la misma grafía capturada de dos formas.
APOSTROPHES = str.maketrans({c: "'" for c in "’‘´`ʾʼ¨"})


def normalize_name(text: str | None) -> str:
    text = (text or "").translate(APOSTROPHES).casefold().strip()
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


def name_forms(name: str | None) -> set[str]:
    """El nombre plegado y, si lleva paréntesis, cada una de sus partes."""
    forms = {normalize_name(name)}
    if parts := re.fullmatch(r"(.*?)\s*\((.+)\)\s*", name or ""):
        forms |= {normalize_name(parts[1]), normalize_name(parts[2])}
    forms.discard("")
    return forms


def split_names(text: str | None) -> list[str]:
    return [n.strip() for n in (text or "").split(",") if n.strip()]


def join_names(names: list[str], exclude: str | None = None) -> str:
    seen = name_forms(exclude)
    out = []
    for name in names:
        if name and normalize_name(name) not in seen:
            seen.add(normalize_name(name))
            out.append(name.strip())
    return ", ".join(out)


def add_alternative_names(obj, names: list[str],
                          name_field: str = "name") -> bool:
    """Agrega `names` a `obj.alternative_names` sin repetir ninguno ni el
    propio nombre o sus partes; de paso limpia los que ya había. Devuelve
    si cambió; no guarda."""
    before = obj.alternative_names or ""
    after = join_names(
        split_names(before) + list(names),
        exclude=getattr(obj, name_field, None))
    if after == before:
        return False
    obj.alternative_names = after or None
    return True
