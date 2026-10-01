from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from leads.evaluar_lead import DatosLead, puntuar, decidir
from compartido.herramientas import leer_web

load_dotenv()

INSTRUCCIONES = """Eres un investigador de leads para una agencia de marketing digital.
Tu trabajo es visitar la web de una empresa y averiguar su sector, si está en Madrid
y cuántas sedes tiene.

Cómo trabajar:
- Empieza leyendo la página principal con la herramienta leer_web.
- Si falta algún dato (por ejemplo, el número de sedes), visita otras páginas de la misma web
que probablemente lo contengan, eligiéndolas de la lista de enlaces que devuelve leer_web.
  Nunca inventes direcciones.
- No visites más de 4 páginas en total.
- No inventes datos: si después de buscar no encuentras algo, déjalo vacío.
- La intención la decides a partir de lo que el lead ha hecho con nosotros, no de su web."""

modelo = init_chat_model("openai:gpt-4.1-mini", temperature=0)

agente = create_agent(
    model=modelo,
    tools=[leer_web],
    system_prompt=INSTRUCCIONES,
    response_format=DatosLead,
)

if __name__ == "__main__":
    lead = "Web: https://clinicaceodent.es/. Ha descargado nuestra guía de SEO local."
    resultado = agente.invoke({"messages": [{"role": "user", "content": lead}]})

    for mensaje in resultado["messages"]:
        mensaje.pretty_print()

    datos = resultado["structured_response"]
    puntos = puntuar(datos)
    print(f"\nDatos: {datos}")
    print(f"Puntuación: {puntos} → {decidir(puntos)}")