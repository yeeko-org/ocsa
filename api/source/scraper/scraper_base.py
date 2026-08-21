import re
import threading
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Any, Dict, List

import requests
from curl_cffi import requests as cffi_requests
from curl_cffi.requests.exceptions import ProxyError
from bs4 import BeautifulSoup
from bs4.element import PageElement, Tag
from django.conf import settings

from source.models import Article

REQUESTS_DEFAULT_HEADERS = {"User-Agent": "Mozilla/4.0"}

# Intentos por URL y punto en el que se renueva la sesión. Ver get_content.
MAX_ATTEMPTS = 6
RENEW_AT = 3


def get_json_content(
    url: str,
    with_proxy: bool = False,
    attempts: int = 1,
    custom_headers: dict | None = None,
) -> dict:
    """
    Hace requests a APIs JSON con headers personalizados.

    Args:
        url: URL de la API
        with_proxy: Si usar proxy
        attempts: Número de intento actual (para reintentos)
        custom_headers: Headers personalizados (ej: Bearer token)

    Returns:
        dict: Respuesta JSON parseada
    """
    import time

    headers = custom_headers or REQUESTS_DEFAULT_HEADERS
    proxy_key = settings.PROXY_KEY

    if with_proxy and proxy_key:
        proxies = {
            "http": f"http://{proxy_key}",
            "https": f"https://{proxy_key}",
        }
        response = requests.get(url, headers=headers, proxies=proxies)
    else:
        response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        if attempts <= 3:
            print(
                f"Intento {attempts} fallido para {url}. "
                f"Status: {response.status_code}"
            )
            time.sleep(2**attempts)
            return get_json_content(url, with_proxy, attempts + 1, custom_headers)
        else:
            raise Exception(
                f"Error al acceder a la API: {response.status_code} "
                f"- {response.text[:200]}"
            )


class ScraperSession:
    """
    Sesión HTTP con cookies persistentes.

    Cloudflare no evalúa peticiones sueltas sino sesiones: al primer
    acceso emite una cookie `cf_clearance` ligada al par (IP,
    fingerprint TLS) y a partir de ahí deja pasar el resto del dominio.
    Sin cookies compartidas cada URL vuelve a caer en el challenge, y
    desde una IP de proxy —con reputación de sobra para ser sospechosa—
    eso significa 403 permanente.
    """

    def __init__(
            self, with_proxy: bool = False, warmup_url: str | None = None
    ) -> None:
        self.with_proxy = with_proxy
        self.warmup_url = warmup_url
        self.last_url: str | None = None
        self._session = self._build_session()
        self._warmup()

    def _build_session(self) -> cffi_requests.Session:
        proxies = None
        if self.with_proxy and settings.PROXY_KEY:
            # El valor lleva esquema http:// aunque el destino sea HTTPS:
            # al proxy se llega por HTTP y de ahí abre el túnel CONNECT.
            proxies = {"https": f"http://{settings.PROXY_KEY}"}
        # impersonate="chrome" replica el handshake TLS de un Chrome real.
        return cffi_requests.Session(impersonate="chrome", proxies=proxies)

    def _warmup(self) -> None:
        """Paga el challenge una sola vez para todo el dominio."""
        if not self.warmup_url:
            return
        try:
            self.get(self.warmup_url)
        except Exception as exc:
            print(f"Warmup fallido para {self.warmup_url}: {exc}")

    def renew(self) -> None:
        """Descarta la sesión quemada; al reconectar el proxy asigna otra IP."""
        try:
            self._session.close()
        except Exception:
            pass
        self.last_url = None
        self._session = self._build_session()
        self._warmup()

    def request(
            self, url: str, method: str = "get",
            referer: str | None = None, timeout: int = 40,
            json: dict | None = None,
    ):
        headers = {}
        # Encadenar el Referer imita la navegación real: sin él, Cloudflare
        # trata cada sección como una entrada directa y la vuelve a retar.
        actual_referer = referer or self.last_url
        if actual_referer:
            headers["Referer"] = actual_referer
        response = self._session.request(
            method.upper(), url, headers=headers or None, timeout=timeout,
            json=json)
        if response.status_code == 200:
            self.last_url = url
        return response

    def get(self, url: str, referer: str | None = None, timeout: int = 40):
        return self.request(url, referer=referer, timeout=timeout)


