"""Los exports de eventos y afectaciones solo traen la ubicación del
proyecto (adr-0035): desde la 0005 de `space_time` ni el evento ni la
afectación tienen ubicación propia.
"""
from django.test import RequestFactory, SimpleTestCase

from api.export_blocks.event import EventExport
from api.export_blocks.impact import ImpactExport
from api.export_blocks.location import LocationBlock, ProjectLocationBlock
from profile_auth.models import User


def titles(columns) -> list[str]:
    return [column.title for column in columns]


class ExportLocationColumnsTests(SimpleTestCase):

    def assert_only_project_location(self, export_class) -> None:
        # Sin request la librería omite toda columna con condition; con
        # usuario autenticado salen todas las que el export puede dar.
        request = RequestFactory().get("/")
        request.user = User(username="capturista")
        columns = export_class().get_resolved_columns(request)
        headers = titles(columns)
        own = set(titles(LocationBlock.columns)) & set(headers)
        self.assertEqual(own, set(), "columnas de ubicación propia")
        for title in titles(ProjectLocationBlock.columns):
            self.assertIn(title, headers)
            self.assertTrue(title.endswith(" del proyecto"), title)

    def test_eventos(self):
        self.assert_only_project_location(EventExport)

    def test_afectaciones(self):
        self.assert_only_project_location(ImpactExport)
