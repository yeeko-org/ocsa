---
name: xls-export-blocks
description: XLSX export pattern. Use when adding, modifying, or debugging Excel exports.
---

# XLSX Export — ExportBlock + ExportXlsMixin

Read the two core classes first — their docstrings and inline comments explain the basic contracts. This document covers rules that are **not obvious from reading the code**.

---

## The field-path ↔ extract() contract

`columns[].field` is a `__`-separated path the mixin resolves by chaining
`.get()` calls on the row dict:

```
"field": "mention__note__id"  →  row["mention"]["note"]["id"]
```

`extract()` must return a dict whose key structure mirrors those paths. Blocks that embed sub-blocks must also call those sub-blocks' `extract()` to build the matching nesting:

```python
class ParentExportBlock(ExportBlock):
    columns = [
        *ChildExportBlock.prefixed("child"),
        {"name": "Own field", "width": 20, "field": "own"},
    ]

    @classmethod
    def extract(cls, obj) -> dict:
        return {
            "child": ChildExportBlock.extract(obj.child),
            "own": obj.own_field,
        }
```

For flat ORM annotations added via `get_annotations()`, set `"subquery": True` in the column dict — the mixin then reads it directly from the top-level row dict instead of traversing.

---

## preset vs. the block's own column paths

`preset` adds a prefix *on top of* the block's columns at expansion time — it does not change the structure `extract()` must return. Use it when the same block appears at different nesting depths in different ViewSets.

```python
# xls_attrs entry                      field produced in sheet
{"special_group": "actor"}                     →  "name", "sector__name", …
{"special_group": "actor", "preset": "actor"}  →  "actor__name", "actor__sector__name", …
```

The block's `columns` are never modified; copies are built at expansion.

---

## Adding export to a ViewSet

```python
class MyViewSet(ExportXlsMixin, BaseViewSet):
    xls_name = "My Export"
    xls_attrs = [
        {"name": "ID", "width": 5, "field": "id"},
        {"special_group": "actor", "preset": "actor"},
        {"name": "Status", "field": "status",
         "conditions": ["only_logged_in"]},
        {"name": "Note count", "field": "note_dates", "operation": "count"},
    ]

    def get_query_for_export_xls(self):
        return self.filter_queryset(
            MyModel.objects
            .select_related('actor', 'actor__sector')
            .distinct()
        )

    def get_export_rows(self, queryset) -> list[dict]:
        from utils.universal import safe_attr
        return [
            {
                "id": obj.id,
                "actor": ActorExportBlock.extract(obj.actor),
                "status": safe_attr(obj.status, 'name'),
                "note_dates": [
                    p.mention.note.date for p in obj.participants.all()
                ],
            }
            for obj in queryset
        ]
```

---

## Creating a new ExportBlock

```python
class MyEntityExportBlock(ExportBlock):
    columns = [
        {"name": "ID", "width": 5, "field": "id"},
        {"name": "Name", "width": 30, "field": "name"},
        {"name": "Type", "width": 20, "field": "type__name"},
    ]

    @classmethod
    def extract(cls, obj) -> dict:
        from utils.universal import safe_attr
        return {
            "id": safe_attr(obj, 'id'),
            "name": safe_attr(obj, 'name'),
            "type": {"name": safe_attr(obj, 'type', 'name')},
        }
```

Register it in `extra_attrs` so ViewSets can reference it as a `special_group`:

```python
extra_attrs = {
    ...
    "my_entity": MyEntityExportBlock,
}
```

---

## Column descriptor options

```python
{"name": "Label", "width": 20, "field": "a__b"}
{"name": "Label", "width": 10, "field": "ann", "subquery": True}
{"special_group": "key"}
{"special_group": "key", "preset": "prefix"}
{"name": "...", "field": "...", "conditions": ["only_logged_in"]}
{"name": "...", "field": "list_field", "operation": "count"}
{"name": "...", "field": "list_field", "operation": "min"}
{"name": "...", "field": "list_field", "operation": "max"}
```