_thread_local = threading.local()


def get_thread_session(with_proxy: bool = False) -> ScraperSession:
    """
    Sesión de respaldo para llamadores que no gestionan la suya. Cada lote
    de scraping corre en su propio hilo, así que equivale a una por lote.
    """
    key = f"session_proxy_{int(with_proxy)}"
    session = getattr(_thread_local, key, None)
    if session is None:
        session = ScraperSession(with_proxy=with_proxy)
        setattr(_thread_local, key, session)
    return session


def fetch(
    url: str,
    with_proxy: bool = False,
    session: ScraperSession | None = None,
    referer: str | None = None,
    method: str = "get",
    json: dict | None = None,
    timeout: int = 40,
):
    """Petición reintentada sobre una ScraperSession; devuelve la respuesta.

    Agotados los intentos entrega la última respuesta fallida: quien llama
    decide si eso es un error o una ausencia legítima de contenido.
    """
    sess = session or get_thread_session(with_proxy)
    response = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = sess.request(
                url, method=method, referer=referer, json=json,
                timeout=timeout)
        except ProxyError as exc:
            raise Exception(
                f"Error de proxy al acceder a {url}: {exc}") from exc
        if response.status_code == 200:
            return response
        # Se reintenta de inmediato, sin backoff: el 403 es un challenge que
        # se resuelve al segundo intento dentro de la misma sesión, no un
        # rate limit que se cure esperando. Agotada la mitad de los intentos
        # damos la IP por quemada y renovamos.
        if attempt == RENEW_AT:
            print(f"Sesión quemada en {url}, renovando IP.")
            sess.renew()

    return response


def get_content(
    url: str,
    parser: str = "html.parser",
    with_proxy: bool = False,
    session: ScraperSession | None = None,
    referer: str | None = None,
) -> BeautifulSoup:
    response = fetch(
        url, with_proxy=with_proxy, session=session, referer=referer)
    if response is None or response.status_code != 200:
        status = response.status_code if response is not None else None
        raise Exception(f"Error al acceder a la página: {status}")
    return BeautifulSoup(response.text, parser)


def get_clean_text(elem: PageElement) -> str:
    """
    Obtiene el texto limpio de un Tag de BeautifulSoup, eliminando espacios
    adicionales y saltos de línea.
    """
    text = elem.get_text(separator=" ")
    text = re.sub(r"\n+", " ", text)  # Reemplaza saltos de línea por espacio
    return re.sub(r"\s+", " ", text).strip()


class MainScraper(ABC):
    """
    diccionario esperado:
    {
        "section_name": {
            "url": "url_section",
            "articles": [
                {
                    "uid": "uid",
                    "title": "title",
                    "url": "url",
                    "imgs": "imgs",
                    "content": "content",
                    "metadata": {}
                }
            ]
        }
    }
    """

    soup_content: BeautifulSoup
    sections_dict: Dict[str, dict]
    scraper_date: str
    session: "ScraperSession | None"
    parser = "html.parser"
    need_proxy = False
    date_format = "%Y/%m/%d"

    def __init__(
            self, scraper_date: date | str,
            session: "ScraperSession | None" = None):
        self.scraper_date = self.date_in_str(scraper_date)
        self.session = session

        self.get_sections()
        self.get_articles()

    def date_in_str(self, date_: date | str) -> str:
        if isinstance(date_, date):
            return date_.strftime(self.date_format)

        pattern = r"^\d{4}/\d{2}/\d{2}$"
        pattern2 = r"^\d{4}\d{2}\d{2}$"
        if not re.match(pattern, date_) and not re.match(pattern2, date_):
            raise ValueError("Invalid date format. Must be YYYY/MM/DD or YYYYMMDD")
        elif re.match(pattern2, date_):
            date_ = datetime.strptime(date_, "%Y%m%d").strftime(self.date_format)

        return date_

    @abstractmethod
    def main_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_sections(self):
        raise NotImplementedError

    @abstractmethod
    def get_articles(self):
        raise NotImplementedError


