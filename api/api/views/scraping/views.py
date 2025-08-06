import threading
from api.views.common_views import BaseGenericViewSet
from django.db import connection
from django_filters import FilterSet, DateFilter
from django.db.models import Count

from rest_framework import permissions
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from urllib.parse import urlencode
from api.permissions import IsEditorOrCreateOrRead
from api.views.article.serializers import (
    ScrapingDateSerializer, ScrapedRecordSerializer,
    ScrapedRecordSimpleSerializer)
from source.models import ScrapedRecord, Article
from source.scraper.jornada import JornadaManagerScraper
from source.scraper.reforma import ReformaManagerScraper


def full_scrape_articles(source, scraped_record: ScrapedRecord):
    connection.close()  # TODO: revisar funcionamiento

    manager_scraper_class = get_manager_scraper_class(source)
    manager_scraper = manager_scraper_class(
        "", "", recover_record=scraped_record,
        open_ai_engine="gemini-2.5-flash")

    manager_scraper.scrape_articles(update=True)
    manager_scraper.build_ai_criteria(block_size=1)


class ScrapingDatesView(APIView):
    serializer_class = ScrapingDateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        serializer = ScrapingDateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        from_date = serializer.validated_data['from_date']  # type: ignore
        to_date = serializer.validated_data['to_date']  # type: ignore
        source = serializer.validated_data['source']  # type: ignore
        print(f"Scraping from {from_date} to {to_date} for source {source}")

        manager_scraper_class = get_manager_scraper_class(source)
        print(f"Using scraper class: {manager_scraper_class.__name__}")

        manager_scraper = manager_scraper_class(
            from_date, to_date or from_date, open_ai_engine="gemini-2.5-flash")

        if manager_scraper.errors or manager_scraper.overlapping_dates:
            return Response({
                "errors": manager_scraper.errors,
                "overlapping_dates": manager_scraper.overlapping_dates
            }, status=status.HTTP_400_BAD_REQUEST)

        manager_scraper.scrape_sections()

        manager_scraper.record_articles()
        # manager_scraper.scrape_articles()
        # manager_scraper.build_ai_criteria(block_size=1)

        scraped_record = manager_scraper.scraped_record
        scraped_data = ScrapedRecordSimpleSerializer(scraped_record).data
        response_data = {
            "articles_count": Article.objects.filter(
                scraped=scraped_record).count(),
            "scraped_record": scraped_data,
            "errors": manager_scraper.errors,
        }

        thread = threading.Thread(
            target=full_scrape_articles, args=(source, scraped_record,))
        thread.start()

        return Response(response_data)


class ScrapedRecordFilter(FilterSet):
    from_date = DateFilter(field_name='from_date', lookup_expr='gte')
    to_date = DateFilter(field_name='to_date', lookup_expr='lte')
    class Meta:
        model = ScrapedRecord
        fields = {
            'source': ['exact'],
        }


class ScrapedRecordView(BaseGenericViewSet):

    queryset = ScrapedRecord.objects.all()\
        .annotate(articles_count=Count('articles'))
    serializer_class = ScrapedRecordSerializer
    permission_classes = [IsEditorOrCreateOrRead]

    filterset_class = ScrapedRecordFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        # is_retrieve = self.action == 'retrieve'
        # if is_retrieve:

        if self.request.user.is_authenticated:
            return queryset
        # return queryset.filter(status=ScrapedRecord.STATUS_DONE)
        return queryset


def get_manager_scraper_class(source):
    from source.models import Source
    if isinstance(source, int):
        source = Source.objects.get(pk=source).name.lower()
    if source == 'jornada' or source == 'la jornada':
        return JornadaManagerScraper
    elif source == "reforma":
        return ReformaManagerScraper
    else:
        raise ValidationError("Invalid source")

