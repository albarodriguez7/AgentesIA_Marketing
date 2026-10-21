from auditoria.comprobaciones import comprobar_confianza, descargar_html
from auditoria.evaluaciones.crear_dataset import extraer_url
from leads.evaluaciones.crear_dataset import cargar_ejemplos


if __name__ == "__main__":
    urls = [extraer_url(ejemplo["lead"]) for ejemplo in cargar_ejemplos()]

    for url in urls:
        soup = descargar_html(url)
        if soup is None:
            print(f"⚪ {url} → no se pudo descargar")
            continue

        confianza = comprobar_confianza(url, soup)
        if not confianza["textos_legales"]:
            print(f"❌ {url} → SIN textos legales")