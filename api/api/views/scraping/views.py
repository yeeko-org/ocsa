import threading
from api.views.common_views import BaseGenericViewSet
from django.db import connection

from rest_framework import permissions
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from urllib.parse import urlencode

from api.views.scraping.serializers import (
    ScrapingDateSerializer, ScrapedRecordSerializer)
from source.models import ScrapedRecord, Article
from source.scraper.jornada import JornadaManagerScraper
from source.scraper.reforma import ReformaManagerScraper
from source.tasks import article_full_content


def full_scrape_articles(scraped_record: ScrapedRecord):
    connection.close()  # TODO: revisar funcionamiento
    manager_scraper = JornadaManagerScraper(
        "", "", recover_record=scraped_record)

    manager_scraper.full_scrape_articles(update=True)


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

        if source == 'jornada':
            managerscraper_class = JornadaManagerScraper

        elif source == "reforma":
            managerscraper_class = ReformaManagerScraper

        else:
            raise ValidationError("Invalid source")
        manager_scraper = managerscraper_class(from_date, to_date or from_date)

        if manager_scraper.errors or manager_scraper.overlapping_dates:
            return Response({
                "errors": manager_scraper.errors,
                "overlapping_dates": manager_scraper.overlapping_dates
            }, status=status.HTTP_400_BAD_REQUEST)

        manager_scraper.scrape_sections()

        manager_scraper.record_articles()

        scraped_record = manager_scraper.scraped_record

        articles_url = reverse("articles-list")
        query = urlencode({"scraped": scraped_record.pk})

        response_data = {
            "articles_count": Article.objects.filter(
                scraped=scraped_record).count(),
            "scraped_record": scraped_record.pk,
            "errors": manager_scraper.errors,
            "articles": f"{articles_url}?{query}"
        }

        thread = threading.Thread(
            target=full_scrape_articles, args=(scraped_record,))
        thread.start()

        return Response(response_data)


class ScrapedRecordView(BaseGenericViewSet):
    queryset = ScrapedRecord.objects.all()
    serializer_class = ScrapedRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            return queryset
        return queryset.filter(status=ScrapedRecord.STATUS_DONE)
