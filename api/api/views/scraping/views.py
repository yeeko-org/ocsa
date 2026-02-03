import threading
from api.views.common_views import BaseGenericViewSet
from django.db import connection
from django_filters import FilterSet, DateFilter
from django.db.models import Count

from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from api.permissions import IsFullEditorOrReadOnly
from api.views.article.source_serializers import ScrapedRecordSimpleSerializer, ScrapedRecordSerializer, \
    ScrapingDateSerializer
from source.models import ScrapedRecord, Article
from source.scraper.jornada import JornadaManagerScraper
from source.scraper.reforma import ReformaManagerScraper
from source.scraper.criteria import ManagerCriteria


def get_manager_scraper_class(source):
    from source.models import Source
    if isinstance(source, int):
        source = Source.objects.get(pk=source).name.lower()
    if source == 'jornada' or source == 'la jornada':
        return JornadaManagerScraper
    elif source == "reforma":
        return ReformaManagerScraper
    elif source == "proceso":
        from source.scraper.proceso import ProcesoManagerScraper

        return ProcesoManagerScraper
    else:
        raise ValidationError("Invalid source")


def full_scrape_articles(scraped_record: ScrapedRecord):
    from django.utils import timezone
    # connection.close()  # TODO: revisar funcionamiento

    manager_scraper_class = get_manager_scraper_class(scraped_record.source)
    manager_scraper = manager_scraper_class(
        "", "", recover_record=scraped_record)
    scraped_record.last_updated = timezone.now()
    scraped_record.save()
    manager_scraper.scrape_articles(update=True)
    manager_criteria = ManagerCriteria(
        recover_record=scraped_record, ai_engine="gemini-3-flash-preview")

    manager_criteria.build_first_criteria()
    manager_criteria.build_second_criteria()


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

        manager_scraper = manager_scraper_class(from_date, to_date or from_date)

        if manager_scraper.errors or manager_scraper.overlapping_dates:
            return Response({
                "errors": manager_scraper.errors,
                "overlapping_dates": manager_scraper.overlapping_dates
            }, status=status.HTTP_400_BAD_REQUEST)

        manager_scraper.scrape_sections()

        manager_scraper.record_articles()

        scraped_record = manager_scraper.scraped_record
        scraped_data = ScrapedRecordSimpleSerializer(scraped_record).data
        response_data = {
            "articles_count": Article.objects.filter(
                scraped=scraped_record).count(),
            "scraped_record": scraped_data,
            "errors": manager_scraper.errors,
        }

        thread = threading.Thread(
            target=full_scrape_articles, args=(scraped_record,))
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
        .select_related('source')\
        .annotate(articles_count=Count('articles'))
    serializer_class = ScrapedRecordSerializer
    permission_classes = [IsFullEditorOrReadOnly]
    ordering = ['-from_date']

    filterset_class = ScrapedRecordFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        # is_retrieve = self.action == 'retrieve'
        # if is_retrieve:

        if self.request.user.is_authenticated:
            return queryset
        # return queryset.filter(status=ScrapedRecord.STATUS_DONE)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        serializer.instance.user = request.user
        serializer.instance.save()
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=["post"],
            permission_classes=[IsFullEditorOrReadOnly])
    def reprocess(self, request, pk=None):
        from django.utils import timezone
        from datetime import timedelta

        scraped_record = self.get_object()
        source = scraped_record.source.id
        dates = []
        fields = ['date_start', 'last_updated']
        for field in fields:
            date_value = getattr(scraped_record, field)
            if date_value:
                dates.append(date_value)
        max_date = max(dates)

        time_now = timezone.now()
        # articles_count = scraped_record.articles.count()

        total_minutes = scraped_record.total_days * 3
        if max_date + timedelta(minutes=total_minutes) > time_now:
            if not request.user.is_superuser:
                return Response(
                    {"detail": "Cannot reprocess a recently updated scraped record."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # last_update = min(scraped_record.date_end, scraped_record.last_update)
        if not scraped_record.date_end:
            if scraped_record.date_start + timedelta(days=1) < time_now:
                return Response(
                    {"detail": "Cannot reprocess an ongoing scraped record."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        thread = threading.Thread(
            target=full_scrape_articles, args=(scraped_record, ))
        thread.start()
        return Response(
            {"detail": "Reprocessing started."},
            status=status.HTTP_200_OK
        )


