"""Deriva pueblo → estados del catálogo de comunidades del micrositio del INPI
y lo escribe en classify/data/inpi_pueblos_estados_<fecha>.json, la fuente
que `load_inpi_catalog` usa para el M2M IndigenousGroup.states.

Cada ficha de pueblo (catalogo.inpi.gob.mx/<pueblo>/) trae una tabla de
wp-data-access cargada por admin-ajax.php con un nonce propio de la página;
el script baja la página, saca el nonce y la publicación, y pagina la tabla.
Solo se conserva el estado (y cuántas comunidades tiene ahí el pueblo).

El servidor no manda el intermedio de GeoTrust: va en --cacert, nunca -k.

    python api/.claude/diagnostics/fetch_inpi_states.py \
        --cacert /tmp/inpi_dl/bundle.pem
"""
import argparse
import datetime
import json
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "classify" / "data"
CATALOG = DATA / "inpi_pueblos_2025-02-21.json"
AJAX = "https://catalogo.inpi.gob.mx/wp-admin/admin-ajax.php"
CALL = re.compile(
    r"wpda_datatables_ajax_call\(([^)]*\"Catalogo2024_1\"[^)]*)\)")
PAGE = 1000


def fetch(url, context, data=None):
    body = urllib.parse.urlencode(data).encode() if data else None
    request = urllib.request.Request(
        url, data=body, headers={"User-Agent": "Mozilla/5.0 (OCSA)"})
    with urllib.request.urlopen(request, context=context, timeout=90) as r:
        return r.read().decode("utf-8")


def table_rows(url, context):
    html = fetch(url, context)
    match = CALL.search(html)
    if not match:
        raise RuntimeError(f"sin tabla de comunidades en {url}")
    args = match.group(1)
    pub_id = re.search(r"_advanced_options,\s*(\d+)", args).group(1)
    nonce = re.findall(r"\"([0-9a-f]{10})\"", args)[-1]
    rows, start = [], 0
    while True:
        data = {
            "action": "wpda_datatables", "wpnonce": nonce, "pubid": pub_id,
            "draw": 1, "start": start, "length": PAGE,
            "search[value]": "", "search[regex]": "false",
            "filter_field_name": "", "filter_field_value": "", "nl2br": "",
        }
        for i in range(7):
            data[f"columns[{i}][data]"] = i
            data[f"columns[{i}][searchable]"] = "true"
        payload = json.loads(fetch(AJAX, context, data))
        rows += payload["data"]
        start += PAGE
        if start >= int(payload["recordsFiltered"]):
            return rows
        time.sleep(0.5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cacert", required=True)
    opts = parser.parse_args()
    context = ssl.create_default_context(cafile=opts.cacert)
    pueblos = json.loads(CATALOG.read_text(encoding="utf-8"))["pueblos"]
    today = datetime.date.today().isoformat()
    out = {}
    for pueblo in pueblos:
        url, shared = pueblo["microsite_url"], None
        if not url:
            # Pirinda no tiene ficha propia (enlace roto): sus comunidades
            # vienen juntas en la de «Matlatzinca o Pirinda», sin separar.
            host = next(p for p in pueblos if p["microsite_url"]
                        and pueblo["dof_name"] in p["microsite_name"])
            url, shared = host["microsite_url"], host["dof_name"]
        rows = table_rows(url, context)
        labels = Counter(r[0] for r in rows)
        states = Counter(r[2].strip() for r in rows if r[2])
        out[pueblo["dof_name"]] = {
            "url": url, "communities": len(rows),
            "labels": dict(labels), "states": dict(sorted(states.items())),
        }
        if shared:
            out[pueblo["dof_name"]]["shared_page_with"] = shared
        print(f"{pueblo['dof_name']}: {len(rows)} comunidades, "
              f"{len(states)} estados {dict(labels)}", file=sys.stderr)
        time.sleep(0.5)
    target = DATA / f"inpi_pueblos_estados_{today}.json"
    target.write_text(json.dumps({
        "title": "Estados donde el INPI registra comunidades de cada pueblo",
        "source": "Tablas «Consulta catálogo por pueblo» del micrositio "
                  "catalogo.inpi.gob.mx (Catalogo2024_1, wp-data-access)",
        "retrieved": today,
        "script": "api/.claude/diagnostics/fetch_inpi_states.py",
        "fields": {
            "communities": "Filas de la tabla de la ficha del pueblo",
            "shared_page_with": "Pueblo cuya ficha se usó porque este no "
                                "tiene propia; sus estados son los de esa "
                                "ficha completa",
            "labels": "Valores de la columna «Pueblo» en la tabla de la "
                      "ficha, con su número de filas",
            "states": "Entidad federativa → número de comunidades",
        },
        "pueblos": out,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(target, file=sys.stderr)


main()
