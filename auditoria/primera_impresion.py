from bs4 import BeautifulSoup

from auditoria.comprobaciones import descargar_html

MAX_H1 = 3
MAX_SUBTITULOS = 5
MAX_PARRAFOS = 3
MIN_CARACTERES_PARRAFO = 40


def textos_de(soup: BeautifulSoup, etiqueta: str, maximo: int, minimo_caracteres: int = 0) -> list:
    textos = []
    for elemento in soup.find_all(etiqueta):
        texto = elemento.get_text(" ", strip=True)
        if texto and len(texto) >= minimo_caracteres:    # descarta los vacíos y los demasiado cortos
            textos.append(texto)
    return textos[:maximo]   # se queda solo con los maximo primeros


def extraer_primera_impresion(soup: BeautifulSoup) -> dict:
    titulo = soup.title.get_text(" ", strip=True) if soup.title else ""  
    # Es como escribir esto:
    # if soup.title:
    #     titulo = soup.title.get_text(strip=True)
    # else:
    # t   itulo = ""


    meta = soup.find("meta", attrs={"name": "description"})    # attrs= filtra por atributos: aquí, una <meta> cuyo "name" sea "description"
    descripcion = meta.get("content", "") if meta else ""
    return {
        "titulo": titulo,
        "descripcion": descripcion,
        "h1": textos_de(soup, "h1", MAX_H1),
        "subtitulos": textos_de(soup, "h2", MAX_SUBTITULOS),
        "parrafos": textos_de(soup, "p", MAX_PARRAFOS, MIN_CARACTERES_PARRAFO),
    }


if __name__ == "__main__":
    soup = descargar_html("https://clinicaceodent.es/")
    if soup is None:
        print("No se pudo descargar la web")
    else:
        print(extraer_primera_impresion(soup))
