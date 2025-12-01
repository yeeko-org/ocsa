from source.scraper.articles import ManagerScraper
from source.models import (
    Article, ScrapedRecord, Source, ArticleQualify, QualifySchema)
from typing import Any, Dict, List, Type


class PreClassify(ManagerScraper):

    def make_preclassify_articles(
            self, block_size: int = 0, alt_version: bool = False):
        self.scraped_record.status = "preclassify"
        self.scraped_record.save()
        if block_size:
            self.block_size = block_size

        if not self.articles_for_openAI:
            return
        prompt_path = "source/scraper/prompt_pre_classify.txt.back"

        if alt_version:
            prompt_path = "source/scraper/prompt_pre_classify_v2.txt.back"

        self.qualify_schema = None

        len_articles = len(self.articles_for_openAI)
        print(f"Preclassify articles for {len_articles} articles")
        for i in range(0, len_articles, self.block_size):
            print(f"Preclassifying articles {i} to {i + self.block_size}")
            self.preclassify_articles(
                self.articles_for_openAI[i:i + self.block_size], prompt_path)

        self.scraped_record.save()

    def preclassify_articles(self, articles: List[dict], prompt_path: str):
        try:
            # full_prompt = json.dumps(articles)
            simple_articles = { }
            for article in articles:
                title = article.get("title")
                if section := article.get("section"):
                    title = f"{title} ({section})"
                simple_articles[article["id"]] = title
            full_prompt = json.dumps(simple_articles, ensure_ascii=False)
        except TypeError as e:
            print(f"Error converting to json art: {e}")
            print("articles:", articles)
            return

        # TODO: Lucian, comentemos esto, pero es super difícil de encontrar
        # algunas cosas como el engine, está en muchos lados y no sé si
        # está declarado acá o allá o en dónde y me confundo, pasa mucho en
        # muchos lados y me pierdo entre miles de declaraciones aisladas.
        self.pre_classify_request = JsonRequestOpenAI(
            prompt_path, engine=self.ai_engine,
            use_deepseek=self.use_deepseek)

        self.pre_classify_response, request_id = self.pre_classify_request \
            .send_prompt(full_prompt)
        if not self.pre_classify_response:
            print("No response from OpenAI")
            return

        try:
            pre_classify_response_items = self.pre_classify_response.items()  # type: ignore
        except Exception as e:
            self.add_error("Error getting items from response", e)
            return
        if not self.scraped_record.preclassification:
            self.scraped_record.preclassification = []  # type: ignore
        self.scraped_record.preclassification += pre_classify_response_items
        counter = { "maybe": 0, "valid": 0, "invalid": 0, "unknown": 0 }
        for article_id, preclassification in pre_classify_response_items:
            # print(f"Preclassification for {uid}: {preclasification}")
            # print(f"objeto: {self.articles_by_uid.get(uid)}")
            if preclassification not in ["valid", "invalid", "maybe", "unknown"]:
                print(f"Invalid preclassification: {preclassification}")
                continue
            # article_obj = self.articles_by_uid.get(uid)
            counter[preclassification] += 1
            article_id = int(article_id)
            article_obj = self.articles_by_id.get(article_id)
            if not article_obj:
                continue
            # is_selected = preclassification in ["valid", "maybe", "unknown"]
            article_obj.preclassification = preclassification
            article_obj.save()
        print(f"counters: {counter.items()}")
