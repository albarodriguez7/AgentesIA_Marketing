import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from urllib.parse import urljoin, urlparse


@tool
def leer_web(url: str) -> str:
    """Descarga una página web y devuelve su texto visible y la lista de enlaces a otras páginas de la misma web.
    Úsala para averiguar a qué se dedica una empresa, dónde está y cuántas sedes tiene.
    Para visitar otras páginas, usa solo direcciones de la lista de enlaces."""
    try:
        respuesta = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        respuesta.raise_for_status()   # mira el código de estado y, si es de error (400 o más), lanza un error de verdad
    except requests.RequestException as error:
        return f"No se pudo leer la web: {error}"

    soup = BeautifulSoup(respuesta.text, "html.parser")
    for etiqueta in soup(["script", "style", "noscript"]):    # ["script", "style", "noscript"] son partes del código de la página que no son texto útil y solo gastarían tokens
        etiqueta.decompose()

    dominio = urlparse(url).netloc
    enlaces = []
    for a in soup.find_all("a", href=True):    # Esto busca todos los enlaces de la página que tengan "href"
        enlace = urljoin(url, a["href"]).split("#")[0]     # urljoin convierte por ejemplo /contacto en https://www.ceodent.es/contacto para que sea una url de verdad
        if urlparse(enlace).netloc == dominio and enlace not in enlaces:   # Solo nos quedamos con enlaces de la misma web
            enlaces.append(enlace)

    texto = " ".join(soup.get_text(separator=" ").split())[:4000]    # quita los espacios y saltos de línea repetidos, que en las webs hay muchísimos
    lista_enlaces = "\n".join(enlaces[:30])   # máximo 30 enlaces
    return f"TEXTO DE LA PÁGINA:\n{texto}\n\nENLACES DE ESTA WEB:\n{lista_enlaces}"





if __name__ == "__main__":  # Solo se ejecuta este if si en el terminar invocamos "herramientas.py", no cuando se llame a la función "leer_web"
    resultado = leer_web.invoke("https://clinicaceodent.es/")
    print(resultado)