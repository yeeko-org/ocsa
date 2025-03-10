import json
import re
import openai

from django.conf import settings
import tiktoken

TOKENS_MAX_LENGTH = getattr(settings, 'OPENAI_TOKENS_MAX_LENGTH', 128000)
MODEL_NAME = getattr(settings, 'OPENAI_ENGINE', 'gpt-4o-2024-11-20')


def format_prompt_text(text: str, has_pipe: bool = False):
    if has_pipe:
        new_text = text
        new_text = re.sub(r"\s{2,}", " ", new_text)
    else:
        new_text = text.replace("\n", "|")
        new_text = re.sub(r"\s{2,}", " ", new_text)
    new_text = new_text.replace("|", "\n")
    new_text = new_text.strip()
    return new_text


class JsonRequestOpenAI:
    first_example: str
    first_response: dict
    prompt: str
    use_deepseek: bool

    def __init__(
            self, prompt_path: str, to_json: bool = True,
            engine: str | None = None, use_deepseek: bool = False,
    ):
        openai_api_key = getattr(
            settings, "DEEPSEEK_API_KEY" if use_deepseek
            else "OPENAI_API_KEY", None)

        self.use_deepseek = use_deepseek

        self.client = openai.OpenAI(
            api_key=openai_api_key,
            base_url='https://api.deepseek.com/v1' if use_deepseek else None)

        self.engine = "deepseek-chat" if use_deepseek else (
            engine or MODEL_NAME)
        self.messages: list[dict] = []
        self.to_json = to_json
        self.response = None
        with open(prompt_path, "r", encoding="utf-8") as file:
            init_prompt = file.read()
        msgs = init_prompt.split("\n====\n")
        self.build_msg(msgs[0], "system")
        for idx, msg in enumerate(msgs[1:]):
            role = "user" if idx % 2 == 0 else "assistant"
            self.build_msg(msg, role)
        self.first_example = ""
        self.first_response = {}
        self.prompt = ""

    def send_prompt(self, new_prompt):
        if not new_prompt:
            return None, None
        self.build_msg(new_prompt, "user")
        response_format = {"type": "json_object"} \
            if self.to_json else None
        try:
            response = self.client.chat.completions.create(
                model=self.engine,
                response_format=response_format,  # type: ignore
                messages=self.messages,  # type: ignore
                temperature=0.6,
                max_tokens=8190 if self.use_deepseek else 16000,
                frequency_penalty=0,
                presence_penalty=0
            )
            self.response = response
        except Exception as e:
            print(f"messages: {self.messages}")
            print(f"OpenAI BadRequestError: {e}")
            raise e

        if self.to_json:
            json_response = response.choices[0].message.content
            if not json_response:
                return None, None
            try:
                return json.loads(json_response), response.id
            except Exception:
                return None, None
        else:
            return response.choices[0].message.content, response.id

    def build_msg(self, prompt, role="user"):

        if self.to_json and role == "assistant":
            try:
                prompt = json.dumps(json.loads(prompt), ensure_ascii=False)
            except Exception as e:
                print(f"Error converting to json: {e}")
                print("prompt:", prompt)
        if self.use_deepseek:
            content = prompt
        else:
            content = [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        self.messages.append({
            "role": role,
            "content": content
        })


def truncate_text(plain_text, limit=None):
    encoding = tiktoken.encoding_for_model(MODEL_NAME)
    tokens = encoding.encode(plain_text)
    token_count = len(tokens)

    tokens_max_length = int((limit or TOKENS_MAX_LENGTH)/2)

    if token_count > tokens_max_length:
        tokens = tokens[:tokens_max_length]
        truncated_text = encoding.decode(tokens)
    else:
        truncated_text = plain_text

    return {
        "original_token_count": token_count,
        "truncated_text": truncated_text,
        "truncated_text_count": len(encoding.encode(truncated_text))
    }
