"""Actores de cada fusión de pueblos indígenas propuesta, para aprobarlas una
por una antes de cargar el catálogo del INPI. Solo lee.

Estado y municipio son los de las ubicaciones de los proyectos donde el
actor participa (el actor no tiene ubicación propia); sin participaciones
con ubicación, los de la ubicación legacy del opositor, marcados «legacy:».

    DATABASE_NAME=ocsa-prod-20261108 DATABASE_LEGACY_NAME=ocsa-prod-20261108 \
        python api/.claude/diagnostics/indigenous_merge_report.py
"""
import os
import sys

import django

BASE = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, BASE)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.db import connection  # noqa: E402

# entrada actual → pueblo oficial (nombre canónico del JSON)
MERGES = {
    "Ayuuk": "Mixe",
    "Binnizá": "Zapoteco",
    "Zapoteca": "Zapoteco",
    "Guarijíos": "Guarijío",
    "Macurawe": "Guarijío",
    "Huichol": "Wixárika",
    "Ikoot": "Ikoots",
    "Mayo-yoreme": "Mayo",
    "Yoreme": "Mayo",
    "Yoremes": "Mayo",
    "Náyeri": "Cora",
    "Purépecha": "P'urhépecha",
    "Rarámuri": "Tarahumara",
    "Tarahumaras": "Tarahumara",
    "Seris": "Seri",
    "Tlapanecos": "Me'phaa",
    "Totonaca": "Totonaco",
    "Tzeltal": "Tseltal",
    "Yokotán": "Yokot'an",
    "Ñomdaa": "Amuzgo",
    "ñhöñhö": "Otomí",
    "Nahum": "Nahua",
}

# Casos sin fusión obvia: se listan para decidir, con el destino posible.
CASES = {
    "Chontal": "¿Chontal de Oaxaca? (el nombre solo es ambiguo)",
    "Xk'eek'en": "¿Maya? (es un cenote de Dzitnup, Valladolid)",
    "Yumana": "familia yumana: Kumiai, Paipai, Cucapá, Kiliwa, Cochimí",
    "Comunidades aledañas": "no es un pueblo",
}

ACTORS_SQL = """
with modern as (
  select p.actor_id,
         string_agg(distinct s.name, '; ') states,
         string_agg(distinct m.name || ' (' || s.short_name || ')', '; ')
           municipalities
  from actor_participant p
  join source_mention mn on mn.id = p.mention_id
  join space_time_location l on l.project_id = mn.project_id
  left join space_time_state s on s.id = l.state_id
  left join space_time_municipality m on m.id = l.municipality_id
  group by p.actor_id),
legacy as (
  select o.actor_id,
         string_agg(distinct o.type_model || ':' || o.origin_id, ' ')
           origins,
         string_agg(distinct coalesce(u.estado, u2.estado), '; ') l_states,
         string_agg(distinct coalesce(u.municipio, u2.municipio), '; ')
           l_munis,
         string_agg(distinct op.pueblo_indigena, '; ') pueblo_raw,
         min(o.created_at)::date migrated
  from actor_originreference o
  left join ocs.opositores op
    on o.type_model = 'Opositores' and op.id = o.origin_id
  left join ocs.opositores_to_ubicaciones ou on ou.opositor_id = op.id
  left join ocs.ubicaciones u on u.id = ou.ubicacion_id
  left join ocs.poblaciones_afectadas pa
    on o.type_model = 'PoblacionAfectada' and pa.id = o.origin_id
  left join ocs.ubicaciones u2 on u2.id = pa.ubicacion_id
  group by o.actor_id)
select a.id, a.name, a.status_validation_id,
       case when md.actor_id is null then 'legacy: ' || lg.l_states
            else md.states end,
       case when md.actor_id is null then lg.l_munis
            else md.municipalities end,
       lg.origins, lg.pueblo_raw,
       (select count(*) from actor_participant p where p.actor_id = a.id)
from actor_actor a
join classify_indigenousgroup g on g.id = a.indigenous_group_id
left join modern md on md.actor_id = a.id
left join legacy lg on lg.actor_id = a.id
where trim(g.name) = %s
order by a.id
"""


def cell(v):
    return str(v if v not in (None, "") else "—").replace("|", "/")


def main():
    with connection.cursor() as cur:
        cur.execute("set search_path to ocsa, ocs, public")
        print("\n### Fusiones obvias")
        report(cur, MERGES)
        print("\n### Casos a decidir")
        report(cur, CASES)


def report(cur, mapping):
    for old, new in mapping.items():
        cur.execute(
            "select id from classify_indigenousgroup where trim(name) = %s",
            [old])
        row = cur.fetchone()
        cur.execute(ACTORS_SQL, [old])
        rows = cur.fetchall()
        gid = row[0] if row else "?"
        print(f"\n#### #{gid} «{old}» → {new} ({len(rows)} actores)\n")
        print("| id | actor | status | estado | municipio | origen "
              "legacy | pueblo_indigena legacy | partic. |")
        print("|---|---|---|---|---|---|---|---|")
        for r in rows:
            print("| " + " | ".join(cell(v) for v in r) + " |")


main()
