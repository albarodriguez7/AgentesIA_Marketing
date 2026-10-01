from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

modelo = init_chat_model("openai:gpt-4.1-mini", temperature=0)

mensajes = [
    SystemMessage("Eres un analista de ventas muy exigente de una agencia de marketing que solo trabaja con empresas de software con más de 50 empleados y presupuesto de marketing superior a 5.000 euros al mes. Respondes siempre en español, de forma breve y directa."),
    HumanMessage("Tenemos un lead: una clínica dental en Madrid con 3 sedes que ha descargado nuestra guía de SEO local. ¿Es un buen lead? Justifícalo en 3 frases."),
]

respuesta = modelo.invoke(mensajes)

print(respuesta.content)