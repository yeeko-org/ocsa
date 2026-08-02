import json
import re

from django.conf import settings
from google import genai
from google.genai import types
from google.genai.errors import ClientError

api_key_name = "GEMINI_API_KEY"
api_key = getattr(settings, api_key_name, None)

# El SDK no trae protección activa: `HttpOptions.timeout=None` llega literal
# a httpx (espera indefinida, un stall tumba el lote entero) y
# `retry_options=None` se traduce a `stop_after_attempt(1)`.
# El 429 se excluye a propósito de los códigos reintentables: nuestros 429
# son cuota diaria agotada, que no se cura esperando; reintentarlos solo
# multiplica el tiempo perdido.
HTTP_OPTIONS = types.HttpOptions(
    timeout=40_000,
    retry_options=types.HttpRetryOptions(
        attempts=3, http_status_codes=[500, 502, 503, 504]),
)

# Piso del TTL del caché: el TTL se calcula por tamaño de lote, así que un
# lote chico quedaba con menos margen del que consume un solo stall.
MIN_CACHE_SECONDS = 300

CACHE_LOST_MSG = "CachedContent not found"

# Crear caché cobra tokens de escritura: con pocos artículos por delante sale
# más barato mandar el system_instruction inline en cada llamada.
MIN_PENDING_FOR_CACHE = 10

# Cinco fallos seguidos con la misma causa ya no son un accidente. Corta los
# lotes condenados (cuota agotada) antes de que generen miles de errores.
MAX_FAILED_STREAK = 5


class RequestGemini:
    client = genai.Client(api_key=api_key, http_options=HTTP_OPTIONS)

    def __init__(self, engine: str | None = None):

        self.engine = engine or settings.GEMINI_ENGINE
        self.messages: list[dict] = []
        self.base_messages: list[str] = []
        self.msgs = []
        self.errors = []
        self.system_msg = None
        self.response = None
        self.cache = None
        self.cache_name: str | None = None
        self.cache_seconds: int = MIN_CACHE_SECONDS
        self.cache_rebuilds: int = 0
        self.cache_disabled: bool = False
        self.cache_error: str | None = None
        self.last_error: str | None = None
        # Clave estable del último fallo (`RESOURCE_EXHAUSTED`, `UNAVAILABLE`);
        # el mensaje completo trae detalles variables y no sirve para agrupar.
        self.last_status: str | None = None
        self.cache_lost: bool = False

    def build_chat(self, prompt_path: str):
        with open(prompt_path, "r", encoding="utf-8") as file:
            init_prompt = file.read()
        self.msgs = init_prompt.split("\n====\n")
        self.system_msg = self.msgs[0]

        # for idx, msg in enumerate(self.msgs[1:]):
        #     role = "sections: " if idx % 2 == 0 else "JSON: "
        #     new_prompt = self.format_prompt(msg)
        #     new_prompt = f"{role}{new_prompt}"
        #     self.base_messages.append(new_prompt)

    def create_cache(
            self, name: str = 'criteria_v1_single', seconds: int = 300
    ) -> bool:
        """Crea el caché de contexto. Devuelve False si no se pudo.

        Sin caché el flujo sigue vivo: ``send_gemini_prompt`` manda el
        ``system_instruction`` en cada llamada. Cuesta más tokens, no rompe.
        """
        self.cache_name = name
        self.cache_seconds = max(seconds, MIN_CACHE_SECONDS)
        self.cache_error = None
        try:
            self.cache = self.client.caches.create(
                model=self.engine,
                config=types.CreateCachedContentConfig(
                    display_name=name,
                    system_instruction=self.system_msg,
                    ttl=f"{self.cache_seconds}s",
                )
            )
        except Exception as e:
            self.cache_error = f"Error creating cache '{name}': {e}"
            self.errors.append(self.cache_error)
            print(self.cache_error)
            self.cache = None
            return False
        return True

    def recreate_cache(self, max_rebuilds: int = 2) -> bool:
        """Rehace el caché expirado con los parámetros de la creación.

        El TTL es una caducidad absoluta desde la creación, así que un lote
        largo lo pierde a media corrida por más margen que se le dé. Al
        agotar los intentos deja ``cache=None`` y el lote termina inline.
        """
        if not self.cache_name or self.cache_rebuilds >= max_rebuilds:
            self.cache = None
            self.cache_disabled = True
            return False
        self.cache_rebuilds += 1
        return self.create_cache(self.cache_name, self.cache_seconds)

    def format_prompt(self, prompt):
        if not prompt:
            return None
        if isinstance(prompt, str):
            new_prompt = prompt.strip()
        elif isinstance(prompt, dict) or isinstance(prompt, list):
            new_prompt = json.dumps(prompt, ensure_ascii=False, indent=2)
        else:
            print(f"Unsupported prompt type: {type(prompt)}")
            return None
        return new_prompt

    def send_gemini_prompt(
            self, new_prompt:str, schema_clss=None, main_name='article'
    ):
        self.last_error = None
        self.last_status = None
        self.cache_lost = False
        new_prompt = self.format_prompt(new_prompt)
        cache_name = self.cache.name if self.cache else None
        if cache_name:
            system_instruction = None
        else:
            system_instruction = self.system_msg
        config = types.GenerateContentConfig(
            # thinking_config=types.ThinkingConfig(thinking_budget=0),
            thinking_config=types.ThinkingConfig(thinking_level='minimal'),
            system_instruction=system_instruction,
            # response_schema=schema_clss,
            response_json_schema=schema_clss.model_json_schema(),
            response_mime_type="application/json",
            cached_content=cache_name,
        )
        # content = f"{content}\nsections: {new_prompt}\nJSON:"
        content = f"{main_name}: {new_prompt}"
        try:
            response = self.client.models.generate_content(
                model=self.engine,
                contents=content,
                config=config,
            )
        except ClientError as e:
            self.last_error = f"{e.message} (ClientError - status {e.status})"
            self.last_status = str(e.status)
            self.cache_lost = CACHE_LOST_MSG in (e.message or "")
            self.errors.append(self.last_error)
            print(f"ClientError: {e.message}")
            return None
        except Exception as e:
            self.last_error = str(e)
            self.last_status = type(e).__name__
            self.errors.append(self.last_error)
            print(f"Error sending Gemini prompt: {e}")
            return None
        self.response = response
        # request_id = response.id
        return response.parsed
