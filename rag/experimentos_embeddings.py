from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()

modelo = OpenAIEmbeddings(model="text-embedding-3-small")


def similitud(a: list, b: list) -> float:
    producto = sum(x * y for x, y in zip(a, b))
    largo_a = sum(x * x for x in a) ** 0.5
    largo_b = sum(y * y for y in b) ** 0.5
    return producto / (largo_a * largo_b)


base = "La web no tiene aviso legal"
otras = [
    "Falta la política de privacidad",
    "No se sabe quién es el dueño de la web ni su NIF",
    "El teléfono no se puede pulsar desde el móvil",
    "Receta de tortilla de patatas",
    "La web tiene aviso legal",
]

vector_base = modelo.embed_query(base)
vectores_otras = modelo.embed_documents(otras)

print(f"Comparando con: «{base}»\n")
for texto, vector in zip(otras, vectores_otras):
    print(f"{similitud(vector_base, vector):.3f}  {texto}")