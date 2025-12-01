# Ejecucion de pruebas de scraping por pasos completos, y sus formas de ver la informacion.

from pprint import pprint
from source.scraper.jornada import JornadaManagerScraper
from source.models import ScrapedRecord, Article


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

    manager_scraper.build_ai_criteria()


    # python manage.py articles_json "2022-10-01" "2022-12-31" 4
    # python manage.py articles_json "2023-05-05" "2023-05-05" 4

    # python manage.py compare_notes --settings=core.settings_prod




