# Script ad-hoc para reclasificar eventos al grupo "Mecanismos legales".
# Ejecutar desde el shell de Django / PyCharm (no es un comando).
from event.models import Event
from source.criteria.reclassify_legal import ReclassifyLegalManager


def backfill_pending() -> int:
    """Marca como 'pending' los eventos cuyo event_type sigue en
    'need_reclassify' y que aún no tienen etapa. Idempotente: no toca
    los que ya fueron reclasificados/confirmados/descartados.
    """
    return Event.objects.filter(
        event_type__status_validation_id='need_reclassify',
        reclassification_stage__isnull=True,
    ).update(reclassification_stage='pending')


# --- 1) Backfill (una vez; seguro de repetir) ---------------------------
marked = backfill_pending()
print(f"Eventos marcados como pending: {marked}")

# --- 2) Reclasificación asistida por IA ---------------------------------
manager = ReclassifyLegalManager(ai_engine="gemini-3-flash-preview")
manager.run()

# --- Inspección de una muestra (monitoreo en localhost) -----------------
# from event.models import Event
# sample = Event.objects.filter(
#     reclassification_stage='reclassified',
#     reclassification_confidence__lt=60,
# ).select_related('event_type')[:20]
# for ev in sample:
#     print(ev.id, ev.reclassification_confidence,
#           ev.reclassification_data)


from source.criteria.reclassify_legal import ReclassifyLegalManager

m = ReclassifyLegalManager(ai_engine="gemini-3-flash-preview")
# backfill primero (marca pending), luego:
art = m.get_articles_objects()[0]
m.build_direct_criteria(art)
