from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langgraph.graph.message import add_messages

from evaluar_lead import DatosLead, puntuar, decidir
from herramientas import leer_web

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()


class EstadoLead(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]    # Es como decir: esta casilla es una lista de mensajes, y cuando alguien escriba en ella, añade al final en vez de borrar
    datos: DatosLead | None
    puntos: int | None
    accion: str | None

# Annotated[tipo, regla] es la forma de Python de decir "este campo es de este tipo, y además lleva esta regla adjunta"
# AnyMessage significa "cualquier tipo de mensaje": de sistema, humano, de la IA o de una herramienta.



INSTRUCCIONES_INVESTIGAR = """Eres un investigador de leads para una agencia de marketing digital.
Tu trabajo es visitar la web de una empresa y averiguar su sector, dónde está y cuántas sedes tiene.

Cómo trabajar:
- Empieza leyendo la página principal con la herramienta leer_web.
- Si falta algún dato, visita otras páginas eligiéndolas de la lista de enlaces que devuelve leer_web.
  Nunca inventes direcciones.
- No visites más de 4 páginas en total.
- Cuando tengas suficiente información, responde con un resumen breve de lo que has averiguado."""

modelo = init_chat_model("openai:gpt-4.1-mini", temperature=0)
modelo_con_herramientas = modelo.bind_tools([leer_web])   # esto le presenta la herramienta a la IA, pero no la ejecuta, solo se la enseña


def investigar(estado: EstadoLead) -> dict:
    mensajes = [SystemMessage(INSTRUCCIONES_INVESTIGAR)] + estado["messages"]
    respuesta = modelo_con_herramientas.invoke(mensajes)
    return {"messages": [respuesta]}    # como "messages" tiene "add_messages", la respuesta se añadirá al final de la conversación



# Extraer
INSTRUCCIONES_EXTRAER = """Extraes datos de leads para una agencia de marketing.
No valores si el lead es bueno o malo: solo extrae la información.
Si un dato no aparece claramente en la investigación, déjalo vacío.
La intención se decide por lo que el lead ha hecho con nosotros, no por su web."""

extractor = modelo.with_structured_output(DatosLead)


def extraer(estado: EstadoLead) -> dict:
    lead_original = estado["messages"][0].content  # Lee el primer mensaje
    resumen = estado["messages"][-1].content   # Lee el ultimo mensaje, que es un resumen
    datos = extractor.invoke([
        SystemMessage(INSTRUCCIONES_EXTRAER),
        HumanMessage(f"Mensaje del lead:\n{lead_original}\n\nInvestigación:\n{resumen}"),
    ])
    return {"datos": datos}


def calcular_puntuacion(estado: EstadoLead) -> dict:
    puntos = puntuar(estado["datos"])
    return {"puntos": puntos, "accion": decidir(puntos)}



# Creo el nodo de herramientas
nodo_herramientas = ToolNode([leer_web])

constructor = StateGraph(EstadoLead)
constructor.add_node("investigar", investigar)   # add_node("nombre", función). / Esos nombres son los que se verán luego en LangSmith, en lugar de "model" y "tools"
constructor.add_node("herramientas", nodo_herramientas)
constructor.add_node("extraer", extraer)
constructor.add_node("puntuar", calcular_puntuacion)

constructor.add_edge(START, "investigar") # Le digo que empieze (START) con investigar
constructor.add_conditional_edges("investigar", tools_condition, {"tools": "herramientas", END: "extraer"})   # Si "tools_condition" es Si, devuelve "tools" sino devuelve extraer
constructor.add_edge("herramientas", "investigar")   # Crea el bucle: después de ejecutar la herramienta, siempre se vuelve a investigar, para que la IA lea el resultado y decida qué hacer
constructor.add_edge("extraer", "puntuar")   # Después de extraer siempre se puntúa
constructor.add_edge("puntuar", END)   # y después de puntuar siempre se termina

agente = constructor.compile()



# START → investigar ⇄ herramientas
#             ↓ (cuando ya no pide herramientas)
#          extraer → puntuar → END  
         





if __name__ == "__main__":
    resultado = agente.invoke({
        "messages": [HumanMessage("Web: https://clinicaceodent.es/. Ha descargado nuestra guía de SEO local.")],
        "datos": None,
        "puntos": None,
        "accion": None,
    })

    for mensaje in resultado["messages"]:
        for peticion in getattr(mensaje, "tool_calls", []):    # getattr significa "dame tool_calls si existe y, si no, una lista vacía"
            print("Visita:", peticion["args"]["url"])

    print("\nDatos:", resultado["datos"])
    print(f"Puntuación: {resultado['puntos']} → {resultado['accion']}")