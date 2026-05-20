"""Ingesta de notas legadas desde PDF.

Dos fases independientes e idempotentes (ver ``source/CLAUDE.md``):

- ``extract.PdfTextExtractor``: descarga el/los PDF de la ``Note``,
  extrae el crudo con PyMuPDF y lo persiste en ``Article.html_content``.
- ``clean.PdfAiCleaner``: limpia ese crudo con Gemini y puebla
  ``Article.paragraphs`` y campos de cabecera.

Importar desde los submódulos (patrón de ``source.criteria``), no desde
este paquete, para evitar costo de importación al cargar Django.
"""