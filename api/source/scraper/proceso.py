"""
Scraper de Proceso usando la API de PressReader.
Hecho por Martín Szyszlican <martin@abrimos.info>

Este scraper obtiene artículos de la revista Proceso a través de la API de PressReader.
A diferencia de otros scrapers (Reforma, Jornada), este trabaja con ediciones mensuales
y requiere autenticación con Bearer token.

Flujo de la API de PressReader:
1. GET /catalog/v1/routes/publication?publication=proceso -> obtiene CID (24em)
2. GET /IssueInfo/GetIssueInfoByCid?cid=24em&issueDate=YYYYMMDD -> obtiene Issue ID
3. GET /pagesMetadata/?issue={issue_id} -> obtiene páginas y lista de artículos
4. GET /Articles/GetItems?articles[]={id1}&articles[]={id2} -> obtiene contenido completo

Credenciales requeridas en .env:
- PRESSREADER_USER
- PRESSREADER_PASS

Códigos de Status de PressReader:
- Status 0: Éxito
- Status 1: Error genérico
- Status 2: Has excedido el número de sesiones simultáneas
          (ejecutar: python close_pressreader_sessions.py)
"""

import atexit
import time
import urllib.parse
from datetime import date, datetime
from typing import List

import requests
from django.conf import settings

from source.models import ScrapedRecord, Source
from source.scraper.articles import ArticleScraper, MainScraper, ManagerScraper
from source.scraper.scraper_base import get_json_content

# URL base de la API de PressReader
PRESSREADER_API_BASE = "https://ingress.pressreader.com/se2skyservices"

# CID de Proceso en PressReader (se puede obtener dinámicamente)
PROCESO_CID = "24em"

# Cache para el token de PressReader (evita múltiples logins)
_pressreader_token_cache: dict = {}

# Historial de tokens usados (para poder cerrar sesiones antiguas)
_pressreader_token_history: list = []

# Flag para controlar si el cleanup automático está habilitado
_auto_cleanup_enabled: bool = False


# GESTIÓN DE TOKENS Y SESIONES DE PRESSREADER
def _cleanup_pressreader_sessions():
    """
    Función de cleanup que se ejecuta automáticamente al salir del programa.
    Cierra todas las sesiones conocidas para no dejar sesiones abiertas.
    """
    if not _auto_cleanup_enabled:
        return

    if _pressreader_token_history:
        print("\n" + "=" * 60)
        print("Limpiando sesiones de PressReader al finalizar...")
        print("=" * 60)
        closed = 0
        for token in _pressreader_token_history:
            try:
                if signout_with_token(token):
                    closed += 1
            except KeyboardInterrupt:
                print("\n⚠ Cleanup interrumpido por el usuario")
                break
            except Exception:
                # Ignorar errores individuales y continuar con los siguientes tokens
                continue
        if closed > 0:
            print(f"✓ Se cerraron {closed} sesiones automáticamente")


def enable_auto_cleanup():
    """
    Habilita el cierre automático de sesiones al finalizar el programa.
    """
    global _auto_cleanup_enabled
    if not _auto_cleanup_enabled:
        _auto_cleanup_enabled = True
        atexit.register(_cleanup_pressreader_sessions)
        print("✓ Auto-cleanup de sesiones habilitado")


def disable_auto_cleanup():
    """
    Deshabilita el cierre automático de sesiones.
    """
    global _auto_cleanup_enabled
    _auto_cleanup_enabled = False
    print("✓ Auto-cleanup de sesiones deshabilitado")


