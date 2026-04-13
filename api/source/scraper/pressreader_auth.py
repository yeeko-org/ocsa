"""
Autenticación y gestión de sesiones contra PressReader.

Este módulo centraliza todo el trato con el vendor PressReader (login,
logout, liveness). Está separado de los scrapers de publicaciones
específicas (Proceso, y eventualmente otras como Nexos) porque la
lógica de sesión es del vendor, no de la publicación.

## Ciclo de vida de sesión

PressReader limita el número de sesiones simultáneas por cuenta. Un
test controlado (ver historial de git: `test_force_signout.py`)
demostró que el flag `forceSignOut=true` del signin NO invalida el
Bearer token previo — este sigue vivo hasta su TTL natural. La única
vía para liberar un slot es llamar explícitamente a `signout_with_token`.

Por eso el flujo canónico aquí es:
  1. `get_pressreader_token()` consulta el modelo `PressReaderSession`
     (singleton lógico: una fila).
  2. Si hay fila y `revalidate_if_stale()` confirma que el token vive,
     se reutiliza.
  3. Si no hay fila o el token está muerto, se hace signOut explícito
     del anterior (si existía) ANTES de un login nuevo, para no
     acumular huérfanas.

El management command `close_pressreader_session` permite cerrar
manualmente la sesión (útil al terminar la jornada en local).

## Credenciales requeridas (.env)
- PRESSREADER_USER
- PRESSREADER_PASS

## Códigos de Status de PressReader
- Status 0: Éxito
- Status 1: Error genérico
- Status 2: Has excedido el número de sesiones simultáneas
            (correr `python manage.py close_pressreader_session`)
"""

import urllib.parse
from typing import Optional

import requests
from django.conf import settings
from django.utils import timezone


PRESSREADER_API_BASE = "https://ingress.pressreader.com/services"

# TTL para liveness check: si el token se validó hace menos de este
# tiempo, se asume vivo sin volver a golpear la API.
LIVENESS_TTL_SECONDS = 600  # 10 minutos

# CID por defecto para el liveness check. Cualquier CID al que la
# cuenta tenga acceso sirve; usamos el de Proceso por ser el único
# consumidor activo. Si se añaden publicaciones, seguir siendo válido.
DEFAULT_LIVENESS_CID = "24em"


def _browser_headers() -> dict:
    """Headers base que replican un navegador — varios endpoints los exigen."""
    return {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) "
            "Gecko/20100101 Firefox/147.0"
        ),
        "Accept": "*/*",
        "Accept-Language": "es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://proceso.pressreader.com",
        "Referer": "https://proceso.pressreader.com/proceso",
    }


def get_pressreader_headers(bearer_token: str) -> dict:
    """Headers de autorización para consumir la API de PressReader."""
    return {
        "Authorization": f"Bearer {bearer_token}",
        "User-Agent": "Mozilla/5.0",
    }


def _do_fresh_login() -> str:
    """
    Ejecuta el flujo completo de login contra PressReader y devuelve el
    bearerToken. No toca el modelo — úsese solo desde `get_pressreader_token`
    o desde tests que manejen su propio ciclo de signOut.

    Flujo (4 pasos):
      1. Visitar proceso.pressreader.com para obtener cookie AProfile (ticket)
      2. POST /authentication/v1/initialize -> token anónimo
      3. POST /auth/Signin con credenciales -> signInToken
      4. POST /authentication/v1/signIn con signInToken -> bearerToken final
    """
    user = getattr(settings, "PRESSREADER_USER", None)
    password = getattr(settings, "PRESSREADER_PASS", None)

    if not user or not password:
        raise ValueError(
            "PRESSREADER_USER y PRESSREADER_PASS deben estar configurados en .env"
        )

    session = requests.Session()
    base_headers = _browser_headers()

    # Paso 1: obtener cookie AProfile
    try:
        session.get(
            "https://proceso.pressreader.com/proceso",
            headers=base_headers, timeout=30,
        )
        ticket = session.cookies.get("AProfile")
        if not ticket:
            raise ValueError("No se obtuvo cookie AProfile")
    except Exception as e:
        raise ValueError(f"Error al acceder a proceso.pressreader.com: {e}")

    # Paso 2: token anónimo
    init_url = "https://proceso.pressreader.com/authentication/v1/initialize"
    init_body = {
        "tickets": [ticket],
        "language": "es-mx",
        "urlReferrer": "https://proceso.pressreader.com/",
        "url": "https://proceso.pressreader.com/proceso",
    }
    try:
        init_response = session.post(
            init_url,
            headers={**base_headers, "Content-Type": "application/json"},
            json=init_body, timeout=30,
        )
        anon_token = (
            init_response.json().get("bearerToken")
            if init_response.status_code == 200 else None
        )
    except Exception as e:
        raise ValueError(f"Error al inicializar sesión: {e}")
    if not anon_token:
        raise ValueError("No se pudo obtener token anónimo de PressReader")

    # Paso 3: signin con credenciales
    signin_url = f"{PRESSREADER_API_BASE}/auth/Signin"
    signin_headers = {
        **base_headers,
        "Authorization": f"Bearer {anon_token}",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }
    signin_body = urllib.parse.urlencode({
        "userName": user,
        "password": password,
        "reCaptchaVersion": "3",
        "reCaptchaToken": "",
        # NOTA: forceSignOut=true NO invalida tokens previos (verificado
        # experimentalmente). Se mantiene por si PressReader lo cambia o
        # afecta otros contadores internos, pero el sistema no depende
        # de él — el signOut explícito en `get_pressreader_token` es la
        # única garantía real de liberar el slot anterior.
        "forceSignOut": "true",
    })
    try:
        signin_response = session.post(
            signin_url, headers=signin_headers,
            data=signin_body, timeout=30,
        )
    except Exception as e:
        raise ValueError(f"Error en signin de PressReader: {e}")

    if signin_response.status_code != 200:
        raise ValueError(
            f"Error en signin: {signin_response.status_code} "
            f"- {signin_response.text[:200]}"
        )

    signin_data = signin_response.json()
    status_code = signin_data.get("Status")
    if status_code == 2:
        raise ValueError(
            "PressReader Status 2: Has excedido el número de sesiones "
            "simultáneas. Corre `python manage.py close_pressreader_session` "
            "para liberar slot antes de reintentar."
        )
    if status_code not in (0, None):
        raise ValueError(f"PressReader Status {status_code}: {signin_data}")

    sign_in_token = signin_data.get("Token") or signin_data.get("signInToken")
    tickets = signin_data.get("tickets", [])
    if not sign_in_token:
        raise ValueError(f"No se obtuvo Token: {signin_data}")

    # Paso 4: completar signin
    complete_url = "https://proceso.pressreader.com/authentication/v1/signIn"
    complete_body = {
        "signInToken": sign_in_token,
        "tickets": tickets,
        "language": "es-mx",
        "enableAutoLogin": True,
    }
    try:
        complete_response = session.post(
            complete_url,
            headers={**base_headers, "Content-Type": "application/json"},
            json=complete_body, timeout=30,
        )
    except Exception as e:
        raise ValueError(f"Error al completar signin: {e}")

    if complete_response.status_code != 200:
        raise ValueError(
            f"Error al completar signin: {complete_response.status_code} "
            f"- {complete_response.text[:200]}"
        )

    bearer_token = complete_response.json().get("bearerToken")
    if not bearer_token:
        raise ValueError(
            f"No se obtuvo bearerToken: {complete_response.json()}"
        )
    return bearer_token


