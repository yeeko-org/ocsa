# -*- coding: utf-8 -*-
"""Tabla fuente de los 57 dictámenes manuales de topónimos legados.

`resolve_legacy_names` deja en `sin_resolver` los fragmentos que ningún
candidato del catálogo explica. Estos son los que además tienen proyecto:
se dictaminaron uno por uno y la razón de cada uno vive en `TABLE`, no en
el CSV, para que el dictamen se pueda revisar y regenerar.

Lee `.claude/legacy_names_verdicts_project.csv` (la rebanada con proyecto
del corrido de `resolve_legacy_names`) y reescribe el CSV que consume el
`--fill`:

    python api/.claude/diagnostics/legacy_names_manual.py
"""
import csv
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

D = "a_details"; L = "llenar"; I = "inutil"; X = "irresoluble"
COL = "colonia o pueblo urbano de la CDMX; el catálogo INEGI solo trae la alcaldía"
# (location_id, legacy_value) -> (verdict, candidate_name, candidate_id, reason)
TABLE = {
 (104, "Bosques de las Lomas"): (D, "", "", COL),
 (114, "Lomas de Chapultepec"): (D, "", "", COL),
 (302, "Bosques de San Elías Repechique"): (D, "", "", "comunidad rarámuri sin fila en el catálogo; el San Elías Repechique del INEGI está en Bocoyna, no en Guachochi"),
 (1129, "Lomas de Santa María"): (D, "", "", "fraccionamiento urbano de Morelia, no una localidad del catálogo"),
 (1544, "Polanco"): (D, "", "", COL),
 (2400, "Polanco"): (D, "", "", COL),
 (3804, "Saratoga esquina con Eje 8 Sur"): (D, "", "", "cruce de calles: es una referencia de domicilio, no un topónimo"),
 (4430, "Bocoyvo"): (L, "Bocoybo (Repogueachi)", "63560", "variante v/b de Bocoybo, en Batopilas: coincide con el municipio que el mismo comentario no encontró"),
 (4513, "Hopelchén"): (X, "", "", "Hopelchén es municipio de Campeche y la ubicación tiene capturado Yucatán: corregirlo mueve el estado, no solo el municipio"),
 (12302, "Loreto"): (X, "", "", "dos localidades de Chínipas lo llevan en el nombre —Ignacio Valenzuela Lagarda (Loreto) y Los Alamillos de Loreto, esta última ya capturada— y nada en el proyecto desempata"),
 (12315, "Creel"): (I, "", "", "Creel es de Bocoyna, Chihuahua, y la ubicación es el río Tula en Hidalgo: captura equivocada"),
 (12324, "Coatzacoalcos"): (D, "", "", "municipio de Veracruz en una ubicación capturada en Oaxaca; el corredor sí llega ahí, así que vale como referencia"),
 (12324, "Puerto de Salina Cruz"): (D, "", "", "el corredor abarca muchos municipios; fijar una sola localidad falsearía el trazo"),
 (12337, "Tecate, Tijuana, playas de rosarito y ensenada"): (D, "", "", "lista de cuatro municipios: no cabe en una llave foránea"),
 (12337, "Valle de San Quintín"): (D, "", "", "región agrícola, no una localidad del catálogo"),
 (12345, "San jeronimo"): (D, "", "", COL),
 (12356, "Catorce, Charcas, Matehuala, Villa de Guadalupe, Villa de La Paz y Villa de Ramos"): (D, "", "", "lista de seis municipios: no cabe en una llave foránea"),
 (12356, "wirikuta"): (D, "", "", "territorio sagrado wixárika, sin fila en el catálogo del INEGI"),
 (12381, "San Ángel"): (D, "", "", COL),
 (12393, "Pueblo Xoco"): (D, "", "", COL),
 (12422, "Espacio Cumbres"): (D, "", "", "nombre del desarrollo y de su colonia en Monterrey, no una localidad"),
 (12424, "Santa Fe"): (D, "", "", COL),
 (12449, "Ampliación Alpes"): (D, "", "", COL),
 (12460, "Bosques de las Lomas"): (D, "", "", COL),
 (12462, "Barranca del Moral"): (D, "", "", COL),
 (12466, "Centro histórico"): (D, "", "", COL),
 (12469, "Puerto Morelos"): (X, "", "", "Puerto Morelos es de Quintana Roo y la ubicación tiene capturado Yucatán: corregirlo mueve el estado"),
 (12470, "San Pancho"): (I, "", "", "apodo de San Francisco, Bahía de Banderas, que ya está capturada en la ubicación"),
 (12473, "Roma Norte"): (D, "", "", COL),
 (12476, "Lomas Hipódromo"): (D, "", "", "colonia de Naucalpan, no una localidad del catálogo"),
 (12477, "San José insurgentes"): (D, "", "", COL),
 (12478, "El Contadero"): (D, "", "", COL),
 (12481, "Roma"): (D, "", "", COL),
 (12482, "Tlaltenango"): (D, "", "", "colonia y pueblo urbano de Cuernavaca; el catálogo solo trae las localidades rurales del municipio"),
 (12487, "Anzures"): (D, "", "", COL),
 (12489, "Centro histórico"): (D, "", "", COL),
 (12514, "El Contadero"): (D, "", "", COL),
 (12523, "Sonora"): (I, "", "", "se capturó el nombre del estado en el campo de localidad"),
 (12529, "El Águila"): (I, "", "", "repite el nombre de la mina (el propio proyecto); San Pedro Totolápam no tiene esa localidad"),
 (12553, "Poblado Cieneguita Lluvia de Oro"): (L, "Cieneguita Lluvia de Oro", "82263", "el prefijo «Poblado» es lo único que estorbaba; la localidad ya está capturada"),
 (12570, "Taico"): (L, "Tampico", "2035", "errata de Tampico: el otro fragmento del mismo comentario nombra la localidad Tampico"),
 (12570, "Tampico"): (L, "Tampico", "252759", "cabecera de Tampico (297 373 hab.); el municipio queda fijado por el fragmento hermano"),
 (12584, "Miguel Hidalgo"): (D, "", "", "colonia Miguel Hidalgo de Cuernavaca, no una localidad del catálogo"),
 (12601, "Santa Úrsula Xitla"): (D, "", "", COL),
 (12643, "Los Napuchis"): (X, "", "", "Carichí tiene siete localidades homónimas Napuchi/Napuchis (de 0 a 95 habitantes) y nada desempata; con geometría, el backfill la calcularía"),
 (12677, "Av. 5 de Mayo, No. 62"): (D, "", "", "domicilio, no un topónimo"),
 (12697, "Valle Poniente"): (D, "", "", "fraccionamiento de Santa Catarina, no una localidad del catálogo"),
 (12737, "San Antonio"): (D, "", "", COL),
 (12742, "Av. Casa de la Moneda"): (D, "", "", "domicilio, no un topónimo"),
 (12748, "Roma Norte"): (D, "", "", COL),
 (12749, "Roma Norte"): (D, "", "", COL),
 (12778, "Polanco"): (D, "", "", COL),
 (12779, "Playa Chacala"): (D, "", "", "Chacala es de Compostela y la ubicación está capturada en Bahía de Banderas: la playa vale como referencia"),
 (12885, "San Nicolás Totolapan"): (L, "Ejido de San Nicolás Totolapan", "84076", "coincide al 100 % en La Magdalena Contreras, el municipio que el mismo comentario no encontró"),
 (12887, "Vicente Guerrero"): (D, "", "", COL),
 (12919, "Ranchería Ocampo"): (D, "", "", "Ocampo no tiene una localidad con ese nombre; «ranchería» describe el asentamiento"),
 (16218, "Pueblo Cuautepec"): (D, "", "", COL),
}

