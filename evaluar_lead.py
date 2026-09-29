from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()


class EvaluacionLead(BaseModel):
    puntuacion: int = Field(description="Puntuación del lead de 0 a 10 según el perfil de cliente ideal")
    encaja_con_icp: bool = Field(description="True si el lead encaja con el perfil de cliente ideal")
    motivos: list[str] = Field(description="Entre 2 y 4 motivos breves que justifican la puntuación")
    siguiente_accion: Literal["contactar", "nutrir", "descartar"] = Field(
        description="contactar si es un buen lead ya, nutrir si encaja pero aún no está listo, descartar si no encaja"
    )

# ICP: el perfil de cliente ideal
ICP = """Agencia de marketing digital especializada en captación para negocios locales de Madrid.
Cliente ideal: negocios de servicios (salud, estética, hostelería, educación) con 2 o más sedes,
que ya muestran interés por el marketing digital."""

modelo = init_chat_model("openai:gpt-4.1-mini", temperature=0)
evaluador = modelo.with_structured_output(EvaluacionLead)

mensajes = [
    SystemMessage(f"Eres un analista de marketing que cualifica leads. Evalúa cada lead según este perfil de cliente ideal:\n{ICP}"),
    HumanMessage("Lead: clínica dental en Madrid con 3 sedes que ha descargado nuestra guía de SEO local."),
]

resultado = evaluador.invoke(mensajes)

print(resultado)
print("Puntuación:", resultado.puntuacion)
print("Acción:", resultado.siguiente_accion)