class ExportBlock:
    """Composable column-and-extractor unit for XLSX exports.

    `columns[].field` paths are relative to where this block sits in the
    row dict. A field `"type__name"` means `row["type"]["name"]` at that
    nesting level. When blocks are composed via `prefixed()`, the caller
    adds the outer key; the block itself always uses relative paths.

    `extract(obj)` must return a dict whose key structure mirrors those
    relative paths. Blocks that embed sub-blocks must call the sub-block's
    `extract()` to build the matching nesting.

    Keep `extract()` free of ORM queries — all needed data must be
    prefetched by the ViewSet's `get_query_for_export_xls()`.
    """

    columns: list[dict] = []

    @classmethod
    def extract(cls, obj) -> dict:
        raise NotImplementedError

    @classmethod
    def prefixed(cls, prefix: str) -> list[dict]:
        """Return copies of columns with field prepended by prefix__."""
        return [
            {**col, "field": f"{prefix}__{col['field']}"}
            for col in cls.columns
        ]