def signout_with_token(token: str) -> bool:
    """
    Cierra la sesión asociada al bearer token. Verificado
    experimentalmente: este endpoint SÍ libera el slot del lado del
    servidor (a diferencia de `forceSignOut=true` en el signin).

    Returns:
        bool: True si la API respondió 200, False en cualquier otro caso.
    """
    signout_url = f"{PRESSREADER_API_BASE}/auth/SignOut"
    try:
        response = requests.post(
            signout_url,
            headers={
                **_browser_headers(),
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={}, timeout=30,
        )
        if response.status_code == 200:
            print(f"  ✓ Sesión cerrada: {token[:40]}...")
            return True
        print(f"  ✗ SignOut HTTP {response.status_code}: {token[:40]}...")
        return False
    except Exception as e:
        print(f"  ✗ Excepción en signOut {token[:40]}...: {e}")
        return False


def check_token_alive(token: str, cid: str = DEFAULT_LIVENESS_CID) -> bool:
    """
    Liveness check contra un endpoint autenticado. Usa cache-busting
    para evitar falsos positivos por caché de CDN.

    Returns:
        True si la API respondió 200; False en 401/403 o cualquier error.
    """
    bust = int(timezone.now().timestamp() * 1000)
    url = f"{PRESSREADER_API_BASE}/calendar/get?cid={cid}&_={bust}"
    headers = {
        **_browser_headers(),
        "Authorization": f"Bearer {token}",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    try:
        r = requests.get(url, headers=headers, timeout=30)
        return r.status_code == 200
    except Exception as e:
        print(f"  ⚠ liveness check falló: {e}")
        return False


def get_pressreader_token() -> str:
    """
    Devuelve un Bearer token válido de PressReader.

    Flujo:
      1. Lee `PressReaderSession` (singleton lógico). Si existe y su
         token pasa el liveness check (o fue validado hace poco), lo
         reutiliza.
      2. Si el token previo está muerto o no existe, hace signOut
         explícito del viejo (si aplica) antes de relogin.
      3. Hace login nuevo vía `_do_fresh_login` y persiste.

    Racional del signOut explícito: `forceSignOut=true` del signin no
    invalida tokens previos (ver test en historial de git). Saltar el
    signOut deja huérfana cada vez que se relogea, hasta saturar el
    límite del servidor.
    """
    # Import diferido para evitar ciclo con source.models
    from source.models import PressReaderSession

    active: Optional[PressReaderSession] = PressReaderSession.get_active()
    if active and active.revalidate_if_stale():
        return active.bearer_token

    # Necesitamos login nuevo. Matar el viejo primero (best-effort).
    if active:
        try:
            signout_with_token(active.bearer_token)
        except Exception as e:
            print(f"  ⚠ signOut del token previo lanzó excepción: {e}")
        active.delete()

    new_token = _do_fresh_login()
    PressReaderSession.objects.create(bearer_token=new_token)
    return new_token