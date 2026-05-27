# Script ad-hoc para ingestar notas legadas desde PDF.
# Ejecutar desde el shell de Django / PyCharm (no es un comando).
#
# Dos fases independientes e idempotentes:
#   1) PdfTextExtractor: descarga PDF + extrae crudo -> Article.html_content
#   2) PdfAiCleaner: limpia el crudo con Gemini -> Article.paragraphs
# Se pueden correr por separado; re-correr no duplica ni reprocesa.

from source.pdf_import.extract import PdfTextExtractor
from source.pdf_import.clean import PdfAiCleaner

# --- 1) Extracción del crudo (sin IA) -----------------------------------
# Usar limit=N para una primera corrida acotada de prueba.
extractor = PdfTextExtractor()
extractor.run()

# --- 2) Limpieza asistida por IA ----------------------------------------
cleaner = PdfAiCleaner(ai_engine="gemini-3-flash-preview")
cleaner.run()

# --- Inspección de una muestra (monitoreo en localhost) -----------------
# from source.models import Article
# sample = Article.objects.filter(uid__startswith="pdf-note-")[:20]
# for art in sample:
#     md = art.metadata or {}
#     print(art.id, art.note_id, "| párrafos:", len(art.paragraphs or []),
#           "| pdf_clean:", md.get("pdf_clean"),
#           "| detectado:", md.get("pdf_detected"))
#     if art.errors:
#         print("   errores:", art.errors[-1])

# --- Reintentar un problemático (limpiar la marca y re-correr Fase 2) ----
# from source.models import Article
# art = Article.objects.get(uid="pdf-note-123")
# md = art.metadata or {}
# md.pop("pdf_clean", None)
# art.metadata = md
# art.save()
# PdfAiCleaner(ai_engine="gemini-3-flash-preview").run()