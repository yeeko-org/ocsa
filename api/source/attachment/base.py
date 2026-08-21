"""Interfaz común de los generadores de adjunto por fuente."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from django.core.files.base import ContentFile

from source.models import Article, Note, NoteFile

logger = logging.getLogger(__name__)


@dataclass
class GeneratedAttachment:
    """Archivo listo para guardarse como NoteFile."""

    content: bytes
    file_name: str
    # Página impresa de la que salió el adjunto, cuando la fuente la
    # identifica: es el dato que corrige ``Note.pages`` al regenerar.
    page_code: str | None = None

    def is_usable(self) -> bool:
        """Sin bytes o sin nombre no hay archivo que guardar.

        Una fuente puede devolver una respuesta vacía con status 200; sin
        este filtro se crearía la fila con un archivo de cero bytes, que
        es justo el residuo que dejó la generación vieja.
        """
        return bool(self.content) and bool(self.file_name)


class AttachmentGenerator(ABC):
    """Recibe un Article y produce (o no) el NoteFile de su nota."""

    source_url: str

    def __init__(self, article: Article) -> None:
        self.article = article

    @abstractmethod
    def build(self) -> GeneratedAttachment | None:
        """Arma el archivo.

        Devuelve None cuando la fuente no da lo necesario (metadatos
        incompletos, PDF inaccesible): la ausencia de adjunto no es un
        error del flujo que crea la nota.
        """

    def generate(
            self, note: Note | None = None, replace: bool = False
    ) -> NoteFile | None:
        """Guarda el adjunto en la nota indicada (o la del artículo).

        Con ``replace=False`` respeta los archivos ya cargados —incluidos
        los que subió un editor a mano—; la regeneración masiva es la que
        pasa ``replace=True``.
        """
        note = note or self.article.note
        if not note or not note.pk:
            return None

        previous_pks = list(note.files.values_list("pk", flat=True))
        if previous_pks and not replace:
            return None

        attachment = self.safe_build()
        if not attachment or not attachment.is_usable():
            return None

        note_file = self.store(note, attachment, previous_pks)
        if not note_file:
            return None

        # Fuera de una regeneración solo se llena el hueco: una página
        # ya capturada por un editor no se pisa.
        if replace or not note.pages:
            self.update_note_pages(note, attachment.page_code)
        return note_file

    def safe_build(self) -> GeneratedAttachment | None:
        """Red de seguridad única para todas las fuentes.

        ``build`` toca red, PDF y render, y su contrato ya admite «no hay
        adjunto» como desenlace válido; un fallo suyo no puede tumbar la
        creación de la nota ni la corrida masiva. Vive aquí y no en cada
        generador para no repetirla por fuente.
        """
        try:
            return self.build()
        except Exception:
            logger.exception(
                "Falló %s sobre el artículo %s",
                type(self).__name__, self.article.pk)
            return None

    @staticmethod
    def store(
            note: Note, attachment: GeneratedAttachment,
            previous_pks: list[int],
    ) -> NoteFile | None:
        """Guarda el adjunto y solo entonces retira los anteriores.

        El orden es el invariante: los bytes llegan a storage, la fila
        queda escrita, y hasta después se borran los viejos. Un fallo a
        media descarga o a media escritura deja los adjuntos previos
        intactos, y nunca una fila NoteFile sin archivo detrás.
        """
        note_file = NoteFile(note=note)
        try:
            note_file.file.save(
                attachment.file_name, ContentFile(attachment.content),
                save=False)
        except Exception:
            logger.exception(
                "No se pudo escribir el adjunto de la nota %s", note.pk)
            return None
        if not note_file.file.name:
            return None

        try:
            note_file.save()
        except Exception:
            # Sin fila que lo apunte, el archivo recién escrito es basura
            # invisible: se retira antes de propagar el error.
            note_file.file.delete(save=False)
            raise

        if previous_pks:
            # La señal post_delete borra el archivo en storage salvo que
            # otra fila lo apunte; guardar antes de borrar hace que el
            # nuevo NoteFile proteja la clave si el nombre coincidiera.
            NoteFile.objects.filter(pk__in=previous_pks).delete()
        return note_file

    @staticmethod
    def update_note_pages(note: Note, page_code: str | None) -> bool:
        """Corrige la página impresa de la nota al regenerar.

        Las notas anteriores a task-41 guardaron el código de la portada
        de sección, no el de la página donde salió el artículo; el
        adjunto ya trae el correcto y esta es la única ocasión en que se
        recalcula.
        """
        if not page_code or note.pages == page_code:
            return False
        note.pages = page_code
        note.save(update_fields=["pages"])
        return True
