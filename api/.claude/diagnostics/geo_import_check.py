"""Diagnóstico de `space_time.geo_import`: lectura de archivos de QGIS.

Fabrica en un directorio temporal los casos que llegan del editor
(GeoJSON, shapefile comprimido en otro CRS, KML, mezcla de tipos,
shapefile sin .prj, KML de varias capas) y verifica el camino completo
`read_geo_file` → `normalize_geojson`. No toca la base ni la red.

    python .claude/diagnostics/geo_import_check.py
"""
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import shapely
from pyogrio.raw import write

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

from space_time.geo_import import (  # noqa: E402
    GeoImportError, read_geo_file)
from space_time.geometry import normalize_geojson  # noqa: E402

PASSED = []
FAILED = []


def check(name, condition, detail=""):
    (PASSED if condition else FAILED).append(name)
    mark = "ok  " if condition else "FALLA"
    print(f"  {mark} {name}{f' — {detail}' if detail else ''}")


def expect_error(name, fragment, function, *args, **kwargs):
    try:
        function(*args, **kwargs)
    except GeoImportError as error:
        check(name, fragment in str(error), str(error))
    except ValueError as error:
        check(name, fragment in str(error), str(error))
    else:
        check(name, False, "no lanzó error")


def write_layer(path, geometries, crs, driver, fields=None, values=None,
                geometry_type=None, layer=None):
    field_data = [np.array(values)] if values is not None else []
    geometry_type = geometry_type or geometries[0].geom_type
    write(
        str(path), shapely.to_wkb(np.array(geometries)), field_data,
        np.array(fields or [], dtype=object), driver=driver, crs=crs,
        geometry_type=geometry_type, layer=layer)


def square(x, y, size=1.0):
    return shapely.Polygon([
        (x, y), (x + size, y), (x + size, y + size), (x, y + size), (x, y)])


def zip_shapefile(folder, base, target, drop_prj=False):
    with zipfile.ZipFile(target, "w") as bundle:
        for part in sorted(folder.glob(f"{base}.*")):
            if drop_prj and part.suffix == ".prj":
                continue
            bundle.write(part, f"capas/{part.name}")
    return target


def run(work):
    print("\n1. GeoJSON con dos polígonos (EPSG:4326)")
    path = work / "dos_poligonos.geojson"
    write_layer(path, [square(-99.1, 19.4), square(-99.0, 19.5)],
                "EPSG:4326", "GeoJSON")
    collection = read_geo_file(path, path.name)
    check("lee 2 features", len(collection["features"]) == 2)
    check("no reproyecta", collection["properties"]["reprojected"] is False)
    feature = normalize_geojson(collection, "polygon")
    check("fusiona en MultiPolygon",
          feature["geometry"]["type"] == "MultiPolygon",
          feature["geometry"]["type"])
    check("conserva 2 partes", len(feature["geometry"]["coordinates"]) == 2)

    print("\n2. Shapefile comprimido en EPSG:6372 con 3 líneas")
    folder = work / "shp"
    folder.mkdir()
    lines = [
        shapely.LineString([(2_500_000 + i * 1000, 900_000),
                            (2_501_000 + i * 1000, 901_000)])
        for i in range(3)]
    write_layer(folder / "lineas.shp", lines, "EPSG:6372", "ESRI Shapefile",
                fields=["nombre"], values=["a", "b", "c"])
    bundle = zip_shapefile(folder, "lineas", work / "lineas.zip")
    collection = read_geo_file(bundle, bundle.name)
    check("lee el zip sin descomprimir", len(collection["features"]) == 3)
    check("marca reproyección", collection["properties"]["reprojected"])
    lon, lat = collection["features"][0]["geometry"]["coordinates"][0]
    check("reproyecta a grados", -120 < lon < -85 and 12 < lat < 33,
          f"({lon:.4f}, {lat:.4f})")
    check("conserva propiedades",
          collection["features"][0]["properties"]["nombre"] == "a")
    feature = normalize_geojson(collection, "line")
    check("fusiona en MultiLineString",
          feature["geometry"]["type"] == "MultiLineString")

    print("\n3. KML con un polígono")
    path = work / "poligono.kml"
    write_layer(path, [square(-103.4, 20.6)], "EPSG:4326", "KML",
                layer="unica")
    collection = read_geo_file(path, path.name)
    feature = normalize_geojson(collection, "polygon")
    check("lee KML de una capa",
          feature["geometry"]["type"] == "Polygon",
          feature["geometry"]["type"])

    print("\n4. KML con dos capas")
    path = work / "dos_capas.kml"
    write_layer(path, [square(-103.4, 20.6)], "EPSG:4326", "KML",
                layer="norte")
    write(str(path), shapely.to_wkb(np.array([square(-103.4, 19.6)])), [],
          np.array([], dtype=object), driver="KML", crs="EPSG:4326",
          geometry_type="Polygon", layer="sur", append=True)
    expect_error("exige elegir capa", "varias capas",
                 read_geo_file, path, path.name)
    collection = read_geo_file(path, path.name, layer="sur")
    check("acepta la capa pedida",
          collection["properties"]["layer"] == "sur")
    expect_error("rechaza capa inexistente", "no existe",
                 read_geo_file, path, path.name, layer="este")

    print("\n5. GeoJSON que mezcla tipos")
    path = work / "mezcla.geojson"
    write_layer(path, [square(-99.1, 19.4),
                       shapely.LineString([(-99.2, 19.3), (-99.1, 19.2)])],
                "EPSG:4326", "GeoJSON", geometry_type="Unknown")
    collection = read_geo_file(path, path.name)
    expect_error("normalize rechaza la mezcla", "distinto tipo",
                 normalize_geojson, collection, "polygon")

    print("\n6. Shapefile sin .prj")
    folder = work / "sin_prj"
    folder.mkdir()
    write_layer(folder / "mudo.shp", [square(-99.1, 19.4)], "EPSG:4326",
                "ESRI Shapefile")
    bundle = zip_shapefile(folder, "mudo", work / "mudo.zip", drop_prj=True)
    expect_error("exige CRS", "sistema de coordenadas",
                 read_geo_file, bundle, bundle.name)

    print("\n7. Rechazos de entrada")
    path = work / "otro.txt"
    path.write_text("nada")
    expect_error("rechaza formato ajeno", "Formato no admitido",
                 read_geo_file, path, path.name)

    print("\n8. Tipo distinto al de la ubicación")
    path = work / "un_poligono.geojson"
    write_layer(path, [square(-99.1, 19.4)], "EPSG:4326", "GeoJSON")
    collection = read_geo_file(path, path.name)
    expect_error("polígono en ubicación de línea", "que espera LineString",
                 normalize_geojson, collection, "line")


def main():
    work = Path(tempfile.mkdtemp(prefix="geo_import_check_"))
    try:
        run(work)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f"\n{len(PASSED)} ok, {len(FAILED)} fallas")
    for name in FAILED:
        print(f"  - {name}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
