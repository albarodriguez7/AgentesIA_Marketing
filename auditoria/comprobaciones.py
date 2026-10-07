import requests
from bs4 import BeautifulSoup, Tag



def descargar_html(url: str) -> BeautifulSoup | None:
    try:
        respuesta = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        respuesta.raise_for_status()
    except requests.RequestException:
        return None
    return BeautifulSoup(respuesta.text, "html.parser")


def usa_https(url: str) -> bool:
    return url.startswith("https://")   # Comprobar que empieza por https



PALABRAS_LEGALES = ["aviso legal", "privacidad"]
PALABRAS_OPINIONES = ["opiniones", "testimonios", "reseñas", "valoraciones", "experiencias"]


def algun_enlace_contiene(soup: BeautifulSoup, palabras: list) -> bool:
    for enlace in soup.find_all("a", href=True):
        texto = enlace.get_text().lower()
        if any(palabra in texto for palabra in palabras):
            return True
    return False


def tiene_textos_legales(soup: BeautifulSoup) -> bool:
    return algun_enlace_contiene(soup, PALABRAS_LEGALES)


def tiene_opiniones(soup: BeautifulSoup) -> bool:
    return algun_enlace_contiene(soup, PALABRAS_OPINIONES)



def comprobar_confianza(url: str, soup: BeautifulSoup) -> dict:
    return {
        "https": usa_https(url),
        "textos_legales": tiene_textos_legales(soup),
        "opiniones": tiene_opiniones(soup),
    }



PATRONES_WHATSAPP = ["wa.me", "wa.link", "whatsapp.com", "whatsapp://"]


def es_enlace_whatsapp(enlace: Tag) -> bool:
    direccion = enlace["href"].lower()
    texto = f'{enlace.get_text()} {enlace.get("aria-label", "")} {enlace.get("title", "")}'.lower()
    return any(patron in direccion for patron in PATRONES_WHATSAPP) or "whatsapp" in texto


def comprobar_conversion(soup: BeautifulSoup) -> dict:
    enlaces = soup.find_all("a", href=True)
    direcciones = [a["href"].lower() for a in enlaces]
    return {
        "telefono_clicable": any(d.startswith("tel:") for d in direcciones),
        "whatsapp": any(es_enlace_whatsapp(a) for a in enlaces),
        "email_clicable": any(d.startswith("mailto:") for d in direcciones),
        "formulario": len(soup.find_all("form")) > 0,
    }





if __name__ == "__main__":
    url = "https://clinicaceodent.es/"
    soup = descargar_html(url)
    if soup is None:
        print("No se pudo descargar la web")
    else:
        print("Conversión:", comprobar_conversion(soup))
        print("Confianza:", comprobar_confianza(url, soup))
        # debugging:
        # print("Veces que aparece 'whatsapp' en el HTML:", html.count("whatsapp"))
        # for a in soup.find_all("a", href=True):
        #     if "whatsapp" in a["href"].lower() or "whatsapp" in a.get_text().lower():
        #         print("Enlace relacionado con WhatsApp:", a["href"])