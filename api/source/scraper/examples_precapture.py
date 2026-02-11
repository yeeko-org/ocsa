from jsonpath_ng.ext import parse
import json


# def first_test(article_id: int) -> None:
from source.criteria.pre_capture import PreCaptureManager
from source.models import Article, Note

article_id = 42865
article = Article.objects.get(pk=article_id)

manager = PreCaptureManager(
    ai_engine="gemini-3-flash-preview",
)
manager.build_direct_criteria(article)

manager.save_criteria_results([], article.pre_capture, article)


self = manager

# first_test(42165)


note = article.note


def update_json_with_path(data, path_str, new_values):
    jsonpath_expr = parse(path_str)
    matches = jsonpath_expr.find(data)
    if matches:
        match = matches[0]
        match.value.update(new_values)
        return match.value
    return None

note = Note.objects.get(pk=5684)
my_json = note.pre_mentions
update_json_with_path(my_json, "$[0]", {"element_id": 5827, "discarded": False})
note.pre_mentions = my_json
note.save()



