

# import json and filter by keys and values
import json
import csv
from typing import List, Dict

# Example of data
# {
#     "id": 2954,
#     "nota_id": null,
#     "titulo": "La Caravana por el agua y el ecologismo de los pueblos",
#     "autor": "Raúl Romero",
#     "nombre_medio": "La Jornada",
#     "fecha": null,
#     "vinculo": "https://www.jornada.com.mx/2022/03/31/opinion/015a2pol",
#     "opositores": [
#         "Opositores al PIM",
#         "Opositores a Planta Bonafont, Puebla"
#     ],
#     "acciones_colectivas": [
#         "Acción directa"
#     ],
#     "afectaciones_ecologicas": [
#         "Agua"
#     ],
#     "afectaciones_sociales": [
#         "Afectaciones a bienes y servicios"
#     ],
#     "hechos_violencia": [
#         "Privación de la vida",
#         "Represión de la protesta social"
#     ],
#     "proyectos": [
#         "Gasoducto PIM",
#         "Planta Bonafont Juan C Bonilla, Puebla",
#         "Proyecto Integral Morelos (PIM)"
#     ],
#     "tipos_despliegue": [
#         "Extractivismo energético",
#         "Hiperurbanización",
#         "Mixto: Extractivismo hídrico / Extractivismo energético"
#     ],
#     "estados": [
#         "Morelos",
#         "Puebla"
#     ],
#     "oposicion": []
# },

# import data in utf-8
data = json.load(open('utils/all_notes.json', 'r', encoding='utf-8'))

# filter by key estados: "Ciudad de México" and "tipo_despliegue": contains "Hiperurbanización"
def filter_data(data: List[Dict[str, str]]) -> List[Dict[str, str]]:
    notes = []
    for note in data:
        if 'Ciudad de México' in note['estados'] and 'Hiperurbanización' in note['tipos_despliegue']:
            notes.append(note)
    return notes


filtered_data = filter_data(data)


# write csv file with filtered data in utf-8
def write_csv(all_data: List[Dict[str, str]]) -> None:
    from django.conf import settings
    base_dir = settings.BASE_DIR
    # is_local = settings.IS_LOCAL
    print("base_dir", base_dir)

    # csv_path = f"{base_dir}\\fixture\\filtered_notes.csv"
    csv_path = "utils/filtered_notes.csv"
    print("csv_path", csv_path)

    # delimiter; "|"  and encoding='utf-8
    with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=all_data[0].keys())
        writer.writeheader()
        for row in all_data:
            writer.writerow(row)
    # close and save file
    file.close()


write_csv(filtered_data)

