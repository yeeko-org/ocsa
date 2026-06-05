"""Diagnóstico de acceso a fuentes del scraper (Cloudflare, proxy, TLS).

Script autónomo, no depende de Django para los modos de red; sí lo
arranca para ejercitar el get_content real. Dos modos según el primer
argumento:

    # Modo Jornada — matriz completa contra el challenge de Cloudflare.
    python source/scraper/scraper_access_test.py [YYYY/MM/DD]

    # Modo URL genérica — para cualquier otra fuente (Reforma, etc.).
    python source/scraper/scraper_access_test.py <url> [--proxy] [--xml]

        --proxy  ejercita get_content() real con with_proxy=True
        --xml    usa parser="xml" en get_content() real

Lee PROXY_KEY directamente del .env en la raíz del proyecto.
"""
import os
import sys
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
    PROXY_KEY = os.getenv("PROXY_KEY")
except ImportError:
    PROXY_KEY = None


UA_OLD = "Mozilla/4.0"
UA_CHROME = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Juego completo de headers de un Chrome real en Windows.
BROWSER_HEADERS = {
    "User-Agent": UA_CHROME,
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "sec-ch-ua": (
        '"Chromium";v="120", "Not(A:Brand";v="24", '
        '"Google Chrome";v="120"'
    ),
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Connection": "keep-alive",
}


def build_proxies() -> dict | None:
    """Ambas claves con esquema http:// (correcto para proxy con CONNECT)."""
    if not PROXY_KEY:
        return None
    return {
        "http": f"http://{PROXY_KEY}",
        "https": f"http://{PROXY_KEY}",
    }


def classify(resp: requests.Response) -> str:
    """Traduce la respuesta a un veredicto legible."""
    cf = resp.headers.get("cf-mitigated")
    if resp.status_code == 200:
        return "OK (contenido servido)"
    if cf == "challenge" or "Just a moment" in resp.text:
        return "BLOQUEADO por Cloudflare (managed challenge / TLS)"
    if resp.status_code == 403:
        return "403 (prohibido, sin marca de challenge)"
    if resp.status_code == 407:
        return "407 (proxy rechaza credenciales)"
    return f"status {resp.status_code}"


def probe(label: str, url: str, *, proxies=None, headers=None) -> None:
    try:
        resp = requests.get(
            url, headers=headers, proxies=proxies, timeout=40)
        print(f"  {label:38} -> {classify(resp)}  "
              f"[{resp.status_code}, {len(resp.text)} bytes]")
    except Exception as exc:  # noqa: BLE001 - diagnóstico, queremos todo
        cause = exc
        while cause.__cause__ or cause.__context__:
            cause = cause.__cause__ or cause.__context__
            if "407" in str(cause) or "Tunnel" in str(cause):
                break
        print(f"  {label:38} -> ERROR {type(exc).__name__}: "
              f"{str(cause)[:70]}")


def _curl_cffi_probe(label: str, url: str, px: str | None) -> None:
    from curl_cffi import requests as creq
    try:
        resp = creq.get(
            url, impersonate="chrome",
            proxies={"https": px, "http": px} if px else None, timeout=40)
        verdict = ("OK" if resp.status_code == 200 and
                   "Just a moment" not in resp.text
                   else "bloqueado/challenge")
        print(f"  {label:38} -> {verdict}  "
              f"[{resp.status_code}, {len(resp.text)} bytes]")
    except Exception as exc:  # noqa: BLE001
        print(f"  {label:38} -> ERROR {type(exc).__name__}: "
              f"{str(exc)[:60]}")


def probe_curl_cffi(url: str, proxies: dict | None) -> None:
    """Impersonación de TLS, con y sin proxy, para ver si el proxy sobra."""
    try:
        import curl_cffi  # noqa: F401
    except ImportError:
        print("  curl_cffi NO instalado (pip install curl_cffi) — omitido")
        return
    # curl_cffi espera el proxy como una sola URL, no el dict de requests.
    px = proxies["https"] if proxies else None
    _curl_cffi_probe("curl_cffi chrome SIN proxy", url, None)
    if px:
        _curl_cffi_probe("curl_cffi chrome CON proxy", url, px)


