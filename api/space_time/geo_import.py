"""Lectura de archivos geográficos exportados desde QGIS."""

from __future__ import annotations

import json
import math
import zipfile
from pathlib import Path
from typing import Any, Callable

import numpy as np
import shapely
from pyogrio import list_layers
from pyogrio.raw import read
from pyproj import CRS, Transformer

MAX_FILE_BYTES = 20 * 1024 * 1024
SUPPORTED_SUFFIXES = {".geojson", ".json", ".zip", ".kml"}
ZIP_INNER_SUFFIXES = {".shp", ".geojson", ".json", ".kml"}
WGS84 = CRS.from_epsg(4326)


class GeoImportError(ValueError):
    """Falla legible por el editor: se muestra tal cual en el front."""


def read_geo_file(path: str | Path, filename: str,
                  layer: str | None = None) -> dict:
    """FeatureCollection en EPSG:4326 y 2D con las propiedades del archivo.

    La colección lleva un miembro extra `properties` (permitido por el
    RFC 7946) con lo que el llamador necesita para avisar al editor:
    capa leída, CRS de origen y cuántas geometrías traía el archivo.
    """
    path = Path(path)
    _check_file(path, filename)
    dataset = _dataset_path(path, filename)
    layer_name = _pick_layer(dataset, filename, layer)
    meta, _, geometries, field_data = read(
        dataset, layer=layer_name, force_2d=True)
    if geometries is None or not len(geometries):
        raise GeoImportError(
            f"El archivo «{filename}» no contiene geometrías.")
    source_crs = _source_crs(meta.get("crs"), filename)
    transform = _transform_for(source_crs)
    fields = [str(name) for name in _as_list(meta.get("fields"))]
    features = []
    for index, wkb in enumerate(geometries):
        geometry = _geometry_from_wkb(wkb, transform)
        if geometry is None:
            continue
        features.append({
            "type": "Feature",
            "properties": _properties(fields, field_data, index),
            "geometry": geometry,
        })
    if not features:
        raise GeoImportError(
            f"El archivo «{filename}» no contiene geometrías válidas.")
    return {
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "layer": layer_name,
            "source_crs": source_crs.to_string(),
            "reprojected": transform is not None,
            "geometries_read": int(len(geometries)),
        },
    }


def _check_file(path: Path, filename: str) -> None:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise GeoImportError(
            f"Formato no admitido: «{suffix or filename}». Se admiten "
            "GeoJSON (.geojson, .json), shapefile comprimido (.zip) y "
            "KML (.kml).")
    if path.stat().st_size > MAX_FILE_BYTES:
        limit = MAX_FILE_BYTES // (1024 * 1024)
        raise GeoImportError(
            f"El archivo pesa más de {limit} MB. Recorta la capa en QGIS "
            "y vuelve a exportarla.")


def _dataset_path(path: Path, filename: str) -> str:
    if Path(filename).suffix.lower() != ".zip":
        return str(path)
    return f"/vsizip/{path}{_zip_folder(path, filename)}"


def _zip_folder(path: Path, filename: str) -> str:
    """Subcarpeta del zip donde están las capas; GDAL no la busca solo."""
    try:
        with zipfile.ZipFile(path) as bundle:
            names = bundle.namelist()
    except zipfile.BadZipFile as error:
        raise GeoImportError(
            f"El archivo «{filename}» no es un zip válido.") from error
    inner = sorted(
        name for name in names
        if Path(name).suffix.lower() in ZIP_INNER_SUFFIXES)
    if not inner:
        raise GeoImportError(
            f"El zip «{filename}» no contiene ninguna capa (.shp, .kml o "
            "GeoJSON).")
    parent = Path(inner[0]).parent.as_posix()
    return "" if parent == "." else f"/{parent}"


def _pick_layer(dataset: str, filename: str, layer: str | None) -> str:
    try:
        layers = list_layers(dataset)
    except Exception as error:
        raise GeoImportError(
            f"No se pudo leer «{filename}»: {error}") from error
    names = [str(row[0]) for row in layers]
    if not names:
        raise GeoImportError(
            f"El archivo «{filename}» no contiene ninguna capa.")
    if layer:
        if layer not in names:
            raise GeoImportError(
                f"La capa «{layer}» no existe en «{filename}». Capas "
                f"disponibles: {', '.join(names)}.")
        return layer
    if len(names) > 1:
        raise GeoImportError(
            f"El archivo «{filename}» tiene varias capas: "
            f"{', '.join(names)}. Elige cuál importar.")
    return names[0]


def _source_crs(crs: Any, filename: str) -> CRS:
    if not crs:
        raise GeoImportError(
            f"El archivo «{filename}» no declara sistema de coordenadas. "
            "Vuelve a exportarlo desde QGIS incluyendo el CRS (para el "
            "shapefile, el archivo .prj).")
    try:
        return CRS.from_user_input(crs)
    except Exception as error:
        raise GeoImportError(
            f"No se reconoce el sistema de coordenadas de «{filename}» "
            f"({crs}).") from error


def _transform_for(source: CRS) -> Callable | None:
    """`None` cuando el archivo ya viene en WGS84 y no hay que reproyectar."""
    if source.equals(WGS84):
        return None
    transformer = Transformer.from_crs(source, WGS84, always_xy=True)

    def reproject(coordinates: np.ndarray) -> np.ndarray:
        lon, lat = transformer.transform(
            coordinates[:, 0], coordinates[:, 1])
        return np.column_stack([lon, lat])

    return reproject


def _geometry_from_wkb(wkb: Any, transform: Callable | None) -> dict | None:
    if wkb is None:
        return None
    geometry = shapely.from_wkb(wkb)
    if geometry is None or geometry.is_empty:
        return None
    if transform is not None:
        geometry = shapely.transform(geometry, transform)
    return json.loads(shapely.to_geojson(geometry))


def _as_list(value: Any) -> list:
    """`meta` trae ndarrays, cuyo valor de verdad no se puede evaluar."""
    return [] if value is None else list(value)


def _properties(fields: list[str], field_data: Any, index: int) -> dict:
    return {
        name: _json_safe(column[index])
        for name, column in zip(fields, _as_list(field_data))
    }


def _json_safe(value: Any) -> Any:
    """Los campos vienen como escalares de numpy, que no son JSON."""
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, (bytes, bytearray)):
        return None
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