class ArticleScraper(ABC):
    article: Article
    soup_content: BeautifulSoup
    session: "ScraperSession | None"

    title: str
    subtitle: str | None
    author: str | None
    content: str
    images: List[dict[str, Any]] | None
    ai_engine: str | None
    pages: str | None = None
    parser = "html.parser"
    need_proxy: bool = False
    paragraphs: List[str] = []

    def __init__(
            self, article: Article, update: bool = False,
            session: "ScraperSession | None" = None):
        self.article = article
        self.session = session
        if article.html_content and not update:
            self.soup_content = BeautifulSoup(article.html_content, self.parser)
            self.get_article_data()
            return
        if self.parser != "json":
            self.soup_content = get_content(
                self.article.url, self.parser, self.need_proxy,
                session=session)
        try:
            self.get_article_data()
        except Exception as e:
            print(f"Error getting article data: {e}")
            return

        article.title = self.title or article.title
        article.subtitle = self.subtitle or article.subtitle
        article.author = self.author or article.author
        article.content = self.content or article.content
        article.paragraphs = self.get_paragraphs(article.content)
        article.pages = self.pages or article.pages  # type: ignore
        # article.paragraps = self.content.split("\n") if self.content else []
        article.html_content = str(self.get_main_body()) or article.html_content
        article.images = self.images or article.images  # type: ignore

    @abstractmethod
    def get_article_data(self):
        raise NotImplementedError

    @abstractmethod
    def get_main_body(self) -> Tag:
        raise NotImplementedError

    @abstractmethod
    def special_cleanup(self, body: Tag) -> Tag:
        raise NotImplementedError

    def get_paragraphs(self, content: str | None = None) -> List[str]:
        if not content:
            return []

        paragraphs = re.split(r"\n{2,}", content)
        final_paragraphs = []
        for paragraph in paragraphs:
            single_line = paragraph.replace("\n", " ").strip()
            if paragraph:
                final_paragraphs.append(single_line)
        return final_paragraphs

    def get_reduced_content_text(self):
        body = self.get_main_body()
        title = self.title
        # print("Body1:", body)
        # if title not in body.get_text():
        #     title = None

        excluded_tags = [
            "script",
            "style",
            "noscript",
            "svg",
            "button",
            "input",
            "textarea",
            "select",
            "option",
            "form",
            "fieldset",
            "canvas",
            "nav",
            "aside",
            "address",
            "map",
            "area",
            "legend",
            "iframe",
            "embed",
            "object",
            "param",
            "video",
            "audio",
        ]
        for excluded_tag in excluded_tags:
            for tag in body.find_all(excluded_tag):
                tag.decompose()
        main_tags = [
            "p",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "li",
            "ul",
            "div",
            "span",
            "article",
            "section",
            "header",
            "footer",
            "img",
            "video",
            "figure",
            "figcaption",
            "blockquote",
            "table",
            "tr",
            "td",
            "th",
            "ol",
            "dl",
            "dt",
            "ddem",
            "strong",
            "b",
            "i",
            "a",
            "br",
        ]
        begin_title = not bool(title)
        for tag in body.find_all():
            tag_text = tag.get_text(strip=True)
            # print(f"Tag: {tag.name}, Text: {tag_text}")
            if not tag_text and tag.name not in main_tags:
                tag.decompose()
            if not begin_title:
                direct_text = tag.string
                if direct_text and title in direct_text:
                    begin_title = True
            if not begin_title:
                if title in tag_text:
                    tag.decompose()

        # body = self.special_cleanup(body)

        allowed_attrs = ["class", "id", "href", "src", "alt", "title"]
        # new_body = BeautifulSoup('', 'html.parser')
        for tag in body.find_all():
            relevant_attrs = {
                key: value for key, value in tag.attrs.items() if key in allowed_attrs
            }
            tag.attrs = relevant_attrs
        try:
            # body_encoding = body.encode("utf-8")
            self.article.html_content = (
                body.prettify().encode("utf-8", errors="ignore").decode("utf-8")
            )
            # print("Body4:", self.htmml_content)
        except Exception as e:
            print("Error body.pretty:", e)
            print("-" * 50)
            print("Body5:", body)
            raise e
        # new_html = body.prettify()
        # self.article.content = body.get_text(separator="\n")
        # self.article.paragraphs = self.get_paragraphs(self.article.content)
        self.article.save()