def probe_real_get_content(
    url: str, with_proxy: bool = False, parser: str = "html.parser"
) -> None:
    """Ejercita la función real get_content (arranca Django)."""
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    flags = f"with_proxy={with_proxy}, parser={parser!r}"
    try:
        import django
        django.setup()
        from source.scraper.scraper_base import get_content
        soup = get_content(url, parser, with_proxy)
        tags = len(soup.find_all(True))
        print(f"  get_content({flags})")
        print(f"      -> OK [{len(str(soup))} bytes, {tags} nodos]")
    except Exception as exc:  # noqa: BLE001
        print(f"  get_content({flags})")
        print(f"      -> ERROR {type(exc).__name__}: {str(exc)[:70]}")


def run_jornada_mode(fecha: str, proxies: dict | None) -> None:
    url = f"https://www.jornada.com.mx/{fecha}/"
    print(f"\nModo Jornada — destino: {url}")
    _print_proxy_status()

    print("\n[1] Salud del proxy (destino neutro httpbin):")
    if proxies:
        probe("proxy -> httpbin/ip", "http://httpbin.org/ip",
              proxies=proxies)
    else:
        print("  sin proxy configurado")

    print("\n[2] Jornada — variantes de acceso:")
    probe("sin proxy + UA viejo", url, headers={"User-Agent": UA_OLD})
    probe("sin proxy + headers Chrome", url, headers=BROWSER_HEADERS)
    if proxies:
        probe("con proxy + UA viejo", url,
              proxies=proxies, headers={"User-Agent": UA_OLD})
        probe("con proxy + headers Chrome", url,
              proxies=proxies, headers=BROWSER_HEADERS)

    print("\n[3] Impersonación de TLS (la prueba que debería pasar):")
    probe_curl_cffi(url, proxies)

    print("\n[4] Función real get_content (integración con el scraper):")
    probe_real_get_content(url)
    print()


def run_url_mode(
    url: str, proxies: dict | None, with_proxy: bool, parser: str
) -> None:
    print(f"\nModo URL — destino: {url}")
    _print_proxy_status()

    print("\n[1] Salud del proxy (destino neutro httpbin):")
    if proxies:
        probe("proxy -> httpbin/ip", "http://httpbin.org/ip",
              proxies=proxies)
    else:
        print("  sin proxy configurado")

    print("\n[2] Acceso directo (requests, delata TLS de Python):")
    probe("sin proxy + headers Chrome", url, headers=BROWSER_HEADERS)
    if proxies:
        probe("con proxy + headers Chrome", url,
              proxies=proxies, headers=BROWSER_HEADERS)

    print("\n[3] Impersonación de TLS (curl_cffi):")
    probe_curl_cffi(url, proxies)

    print("\n[4] Función real get_content (integración con el scraper):")
    probe_real_get_content(url, with_proxy=with_proxy, parser=parser)
    print()


def _print_proxy_status() -> None:
    user = PROXY_KEY.split(":")[0] if PROXY_KEY else "n/a"
    status = "cargada" if PROXY_KEY else "NO encontrada"
    print(f"PROXY_KEY: {status} (usuario: {user})")


def main() -> None:
    args = sys.argv[1:]
    flags = {a for a in args if a.startswith("--")}
    positional = [a for a in args if not a.startswith("--")]
    target = positional[0] if positional else "2025/01/30"
    proxies = build_proxies()

    if target.startswith("http"):
        run_url_mode(
            target, proxies,
            with_proxy="--proxy" in flags,
            parser="xml" if "--xml" in flags else "html.parser")
    else:
        run_jornada_mode(target, proxies)


if __name__ == "__main__":
    main()