def get_pressreader_token() -> str:
    """
    Obtiene el Bearer token de PressReader haciendo login con las credenciales.
    El token se cachea para evitar múltiples logins en la misma sesión.

    El flujo de autenticación de PressReader es:
    1. Obtener token anónimo desde proceso.pressreader.com/authentication/v1/initialize
    2. Hacer signin con credenciales usando el token anónimo
    3. Completar el signin para obtener el bearerToken final

    Requiere en settings (via .env):
    - PRESSREADER_USER
    - PRESSREADER_PASS

    Returns:
        str: Bearer token para usar en headers de autorización
    """
    # Verificar cache (token válido por 1 hora)
    if _pressreader_token_cache.get("token"):
        cache_time = _pressreader_token_cache.get("time", 0)
        if time.time() - cache_time < 3600:  # 1 hora
            return _pressreader_token_cache["token"]

    user = getattr(settings, "PRESSREADER_USER", None)
    password = getattr(settings, "PRESSREADER_PASS", None)

    if not user or not password:
        raise ValueError(
            "PRESSREADER_USER y PRESSREADER_PASS deben estar configurados en .env"
        )

    session = requests.Session()
    base_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Accept": "*/*",
        "Accept-Language": "es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://proceso.pressreader.com",
        "Referer": "https://proceso.pressreader.com/proceso",
    }

    # Paso 1: Visitar la página para obtener cookies y ticket
    try:
        init_response = session.get(
            "https://proceso.pressreader.com/proceso", headers=base_headers, timeout=30
        )
        # Extraer el ticket de la cookie AProfile
        aprof_cookie = session.cookies.get("AProfile")
        if not aprof_cookie:
            raise ValueError("No se obtuvo cookie AProfile")

        ticket = aprof_cookie
    except Exception as e:
        raise ValueError(f"Error al acceder a proceso.pressreader.com: {e}")

    # Paso 2: Inicializar sesión y obtener token anónimo
    init_url = "https://proceso.pressreader.com/authentication/v1/initialize"
    init_body = {
        "tickets": [ticket],
        "language": "es-mx",
        "urlReferrer": "https://proceso.pressreader.com/",
        "url": "https://proceso.pressreader.com/proceso",
    }

    try:
        init_auth_response = session.post(
            init_url,
            headers={**base_headers, "Content-Type": "application/json"},
            json=init_body,
            timeout=30,
        )
        if init_auth_response.status_code == 200:
            init_data = init_auth_response.json()
            anon_token = init_data.get("bearerToken")
        else:
            anon_token = None
    except Exception as e:
        raise ValueError(f"Error al inicializar sesión: {e}")

    if not anon_token:
        raise ValueError("No se pudo obtener token anónimo de PressReader")

    # Paso 3: Hacer signin con las credenciales
    signin_url = "https://ingress.pressreader.com/services/auth/Signin"
    signin_headers = {
        **base_headers,
        "Authorization": f"Bearer {anon_token}",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }
    signin_body = urllib.parse.urlencode(
        {
            "userName": user,
            "password": password,
            "reCaptchaVersion": "3",
            "reCaptchaToken": "",
            "forceSignOut": "true",  # Forzar cierre de sesiones previas
        }
    )

    try:
        signin_response = session.post(
            signin_url, headers=signin_headers, data=signin_body, timeout=30
        )
    except Exception as e:
        raise ValueError(f"Error en signin de PressReader: {e}")

    if signin_response.status_code != 200:
        raise ValueError(
            f"Error en signin: {signin_response.status_code} - {signin_response.text[:200]}"
        )

    signin_data = signin_response.json()
    status_code = signin_data.get("Status")

    # Interpretar códigos de status de PressReader
    if status_code == 2:
        raise ValueError(
            "PressReader Status 2: Has excedido el número de sesiones simultáneas. "
            "Ejecuta 'python close_pressreader_sessions.py' para cerrar sesiones antiguas."
        )
    elif status_code != 0 and status_code is not None:
        raise ValueError(f"PressReader Status {status_code}: {signin_data}")

    sign_in_token = signin_data.get("Token") or signin_data.get("signInToken")
    tickets = signin_data.get("tickets", [])

    if not sign_in_token:
        raise ValueError(f"No se obtuvo Token: {signin_data}")

    # Paso 4: Completar el signin para obtener el bearerToken final
    complete_url = "https://proceso.pressreader.com/authentication/v1/signIn"
    complete_headers = {
        **base_headers,
        "Content-Type": "application/json",
    }
    complete_body = {
        "signInToken": sign_in_token,
        "tickets": tickets,
        "language": "es-mx",
        "enableAutoLogin": True,
    }

    try:
        complete_response = session.post(
            complete_url, headers=complete_headers, json=complete_body, timeout=30
        )
    except Exception as e:
        raise ValueError(f"Error al completar signin: {e}")

    if complete_response.status_code != 200:
        raise ValueError(
            f"Error al completar signin: {complete_response.status_code} - {complete_response.text[:200]}"
        )

    complete_data = complete_response.json()
    bearer_token = complete_data.get("bearerToken")

    if not bearer_token:
        raise ValueError(f"No se obtuvo bearerToken: {complete_data}")

    # Guardar en cache
    _pressreader_token_cache["token"] = bearer_token
    _pressreader_token_cache["time"] = time.time()
    _pressreader_token_cache["session"] = (
        session  # Guardar sesión para poder cerrarla después
    )

    # Agregar al historial de tokens usados
    if bearer_token not in _pressreader_token_history:
        _pressreader_token_history.append(bearer_token)

    # Habilitar auto-cleanup si no está ya habilitado
    if not _auto_cleanup_enabled:
        enable_auto_cleanup()

    return bearer_token


def signout_with_token(token: str) -> bool:
    """
    Cierra una sesión específica usando un Bearer token conocido.

    Args:
        token: Bearer token de la sesión a cerrar

    Returns:
        bool: True si se cerró exitosamente, False si falló
    """
    base_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Accept": "*/*",
        "Accept-Language": "es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://proceso.pressreader.com",
        "Referer": "https://proceso.pressreader.com/proceso",
    }

    signout_url = "https://ingress.pressreader.com/services/auth/SignOut"

    try:
        response = requests.post(
            signout_url,
            headers={
                **base_headers,
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={},
            timeout=30,
        )

        if response.status_code == 200:
            print(f"  ✓ Sesión cerrada: {token[:40]}...")
            return True
        else:
            print(f"  ✗ Error {response.status_code} para token: {token[:40]}...")
            return False

    except Exception as e:
        print(f"  ✗ Excepción al cerrar token {token[:40]}...: {e}")
        return False


def close_all_pressreader_sessions() -> int:
    """
    Cierra todas las sesiones conocidas usando los tokens del historial.

    Returns:
        int: Número de sesiones cerradas exitosamente
    """
    all_tokens = list(_pressreader_token_history)

    if not all_tokens:
        print("No hay tokens en el historial")
        return 0

    print(f"Intentando cerrar {len(all_tokens)} sesiones conocidas...")
    closed_count = 0

    for token in all_tokens:
        if signout_with_token(token):
            closed_count += 1

    # Limpiar el historial de tokens cerrados
    _pressreader_token_history.clear()
    _pressreader_token_cache.clear()

    return closed_count


def get_pressreader_headers(bearer_token: str) -> dict:
    """
    Construye los headers estándar para las peticiones a PressReader API.

    Args:
        bearer_token: Token de autenticación de PressReader

    Returns:
        Dict con headers de autorización y user-agent
    """
    return {
        "Authorization": f"Bearer {bearer_token}",
        "User-Agent": "Mozilla/5.0",
    }


# SCRAPER DE PROCESO


class ProcesoManagerScraper(ManagerScraper):
    """
    IMPORTANTE: Para evitar el error status dos (demasiadas sesiones)
    Este scraper habilita automáticamente el cierre de sesiones
    de PressReader al finalizar. Las sesiones se cerrarán automáticamente
    cuando el programa termine, incluso si hay errores o interrupciones.
    """

    date_format = "%Y%m%d"

    def __init__(
        self,
        from_date: str | date | None,
        to_date: str | date | None,
        recover_record: ScrapedRecord | None = None,
    ) -> None:
        # Habilitar auto-cleanup de sesiones de PressReader
        enable_auto_cleanup()

        super().__init__(
            from_date,
            to_date,
            ProcesoMainScraper,
            ProcesoArticleScraper,
            recover_record=recover_record,
        )

    def get_source(self) -> Source:
        if not hasattr(self, "source") or not self.source:
            self.source, _ = Source.objects.get_or_create(
                main_url="https://www.proceso.com.mx",
                defaults={"name": "Proceso", "is_news": True},
            )
        return self.source

    def scrape_sections(self):
        """
        Override para consultar el calendario y obtener solo las fechas con issues disponibles.
        """
        from source.scraper.articles import date_in_date

        self.scraped_record.set_status("get_sections")

        from_date = date_in_date(self.scraped_record.from_date)
        to_date = date_in_date(self.scraped_record.to_date)

        # Obtener token para consultar el calendario
        bearer_token = get_pressreader_token()

        # Consultar calendario para obtener fechas reales con issues
        str_dates = self.get_available_issues(from_date, to_date, bearer_token)

        if not str_dates:
            print(f"No se encontraron issues disponibles entre {from_date} y {to_date}")
            self.scraped_record.data = {}
            self.scraped_record.save()
            return

        print(f"Encontrados {len(str_dates)} issues: {str_dates}")

        articles_by_date = {}

        for date_ in str_dates:
            try:
                sections_dict = self.main_scraper_class(date_).sections_dict
            except Exception as e:
                sections_dict = {
                    "error": f"Error getting sections for date {date_}",
                    "exception": str(e),
                }
            articles_by_date[date_] = sections_dict

        self.scraped_record.data = articles_by_date
        self.scraped_record.save()

    # Si recibimos más de un día, necesitamos revisar si hay issues disponibles para cada día
    def get_available_issues(
        self, from_date: date, to_date: date, bearer_token: str
    ) -> List[str]:
        """
        Consulta el calendario de PressReader para obtener las fechas que realmente tienen issues.

        Args:
            from_date: Fecha inicial del rango
            to_date: Fecha final del rango
            bearer_token: Token de autenticación de PressReader

        Returns:
            Lista de fechas en formato YYYYMMDD que tienen issues disponibles
        """
        headers = get_pressreader_headers(bearer_token)

        # El endpoint del calendario no usa /se2skyservices
        calendar_url = (
            f"https://ingress.pressreader.com/services/calendar/get?cid={PROCESO_CID}"
        )

        try:
            calendar_response = get_json_content(calendar_url, custom_headers=headers)
        except Exception as e:
            print(f"Error al obtener calendario: {e}")
            return []

        available_dates = []

        # El calendario tiene formato: {"Years": {"2025": {"12": {"1": {...}}}}}
        years = calendar_response.get("Years", {})

        for year_str, months in years.items():
            year = int(year_str)

            # Filtrar por rango de fechas
            if year < from_date.year or year > to_date.year:
                continue

            for month_str, days in months.items():
                month = int(month_str)

                for day_str in days.keys():
                    day = int(day_str)

                    # Crear fecha y verificar que esté en el rango
                    issue_date = date(year, month, day)

                    # Convertir from_date y to_date a date si son datetime
                    from_date_cmp = (
                        from_date.date() if hasattr(from_date, "date") else from_date
                    )
                    to_date_cmp = (
                        to_date.date() if hasattr(to_date, "date") else to_date
                    )

                    if from_date_cmp <= issue_date <= to_date_cmp:
                        # Formato YYYYMMDD
                        available_dates.append(issue_date.strftime("%Y%m%d"))

        return sorted(available_dates)


class ProcesoMainScraper(MainScraper):
    parser = "json"  # We don't use Beautiful Soup
    need_proxy = False

    # Atributos específicos de PressReader
    bearer_token: str
    issue_id: str | None
    cid: str = PROCESO_CID

    def __init__(self, scraper_date: date | str):
        """
        Inicializa el scraper para una fecha específica.
        No llamamos a super().__init__() porque usamos API JSON en lugar de HTML.

        Args:
            scraper_date: Fecha en formato YYYYMMDD o date object
        """
        # Convertir fecha al formato esperado (NO llamar a super para evitar get_content HTML)
        from source.scraper.scraper_base import date_in_str

        if isinstance(scraper_date, date):
            self.scraper_date = scraper_date.strftime("%Y%m%d")
        else:
            # Limpiar formato - puede venir como YYYY/MM/DD o YYYYMMDD
            self.scraper_date = scraper_date.replace("/", "")

        # Obtener token antes de hacer peticiones
        self.bearer_token = get_pressreader_token()
        self.issue_id = None
        self.sections_dict = {}

        # Obtener estructura del issue desde la API JSON
        self.get_sections()
        self.get_articles()

    def main_url(self) -> str:
        """URL para obtener información del issue."""
        return (
            f"{PRESSREADER_API_BASE}/IssueInfo/GetIssueInfoByCid"
            f"?cid={self.cid}&issueDate={self.scraper_date}"
        )

    def get_headers(self) -> dict:
        """Headers con autenticación para la API."""
        return get_pressreader_headers(self.bearer_token)

    def get_sections(self):
        """
        Obtiene la estructura del issue desde PressReader.
        Las "secciones" en Proceso son las páginas de la revista.
        """
        headers = self.get_headers()

        # Paso 1: Obtener información del issue
        try:
            issue_response = get_json_content(self.main_url(), custom_headers=headers)
        except Exception as e:
            self.sections_dict = {"error": f"Error al obtener issue: {str(e)}"}
            return

        if not issue_response or "Issue" not in issue_response:
            self.sections_dict = {
                "error": f"No se encontró issue para la fecha {self.scraper_date}"
            }
            return

        self.issue_id = issue_response["Issue"].get("Issue")

        if not self.issue_id:
            self.sections_dict = {"error": "No se pudo obtener el ID del issue"}
            return

        # Paso 2: Obtener metadata de páginas
        pages_url = f"{PRESSREADER_API_BASE}/pagesMetadata/?issue={self.issue_id}"

        try:
            pages_response = get_json_content(pages_url, custom_headers=headers)
        except Exception as e:
            self.sections_dict = {"error": f"Error al obtener páginas: {str(e)}"}
            return

        # Paso 3: Organizar por páginas (secciones)
        self.sections_dict = {}

        # La API retorna una lista directamente, no un dict con "Pages"
        pages_list = pages_response if isinstance(pages_response, list) else []

        for page in pages_list:
            page_number = page.get("PageNumber", 0)
            page_title = f"Página {page_number}"

            # Extraer IDs de artículos de esta página
            article_ids = []
            for article_meta in page.get("Articles", []):
                article_id = article_meta.get("ArticleId")
                if article_id:
                    article_ids.append(
                        {
                            "uid": str(article_id),
                            "title": article_meta.get("Title", ""),
                            "metadata": {
                                "article_id": str(article_id),
                                "page_number": page_number,
                                "issue_id": self.issue_id,
                            },
                        }
                    )

            if article_ids:
                self.sections_dict[page_title] = {
                    "page_number": page_number,
                    "issue_id": self.issue_id,
                    "articles": article_ids,
                }

    def get_articles(self):
        """
        Obtiene el contenido completo de los artículos desde la API.
        """
        if not self.issue_id:
            print("  ⚠ No hay issue_id, saltando get_articles")
            return

        headers = self.get_headers()
        print(f"  Obteniendo contenido de artículos para issue {self.issue_id}")

        for section_name, section_data in self.sections_dict.items():
            if "articles" not in section_data:
                continue

            article_ids = [art["uid"] for art in section_data["articles"]]

            if not article_ids:
                continue

            print(f"    Sección '{section_name}': {len(article_ids)} artículos")

            # La API tiene un límite de artículos por request, procesar en lotes
            batch_size = 50
            for i in range(0, len(article_ids), batch_size):
                batch_ids = article_ids[i : i + batch_size]

                # Construir URL con múltiples IDs
                # formato correcto: articles=id1%2Cid2%2Cid3 (IDs separados por %2C que es comma URL-encoded)
                articles_ids_str = "%2C".join(batch_ids)
                articles_url = f"https://ingress.pressreader.com/services/articles/GetItems?comment=LatestByAll&viewType=text&articles={articles_ids_str}&IsHyphenated=true&options=1"

                # Debug: mostrar la primera URL y los IDs
                if i == 0:
                    print(f"      URL (primeros 200 chars): {articles_url[:200]}")
                    print(f"      IDs enviados: {batch_ids[:3]}...")

                try:
                    articles_response = get_json_content(
                        articles_url, custom_headers=headers
                    )
                    # La API puede retornar "Items" o "Articles"
                    items_count = len(
                        articles_response.get("Items")
                        or articles_response.get("Articles", [])
                    )
                    print(
                        f"      Batch {i // batch_size + 1}: {items_count} artículos obtenidos"
                    )

                    # Debug: mostrar respuesta si está vacía
                    if items_count == 0 and i == 0:
                        print(
                            f"      ⚠ Respuesta vacía. Keys: {list(articles_response.keys())}"
                        )
                        if "Items" in articles_response:
                            print(f"         Items es: {articles_response['Items']}")
                        if "Articles" in articles_response:
                            articles_list = articles_response["Articles"]
                            print(
                                f"         Articles count: {len(articles_list) if isinstance(articles_list, list) else 'not a list'}"
                            )
                        if "Pages" in articles_response:
                            pages_list = articles_response["Pages"]
                            print(
                                f"         Pages count: {len(pages_list) if isinstance(pages_list, list) else 'not a list'}"
                            )
                except Exception as e:
                    print(f"      ✗ Error en batch: {str(e)[:100]}")
                    section_data["error"] = str(e)
                    continue

                self._process_articles_response(articles_response, section_data)

        # Actualizar UIDs al final para que sean únicos globalmente (formato: YYYYMMDD/articleid)
        total_with_url = 0
        total_articles = 0
        for section_name, section_data in self.sections_dict.items():
            if "articles" in section_data:
                for article in section_data["articles"]:
                    total_articles += 1
                    if article.get("url"):
                        total_with_url += 1
                    # Solo agregar prefijo si no lo tiene ya
                    if "/" not in article["uid"]:
                        article["uid"] = f"{self.scraper_date}/{article['uid']}"

        print(
            f"  ✓ Total: {total_articles} artículos, {total_with_url} con URL completa"
        )

    def _process_articles_response(self, articles_response: dict, section_data: dict):
        """Procesa la respuesta de la API de artículos y actualiza section_data."""

        # Mapear respuesta a los artículos
        # La API puede retornar "Items" o "Articles" dependiendo del endpoint
        articles_data = articles_response.get("Items") or articles_response.get(
            "Articles", []
        )
        matched = 0

        # Debug: ver estructura de la respuesta
        if articles_data and len(articles_data) > 0:
            first_article = articles_data[0]
            print(
                f"      Debug: Primer artículo de API - Keys: {list(first_article.keys())}"
            )
            print(
                f"      Debug: Id={first_article.get('Id')}, BookmarkId={first_article.get('BookmarkId')}"
            )
            print(f"      Debug: ¿Tiene Blocks? {bool(first_article.get('Blocks'))}")
            if first_article.get("Blocks"):
                print(
                    f"      Debug: Blocks count: {len(first_article.get('Blocks', []))}"
                )

        # Debug: mostrar UIDs locales para comparar
        if "articles" in section_data:
            local_uids = [art["uid"].split("/")[-1] for art in section_data["articles"]]
            print(f"      Debug: UIDs locales en section: {local_uids[:3]}...")

        for api_article in articles_data:
            # La API retorna Id como número, convertir a string para comparar
            article_id = str(api_article.get("Id", ""))

            # Debug: ver IDs que intentamos matchear
            if not article_id:
                print(f"      ⚠ Artículo sin ID en respuesta API")
                continue

            # Buscar el artículo en nuestra lista (uid puede tener o no el prefijo de fecha)
            for article in section_data["articles"]:
                # Extraer el ID sin el prefijo de fecha si existe
                article_uid = article["uid"].split("/")[-1]

                if article_uid == article_id:
                    matched += 1
                    # Actualizar con datos completos
                    article["title"] = api_article.get("Title") or article["title"]
                    article["subtitle"] = api_article.get("Subhead", "")

                    # El contenido está en Blocks, no en Text
                    blocks = api_article.get("Blocks", [])
                    text_content = ""
                    if blocks:
                        for block in blocks:
                            block_text = block.get("Text", "")
                            if block_text:
                                text_content += block_text + "\n\n"
                    article["content"] = text_content.strip()

                    article["url"] = self._build_article_url(article_id)

                    # Guardar datos completos de la API en metadata
                    article["metadata"]["api_data"] = {
                        "Title": api_article.get("Title"),
                        "Subhead": api_article.get("Subhead"),
                        "Byline": api_article.get("Byline"),
                        "Bylines": api_article.get("Bylines"),
                        "Page": api_article.get("Page"),
                        "Blocks": blocks[:2]
                        if blocks
                        else [],  # Guardar solo los primeros 2 bloques como muestra
                    }

                    # Extraer imágenes si las hay
                    article["images"] = []
                    if api_article.get("ImageUrl"):
                        article["images"].append(
                            {
                                "src": api_article.get("ImageUrl"),
                                "caption": api_article.get("ImageCaption", ""),
                            }
                        )

                    break

        if matched < len(articles_data):
            print(
                f"        ⚠ Solo se emparejaron {matched} de {len(articles_data)} artículos de la API"
            )

    def _build_article_url(self, article_id: str) -> str:
        """Construye URL de acceso al artículo en PressReader."""
        return (
            f"https://www.pressreader.com/mexico/proceso/{self.issue_id}/{article_id}"
        )


class ProcesoArticleScraper(ArticleScraper):
    """
    Scraper de artículos individuales de Proceso.
    Como los datos ya vienen de la API, principalmente formatea el contenido.
    """

    need_proxy = False
    parser = "json"  # We don't use Beautiful Soup

    def get_article_data(self):
        """
        Extrae datos del artículo.
        La mayoría ya viene en metadata.api_data de la API de PressReader.
        """
        api_data = {}
        if self.article.metadata:
            api_data = self.article.metadata.get("api_data", {})

        self.title = api_data.get("Title") or self.article.title or ""
        self.subtitle = api_data.get("Subhead") or self.article.subtitle
        self.author = api_data.get("Author") or api_data.get("Byline")
        self.content = self.article.basic_content or ""

        # Debug
        print(f"    [{self.article.uid}] Content length: {len(self.content)}")
        if not self.content:
            print(f"      ⚠ Sin contenido. api_data keys: {list(api_data.keys())}")

        # Imágenes ya vienen procesadas
        self.images = self.article.images or []

    def get_main_body(self):
        """
        No usamos HTML para Proceso, retornamos None.
        El contenido de texto plano ya está en self.content.
        """
        return None

    def special_cleanup(self, body):
        """
        No necesitamos limpieza HTML para Proceso.
        """
        return body


# URLs de referencia de la API de PressReader (documentación)
# Estas constantes documentan el flujo de la API
_API_DOCS = {
    "get_cid": f"{PRESSREADER_API_BASE}/catalog/v1/routes/publication?publication=proceso",
    "get_issue": f"{PRESSREADER_API_BASE}/IssueInfo/GetIssueInfoByCid?cid=24em&issueDate=YYYYMMDD",
    "get_pages": f"{PRESSREADER_API_BASE}/pagesMetadata/?issue={{issue_id}}",
    "get_articles": f"{PRESSREADER_API_BASE}/Articles/GetItems?articles[]={{article_id}}",
    "get_page_keys": f"{PRESSREADER_API_BASE}/IssueInfo/GetPageKeys?issue={{issue_id}}&pageNumber=0&preview=true",
    "get_image": "https://i.prcdn.co/img?file={{issue_id}}&page={{page}}&scale=300&ticket={{ticket}}",
}