src = os.path.join(BASE, ".claude/legacy_names_verdicts_project.csv")
rows = [r for r in csv.DictReader(open(src)) if r["verdict"] == "sin_resolver"]
missing = [(r["location_id"], r["legacy_value"]) for r in rows
           if (int(r["location_id"]), r["legacy_value"]) not in TABLE]
assert not missing, missing
out = os.path.join(
    BASE, ".claude/verdicts/legacy_names_manual_project.csv")
fields = ["location_id", "project_id", "legacy_value", "scope_municipality",
          "has_geometry", "verdict", "candidate_name", "candidate_id",
          "reason"]
with open(out, "w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=fields)
    writer.writeheader()
    for r in rows:
        verdict, name, cid, reason = TABLE[(int(r["location_id"]),
                                            r["legacy_value"])]
        writer.writerow({
            "location_id": r["location_id"], "project_id": r["project_id"],
            "legacy_value": r["legacy_value"],
            "scope_municipality": r["scope_municipality"],
            "has_geometry": r["has_geometry"], "verdict": verdict,
            "candidate_name": name, "candidate_id": cid, "reason": reason})
from collections import Counter
print("filas:", len(rows), Counter(TABLE[(int(r['location_id']), r['legacy_value'])][0] for r in rows))
print("CSV:", out)
