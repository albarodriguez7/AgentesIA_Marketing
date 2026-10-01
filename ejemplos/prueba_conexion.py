import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

print("¿Clave encontrada?", os.getenv("OPENAI_API_KEY") is not None)

modelo = init_chat_model("openai:gpt-4.1-mini", temperature=0)

respuesta = modelo.invoke("Explica en una frase qué es un lead en marketing.")

print(respuesta.content)

print(respuesta.usage_metadata)