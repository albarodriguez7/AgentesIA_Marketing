from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

from auditoria.evaluaciones.evaluar_primera_impresion import (
    INSTRUCCIONES_JUEZ,
    JuicioPrimeraImpresion,
    formatear_para_juez,
)

load_dotenv()

VACIO = {"cumple": "no", "prueba": ""}

# (nombre del caso, prueba de para_quien, respuesta correcta del juez)
CASOS = [
    ("Viena", "En colaboración con la CorAvant, apoyamos a las personas que viven con una cardiopatía .", False),
    ("La Bola", "En pleno centro, a un paso del Palacio Real.", False),
    ("CeoDent", "Especialistas en odontología integral para niños y adultos", True),
]

juez = init_chat_model("openai:gpt-4.1", temperature=0).with_structured_output(JuicioPrimeraImpresion)

for nombre, prueba, esperado in CASOS:
    valoracion = {
        "que_ofrecen": VACIO,
        "para_quien": {"cumple": "parcialmente", "prueba": prueba},
        "donde": VACIO,
        "propuesta_de_valor": VACIO,
    }
    juicio = juez.invoke([
        SystemMessage(INSTRUCCIONES_JUEZ),
        HumanMessage(formatear_para_juez(valoracion)),
    ])
    veredicto = juicio.para_quien
    marca = "✅" if veredicto.prueba_pertinente == esperado else "❌"
    print(f"{marca} {nombre}: pertinente = {veredicto.prueba_pertinente} (esperado {esperado})")
    print(f"   {veredicto.razonamiento}\n")