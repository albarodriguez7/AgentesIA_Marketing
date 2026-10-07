from typing import Literal

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from dotenv import load_dotenv

from auditoria.comprobaciones import descargar_html

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage




class Criterio(BaseModel):
    cumple: Literal["si", "parcialmente", "no"] = Field(
        description="'si' si se ve con claridad, 'parcialmente' si es vago o incompleto, 'no' si no aparece."
    )
    prueba: str = Field(
        description=(
            "La frase más corta posible (una sola oración o parte de ella) copiada literalmente "
            "del texto de la web que lo demuestra. Texto vacío si cumple es 'no'."
        )
    )

# modelo anidado (usa un formulario dentro de otro formulario):
class ValoracionPrimeraImpresion(BaseModel):
    que_ofrecen: Criterio = Field(description="¿Queda claro qué servicios o productos ofrece el negocio?")
    para_quien: Criterio = Field(
        description=(
            "¿Queda claro a qué tipo de clientes se dirige? Es 'si' si nombra algún tipo de cliente, "
            "aunque sea amplio (por ejemplo: 'niños y adultos', 'familias', 'empresas', 'deportistas'). "
            "Es 'parcialmente' si solo se deduce de forma indirecta, y 'no' si no hay ninguna pista."
        )
    )
    donde: Criterio = Field(description="¿Queda claro en qué zona o ciudad trabaja?")
    propuesta_de_valor: Criterio = Field(description="¿Explica por qué elegirlo a él y no a otro? Solo es 'si' si dice algo concreto y "
            "diferenciador: una especialidad poco común, un horario, una garantía, un precio o un "
            "dato comprobable. Las frases genéricas que podría decir cualquier negocio ('calidad', "
            "'confianza', 'experiencia', 'atención personalizada') son como mucho 'parcialmente'.")



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





INSTRUCCIONES = """Eres un experto en marketing local que revisa la primera impresión de la web de un negocio.
Recibirás el título, la descripción, los titulares y los primeros párrafos de la portada: es lo único que ve un visitante en los primeros segundos.

Reglas:
- Valora solo con lo que aparece en ese texto. No uses lo que sepas del negocio por otras fuentes.
- En "prueba" copia una frase literal del texto, sin cambiarla. Si no hay ninguna, déjalo vacío.
- Si algo solo se insinúa, responde "parcialmente": no lo des por claro.
- Si no aparece, responde "no"."""


def formatear_impresion(impresion: dict) -> str:
    titulo = impresion["titulo"]
    descripcion = impresion["descripcion"]
    titulares = " | ".join(impresion["h1"])
    subtitulos = " | ".join(impresion["subtitulos"])
    parrafos = "\n".join(impresion["parrafos"])
    return (
        f"TÍTULO DE LA PÁGINA: {titulo}\n"
        f"DESCRIPCIÓN: {descripcion}\n"
        f"TITULAR PRINCIPAL: {titulares}\n"
        f"SUBTÍTULOS: {subtitulos}\n"
        f"PRIMEROS PÁRRAFOS:\n{parrafos}"
    )


def valorar_primera_impresion(impresion: dict) -> ValoracionPrimeraImpresion:   # ValoracionPrimeraImpresion es el formulario
    modelo = init_chat_model("openai:gpt-4.1-mini", temperature=0)
    valorador = modelo.with_structured_output(ValoracionPrimeraImpresion)
    mensajes = [
        SystemMessage(INSTRUCCIONES),
        HumanMessage(formatear_impresion(impresion)),
    ]
    return valorador.invoke(mensajes)  # lo que nos devuelve no es el modelo, es el valorador (que ya tiene dentro de el la respuesta del modelo pero esta vez con la estructura que le hemos pedido)






if __name__ == "__main__":
    load_dotenv()
    soup = descargar_html("https://clinicaceodent.es/")
    if soup is None:
        print("No se pudo descargar la web")
    else:
        impresion = extraer_primera_impresion(soup)  # se convierte en un diccionario
        print(valorar_primera_impresion(impresion))