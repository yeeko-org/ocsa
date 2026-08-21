"""Imágenes del PDF de La Jornada: estáticos locales y fotos remotas.

Los estáticos del sitio (logo, banderillas, cabeceras de sección) se
versionan en ``jornada_assets/`` porque no cambian y traerlos en cada
render ataría la generación de la nota a la disponibilidad del sitio.
Las fotos del artículo sí viajan por red: son distintas en cada nota.
"""

import base64
import mimetypes
from pathlib import Path

import requests

ASSETS_DIR = Path(__file__).resolve().parent / "jornada_assets"

SITE_ROOT = "https://www.jornada.com.mx"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like "
    "Gecko) Chrome/126.0.0.0 Safari/537.36"
)

PHOTO_TIMEOUT = 15


def data_uri(content: bytes, mime: str = "image/jpeg") -> str:
    """Empotra la imagen en el marcado, para no dejar archivos temporales."""
    encoded = base64.b64encode(content).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def local_asset(name: str) -> str | None:
    """Estático versionado del sitio, o None si no lo tenemos.

    Las secciones sin banderilla propia (``columnas``, ``editorial``:
    tres artículos en todo el acervo) devuelven None y se imprimen sin
    ella, en vez de tumbar el render.
    """
    path = ASSETS_DIR / name
    if not path.exists():
        return None
    mime = mimetypes.guess_type(name)[0] or "image/png"
    return data_uri(path.read_bytes(), mime)


def remote_image(url: str) -> str | None:
    """Foto del artículo desde el sitio; None si la red o el sitio fallan.

    Una foto perdida degrada el PDF, no lo cancela: la nota se crea igual.
    """
    try:
        response = requests.get(
            url, headers={"User-Agent": USER_AGENT}, timeout=PHOTO_TIMEOUT)
    except requests.RequestException:
        return None
    if response.status_code != 200 or not response.content:
        return None
    mime = (response.headers.get("Content-Type") or "").split(";")[0]
    if not mime.startswith("image/"):
        mime = mimetypes.guess_type(url)[0] or "image/jpeg"
    return data_uri(response.content, mime)
