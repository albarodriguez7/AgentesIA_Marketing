from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

NOMBRE_DATASET = "leads-cualificacion"

ejemplos = [
    {
        "inputs": {"lead": "Web: https://clinicaceodent.es/. Ha pedido una auditoría gratuita."},
        "outputs": {"sector": "salud", "en_madrid": True, "tramo_sedes": "1", "accion": "contactar"},
    },
    {
        "inputs": {"lead": "Web: https://www.fitnesspark.es/. Se ha suscrito a nuestra newsletter."},
        "outputs": {"sector": "otro", "en_madrid": True, "tramo_sedes": "mas de 10", "accion": "descartar"},
    },
    {
        "inputs": {"lead": "Web: https://www.grupodentalcibeles.es/. Ha descargado nuestra guía de SEO local."},
        "outputs": {"sector": "salud", "en_madrid": True, "tramo_sedes": "2 a 10", "accion": "contactar"},
    },
    {
        "inputs": {"lead": "Web: https://www.bcnlanguages.com/. Ha pedido una auditoría gratuita."},
        "outputs": {"sector": "educacion", "en_madrid": False, "tramo_sedes": "2 a 10", "accion": "descartar"},
    },
    {
        "inputs": {"lead": "Web: https://www.pizzavk.com/. Ha descargado nuestra guía de SEO local."},
        "outputs": {"sector": "hosteleria", "en_madrid": True, "tramo_sedes": "1", "accion": "nutrir"},
    },
    {
        "inputs": {"lead": "Web: https://fisioterapiadomiciliomanuel.com/. Se ha suscrito a nuestra newsletter."},
        "outputs": {"sector": "salud", "en_madrid": True, "tramo_sedes": "1", "accion": "nutrir"},
    },
]

cliente = Client()
dataset = cliente.create_dataset(
    dataset_name=NOMBRE_DATASET,
    description="Leads reales con la respuesta correcta comprobada a mano",
)
cliente.create_examples(dataset_id=dataset.id, examples=ejemplos)

print(f"Dataset '{NOMBRE_DATASET}' creado con {len(ejemplos)} ejemplos.")