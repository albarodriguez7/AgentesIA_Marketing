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
            "del texto de la web que demuestra ESTE criterio concreto. No uses una frase que hable "
            "de otra cosa. Texto vacío si cumple es 'no'."
        )
    )

# modelo anidado (usa un formulario dentro de otro formulario):
class ValoracionPrimeraImpresion(BaseModel):
    que_ofrecen: Criterio = Field(
        description=(
            "¿Queda claro qué ofrece el negocio? Es 'si' si nombra sus servicios o productos "
            "principales (por ejemplo: 'implantes y ortodoncia', 'pizzas a domicilio', 'cortes y mechas'). "
            "Es 'parcialmente' si solo dice el tipo de negocio ('pizzería', 'peluquería'). "
            "Es 'no' si no se sabe a qué se dedica."
        )
    )
    para_quien: Criterio = Field(
    description=(
        "¿Queda claro a qué tipo de clientes se dirige? Es 'si' si nombra algún tipo de cliente, "
        "aunque sea amplio (por ejemplo: 'niños y adultos', 'familias', 'empresas', 'deportistas'). "
        "Es 'parcialmente' si describe la situación o necesidad de sus clientes sin nombrar un tipo "
        "(por ejemplo: 'si vuelves a entrenar después de una lesión'). "
        "Es 'no' si ninguna frase habla de sus clientes. Las frases genéricas que valen para cualquier "
        "negocio ('para ti', 'tu mejor versión'), las que dicen que es para todo el mundo "
        "('para todos', 'for everyone') y las frases sobre servicios, ubicación, filosofía "
        "o causas solidarias NO cuentan: en ese caso es 'no'."
        )
    )
    donde: Criterio = Field(
        description=(
            "¿Queda claro dónde está? Es 'si' si da la dirección o el barrio junto con la ciudad "
            "(por ejemplo: 'Hortaleza, Madrid'). Es 'parcialmente' si solo da el barrio o solo la ciudad. "
            "Es 'no' si no aparece ninguna ubicación."
        )
    )
    propuesta_de_valor: Criterio = Field(description="¿Explica por qué elegirlo a él y no a otro? Solo es 'si' si dice algo concreto y "
            "diferenciador: una especialidad poco común, un horario, una garantía, un precio o un "
            "dato comprobable. Las frases genéricas que podría decir cualquier negocio ('calidad', "
            "'confianza', 'experiencia', 'atención personalizada') son como mucho 'parcialmente'.")




def normalizar(texto: str) -> str:
    return " ".join(texto.lower().split())


def prueba_es_valida(criterio: Criterio, texto: str) -> bool:
    if criterio.cumple == "no":
        return True
    if criterio.prueba == "":
        return False
    return normalizar(criterio.prueba) in normalizar(texto)
    # Es como poner: 
    # if normalizar(criterio.prueba) in normalizar(texto):
    #     return True
    # else:
    #     return False


def criterios_sin_prueba_valida(valoracion: ValoracionPrimeraImpresion, texto: str) -> list:
    sin_prueba = []
    for nombre, criterio in valoracion:
        if not prueba_es_valida(criterio, texto):
            sin_prueba.append(nombre)
    return sin_prueba




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
- Si no aparece, responde "no".
- Si ninguna frase responde de verdad a un criterio, responde "no". Es mejor un "no" honesto que un "parcialmente" con una prueba que habla de otra cosa.
"""


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






WEBS_DE_PRUEBA = [
    "https://www.trainingboutique.es/",
    "https://www.viena.es/es/",
    "https://www.labola.es/es",
    "https://clinicaceodent.es/",
    "https://www.kidsandus.es/es",
]

if __name__ == "__main__":
    load_dotenv()
    for url in WEBS_DE_PRUEBA:
        print(f"\n=== {url} ===")
        soup = descargar_html(url)
        if soup is None:
            print("No se pudo descargar la web")
            continue

        impresion = extraer_primera_impresion(soup)
        texto = formatear_impresion(impresion)
        valoracion = valorar_primera_impresion(impresion)

        for nombre, criterio in valoracion:
            print(f"{nombre}: {criterio.cumple} → {criterio.prueba}")

        sin_prueba = criterios_sin_prueba_valida(valoracion, texto)
        if sin_prueba:
            print("⚠️ Pruebas que no aparecen en la web:", sin_prueba)
        else:
            print("✅ Todas las pruebas aparecen en la web")