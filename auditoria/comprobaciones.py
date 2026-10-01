import requests
from bs4 import BeautifulSoup


def descargar_html(url: str) -> BeautifulSoup | None:
    try:
        respuesta = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        respuesta.raise_for_status()
    except requests.RequestException:
        return None
    return BeautifulSoup(respuesta.text, "html.parser")


def comprobar_conversion(soup: BeautifulSoup) -> dict:
    enlaces = [a["href"].lower() for a in soup.find_all("a", href=True)]
    return {
        "telefono_clicable": any(e.startswith("tel:") for e in enlaces),
        "whatsapp": any("wa.me" in e or "whatsapp.com" in e for e in enlaces),
        "email_clicable": any(e.startswith("mailto:") for e in enlaces),
        "formulario": len(soup.find_all("form")) > 0,
    }


if __name__ == "__main__":
    soup = descargar_html("https://clinicaceodent.es/")
    if soup is None:
        print("No se pudo descargar la web")
    else:
        print(comprobar_conversion(soup))