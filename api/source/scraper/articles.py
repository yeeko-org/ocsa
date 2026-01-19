from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from typing import Dict, List, Type
from tqdm import tqdm
from source.models import Article, ScrapedRecord, Source
from source.scraper.scraper_base import MainScraper, ArticleScraper


def date_in_date(date_: str | date) -> date:
    if isinstance(date_, date):
        return date_
    try:
        return datetime.strptime(date_, "%Y/%m/%d")
    except ValueError as e:

        try:
            return datetime.strptime(date_, "%Y%m%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format. Must be YYYY/MM/DD: {e}")


def get_date_range(
        from_date: str | date, to_date: str | date,
        date_out_format: str = "%Y/%m/%d"
) -> List[str]:

    from_date = date_in_date(from_date)
    to_date = date_in_date(to_date)

    if from_date > to_date:
        raise ValueError(
            "'from_date' debe ser anterior o igual a 'to_date'")

    date_list = []
    current_date = from_date
    while current_date <= to_date:
        date_list.append(current_date.strftime(date_out_format))
        current_date += timedelta(days=1)

    return date_list


class CriteriaError(Exception):

    def __init__(self, article: Article, message: str,
                 exception: Exception | None = None):
        from django.utils import timezone
        final_msg = message
        if exception:
            final_msg += f" | Exception: {str(exception)}"
        if article:
            article_error = f"{timezone.now().isoformat()} - {final_msg}"
            article.errors = article.errors or []
            article.errors.append(article_error)
            article.save()
        final_msg = f"ID - {article.id} ({article.title}): {final_msg}"
        super().__init__(final_msg)


class ManagerScraper(ABC):
    scraped_record: ScrapedRecord | None
    main_scraper_class: Type["MainScraper"]
    article_scraper_class: Type["ArticleScraper"]

    date_format = "%Y/%m/%d"
    parser = "html.parser"
    source: Source
    articles_by_date: Dict[str, dict]
    overlapping_dates: list
    errors: list

    def __init__(
            self, from_date: str | date | None, to_date: str | date | None,
            main_scraper_class: Type["MainScraper"],
            article_scraper_class: Type["ArticleScraper"],
            recover_record: ScrapedRecord | None = None,
    ) -> None:
        self.main_scraper_class = main_scraper_class
        self.article_scraper_class = article_scraper_class
        self.overlapping_dates = []
        self.errors = []
        self.scraped_record = None

        if recover_record:
            self.scraped_record = recover_record
            self.source = recover_record.source or self.get_source()
            return

        if not self.check_overlapping_records(from_date, to_date):
            print("Overlapping records found, aborting scraping.")
            return

        self.scraped_record = ScrapedRecord.objects.create(
            source=self.get_source(), from_date=date_in_date(from_date),
            to_date=date_in_date(to_date))

    def add_errors(self, errors: List[str]):
        if not self.scraped_record:
            self.errors.extend(errors)
            return
        if not self.scraped_record.errors:
            self.scraped_record.errors = []
        self.scraped_record.errors.extend(errors)
        self.scraped_record.save()

    def add_error(
            self, error: str,
            exception: Exception | None = None,
            raise_exception: bool = False):

        if exception and raise_exception:
            raise exception
        if not self.scraped_record:
            self.errors.append(f"{error}: {exception or ''}")
            return

        if not self.scraped_record.errors:
            self.scraped_record.errors = []

        self.scraped_record.errors.append(f"{error}: {exception or ''}")
        self.scraped_record.save()

    def check_overlapping_records(self, from_date, to_date):
        from_date = date_in_date(from_date)
        to_date = date_in_date(to_date)

        overlapping_records = ScrapedRecord.objects.filter(
            from_date__lte=to_date,
            to_date__gte=from_date,
            source=self.get_source(),
            status__isnull=False
        ).exclude(status="failed")

        self.overlapping_dates = [
            [record.from_date.strftime("%Y/%m/%d"),
             record.to_date.strftime("%Y/%m/%d")]
            for record in overlapping_records
        ]

        if self.overlapping_dates:
            self.add_error("Ya existen registros para las fechas")
            return False
        return True

    def scrape_sections(self):

        self.scraped_record.set_status("get_sections")
        str_dates = get_date_range(
            self.scraped_record.from_date, self.scraped_record.to_date,
            date_out_format=self.date_format)
        articles_by_date = {}

        for date_ in str_dates:
            try:
                sections_dict = self.main_scraper_class(date_).sections_dict
            except Exception as e:
                sections_dict = {
                    "error": f"Error getting sections for date {date_}",
                    "exception": str(e)
                }
            articles_by_date[date_] = sections_dict

        self.scraped_record.data = articles_by_date  # type: ignore
        self.scraped_record.save()

    @abstractmethod
    def get_source(self) -> Source:
        raise NotImplementedError

    def record_articles(self):
        self.scraped_record.set_status("record_articles")

        self.get_source()
        for date_, sections_dict in self.scraped_record.data.items():  # type: ignore
            for section_name, section_data in sections_dict.items():
                if section_name in ["error", "exception"]:
                    print(f"Error in {date_}/{section_name} : {section_data}")
                    continue
                for article_data in section_data.get("articles", []):
                    try:
                        self.record_article(
                            article_data, section_name, date_)
                    except Exception as e:
                        article_data.setdefault("errors", []).append(str(e))

        self.scraped_record.save()

    def record_article(
            self, article_data: dict, section_name: str, date_: str,
    ):
        uid = article_data.get("uid") or ""
        title = article_data.get("title")
        url = article_data.get("url")
        if not all([uid, url]):
            return
        images = article_data.get("images")
        content = article_data.get("content")
        metadata = article_data.get("metadata")

        defaults = {
            "title": title,
            "url": url,
            "images": images,
            "basic_content": content,
            "metadata": metadata,
            "section": section_name,
            "published_date": date_in_date(date_),
            "scraped": self.scraped_record,
        }
        article_obj, _ = Article.objects.get_or_create(
            uid=uid, source=self.get_source(), defaults=defaults)

    def scrape_articles(self, update: bool = False):
        articles = Article.objects.filter(scraped=self.scraped_record)
        for article in tqdm(articles, desc="Scraping articles"):
            try:
                self.full_scrape_article(article, update)
            except CriteriaError as e:
                self.add_error(str(e))

    def full_scrape_article(
            self, article: Article, update: bool = False):

        if not article.content:
            try:
                article_scraper = self.article_scraper_class(
                    article, update=update)
            except Exception as e:
                raise CriteriaError(
                    article, "Error scraping article", e)
            try:
                article_scraper.get_reduced_content_text()
            except Exception as e:
                raise CriteriaError(
                    article, "Error getting content for article", e)
