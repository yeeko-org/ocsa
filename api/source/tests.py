from source.scraper.proceso import ProcesoMainScraper


def probe_proceso_sections(scraper_date: str = "20240201") -> None:
    """
    Sonda manual: cuántas secciones y artículos trae un issue de Proceso.

    Vive dentro de una función porque `manage.py test` importa este módulo:
    suelto, disparaba un scraping real contra PressReader en cada corrida
    y quemaba el slot de sesión.
    """
    main = ProcesoMainScraper(scraper_date)
    print("secciones:", list(main.sections_dict.keys()))
    total = sum(len(s["articles"]) for s in main.sections_dict.values())
    print("total artículos:", total)
