from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

MIN_SEDES = 2
MAX_SEDES = 10


class DatosLead(BaseModel):
    sector: Literal["salud", "estetica", "hosteleria", "educacion", "otro"] = Field(
        description="Sector del negocio"
    )
    numero_sedes: int | None = Field(
        description="Número de sedes o direcciones físicas distintas confirmadas; None si no está confirmado"
    )

    en_madrid: bool = Field(description="True si el negocio está en Madrid")
    intencion: Literal["alta", "media", "baja"] = Field(
        description=(
            "alta: pide auditoría, presupuesto o reunión; "
            "media: se interesa por un servicio concreto o descarga contenido específico; "
            "baja: acciones genéricas como suscribirse a la newsletter"
        )
    )

 

def puntuar(datos: DatosLead) -> int:
    if not datos.en_madrid:  # Si no está en Madrid devuelve 0, aquí ya decimos que los negocios de fuera de Madrid no nos interesan.
        return 0
    puntos = 0
    if datos.sector != "otro":
        puntos += 3
    if datos.en_madrid:  # Esta parte ahora se cumple siempre porque hasta aquí solo llegan los que si son de Madrid. Los que no lo son se han ido en el primer if.
        puntos += 2  
    if datos.numero_sedes is not None and MIN_SEDES <= datos.numero_sedes <= MAX_SEDES:
        puntos += 2
    puntos += {"alta": 3, "media": 2, "baja": 0}[datos.intencion]
    return puntos


def decidir(puntos: int) -> str:
    if puntos >= 8:
        return "contactar"
    if puntos >= 5:
        return "nutrir"
    return "descartar"




if __name__ == "__main__":   # He metido todo lo de abajo en este if para que no se ejecute cada vez que llamo al archivo "evaluar_lead.py"
    modelo = init_chat_model("openai:gpt-4.1-mini", temperature=0)
    extractor = modelo.with_structured_output(DatosLead)

    leads = [
        "Clínica dental en Madrid con 3 sedes que ha descargado nuestra guía de SEO local.",
        "Empresa de software de Barcelona con 200 empleados que pidió información sobre publicidad en LinkedIn.",
        "Academia de idiomas en Madrid con 1 sede que se suscribió a la newsletter.",
        "Cadena de 4 centros de estética en Madrid que solicitó una auditoría gratuita.",
    ]


    def crear_mensajes(lead: str) -> list:
        return [
            SystemMessage(
                "Extraes datos de leads para una agencia de marketing. "
                "No valores si el lead es bueno o malo: solo extrae la información que aparece en el texto."
            ),
            HumanMessage(f"Lead: {lead}"),
        ]


    resultados = extractor.batch([crear_mensajes(lead) for lead in leads])  # para cada lead de la lista, crea su conversación, y guárdalas todas en una lista nueva

    for lead, datos in zip(leads, resultados):
        puntos = puntuar(datos)
        accion = decidir(puntos)
        print(f"\n{lead}")
        print(f"  Datos: {datos}")
        print(f"  Puntuación: {puntos} → {accion}")