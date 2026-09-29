import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool


@tool
def leer_web(url: str) -> str:
    """Descarga una página web y devuelve su texto visible.
    Úsala para averiguar a qué se dedica una empresa, dónde está y cuántas sedes tiene."""
    try:
        respuesta = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        respuesta.raise_for_status()   # mira el código de estado y, si es de error (400 o más), lanza un error de verdad
    except requests.RequestException as error:
        return f"No se pudo leer la web: {error}"

    soup = BeautifulSoup(respuesta.text, "html.parser")
    for etiqueta in soup(["script", "style", "noscript"]):  # ["script", "style", "noscript"] son partes del código de la página que no son texto útil y solo gastarían tokens
        etiqueta.decompose()

    texto = " ".join(soup.get_text(separator=" ").split())   # quita los espacios y saltos de línea repetidos, que en las webs hay muchísimos
    return texto[:4000]  # nos quedamos con los primeros 4.000 caracteres


if __name__ == "__main__":  # Solo se ejecuta este if si en el terminar invocamos "herramientas.py", no cuando se llame a la función "leer_web"
    resultado = leer_web.invoke("https://clinicaceodent.es/")
    print(resultado[:1000])
    print("\nCaracteres:", len(resultado))