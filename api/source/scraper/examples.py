# Ejecucion de pruebas de scraping por pasos completos, y sus formas de ver la informacion.

from pprint import pprint

from source.models import Article, ScrapedRecord
from source.scraper.jornada import JornadaManagerScraper
from source.scraper.proceso import ProcesoManagerScraper, close_all_pressreader_sessions


def examples_base():

    # manager_scraper = JornadaManagerScraper(
    #     "2022/10/01", "2022/12/31", ai_engine="gpt-4o-mini")
    manager_scraper = JornadaManagerScraper(
        "2022/02/01", "2023/02/28", ai_engine="gpt-4o-mini")

    # print(manager_scraper.scraped_record)
    manager_scraper.scrape_sections()

    # aqui podemos ver toda la estructura de la informacion que se obtuvo por
    # cada fecha, seccion, articulo y los posibles errores que se hayan tenido
    # en el proceso a nivel de fecha, seccion o articulo.
    pprint(manager_scraper.scraped_record.data)

    # se puede consultar el admin para mejor visualizacion de los datos
    # tambien podemos recuperar el record desde donde lo dejamos usando el record como referencia

    manager_scraper = JornadaManagerScraper(
        "", "", recover_record=ScrapedRecord.objects.last(),
        ai_engine="gpt-4o-mini")
    manager_scraper = JornadaManagerScraper(
        "", "", recover_record=ScrapedRecord.objects.get(pk=10),
        ai_engine="gpt-4o-mini")

    # record articles genera los registros de los articulos con get_or_create
    # basado en el uid y el source, tambien genera los datos de las listas
    # articles_for_ai y articles_by_uid, compatible con recuperacion
    manager_scraper.record_articles()
    # manager_scraper.record_articles(reset=True)
    manager_scraper.scrape_articles()

    manager_scraper.build_first_criteria()


    # python manage.py articles_json "2022-10-01" "2022-12-31" 4
    # python manage.py articles_json "2023-05-05" "2023-05-05" 4

    # python manage.py compare_notes --settings=core.settings_prod


def examples_proceso():
    """
    Ejemplo de uso del scraper de Proceso usando la API de PressReader.

    IMPORTANTE: Antes de ejecutar, asegúrate de tener configurado el
    PRESSREADER_TOKEN en las variables de entorno.

    Ejemplo:
    export PRESSREADER_TOKEN="tu_token_aqui"

    O agrégalo al archivo .env:
    PRESSREADER_TOKEN=tu_token_aqui
    """

    # Scrapear un rango de fechas
    # Formato de fecha: "YYYY/MM/DD" o date object
    manager_scraper = ProcesoManagerScraper("2025/09/01", "2025/09/30")
    manager_scraper = ProcesoManagerScraper(
        "", "", recover_record=ScrapedRecord.objects.get(id=82))

    # Paso 1: Obtener secciones y artículos de la API
    manager_scraper.scrape_sections()

    # Ver la estructura de datos obtenida
    pprint(manager_scraper.scraped_record.data)

    # Paso 2: Registrar artículos en la base de datos
    manager_scraper.record_articles()

    # Paso 3: Obtener el contenido completo de cada artículo
    manager_scraper.scrape_articles()

    # Paso 4: Aplicar criterios de IA para clasificación
    from source.scraper.criteria import ManagerCriteria

    manager_criteria = ManagerCriteria(
        recover_record=manager_scraper.scraped_record,
        ai_engine="gemini-3-flash-preview",
    )
    manager_criteria.build_first_criteria()
    manager_criteria.build_second_criteria()

    # Recuperar un scraping existente
    # manager_scraper = ProcesoManagerScraper(
    #     "", "", recover_record=ScrapedRecord.objects.last())

    # Ver artículos scrapeados
    articles = Article.objects.filter(
        scraped=manager_scraper.scraped_record, source__name="Proceso"
    )
    print(f"Total de artículos scrapeados: {articles.count()}")

    # Ver artículos relevantes (con certainty_degree > 100)
    relevant_articles = articles.filter(certainty_degree__gt=100)
    print(f"Artículos relevantes: {relevant_articles.count()}")

    for article in relevant_articles[:5]:
        print(f"\nTítulo: {article.title}")
        print(f"Sección: {article.section}")
        print(f"Grado de certeza: {article.certainty_degree}")
        print(f"URL: {article.url}")


def direct_article():
    from source.scraper.proceso import ProcesoArticleScraper, close_all_pressreader_sessions
    from source.models import Article, ScrapedRecord
    article = Article.objects.get(pk=45293)
    scraper = ProcesoArticleScraper(article, update=True)
    scraper.get_reduced_content_text()

    close_all_pressreader_sessions()


