from source.scraper.proceso import ProcesoMainScraper

main = ProcesoMainScraper("20240201")
print("secciones:", list(main.sections_dict.keys()))
total = sum(len(s["articles"]) for s in main.sections_dict.values())
print("total artículos:", total)

