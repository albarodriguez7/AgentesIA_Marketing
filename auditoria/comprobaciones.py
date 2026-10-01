import requests
from bs4 import BeautifulSoup, Tag


def descargar_html(url: str) -> BeautifulSoup | None:
    try:
        respuesta = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        respuesta.raise_for_status()
    except requests.RequestException:
        return None
    return BeautifulSoup(respuesta.text, "html.parser")


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
    soup = descargar_html("https://clinicaceodent.es/")
    if soup is None:
        print("No se pudo descargar la web")
    else:
        print(comprobar_conversion(soup))
        html = str(soup).lower() 
        # debugging:
        # print("Veces que aparece 'whatsapp' en el HTML:", html.count("whatsapp"))
        # for a in soup.find_all("a", href=True):
        #     if "whatsapp" in a["href"].lower() or "whatsapp" in a.get_text().lower():
        #         print("Enlace relacionado con WhatsApp:", a["href"])