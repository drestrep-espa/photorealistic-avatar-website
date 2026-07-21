import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

PDF_PATH = "data/02-NNUU_PGOU_BOADILLA_2017_COMPLETO.pdf"

vector_store = client.vector_stores.create(name="normativa-boadilla")
print("vector store id:", vector_store.id)

with open(PDF_PATH, "rb") as f:
    result = client.vector_stores.files.upload_and_poll(
        vector_store_id=vector_store.id,
        file=f,
    )

print("file id:", result.id)
print("status:", result.status)
