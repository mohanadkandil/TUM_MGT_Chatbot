from weaviate import Client, auth
import os
import application.backend.datastore.collections.main.schema as main_schema
from dotenv import find_dotenv, load_dotenv
import weaviate

load_dotenv(find_dotenv())
# Stellen Sie sicher, dass die Umgebungsvariablen WEAVIATE_URL und WEAVIATE_API_KEY korrekt gesetzt sind
weaviate_url = os.getenv("WCS_URL")  # URL Ihrer Weaviate-Instanz
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")  # Ihr Weaviate-API-Schlüssel
openai_api_key = os.getenv("OPENAI_API_KEY")  # Ihr OpenAI-API-Schlüssel
# Authentifizierung (falls notwendig)


from application.backend.datastore.db import ChatbotVectorDatabase

chatvec = ChatbotVectorDatabase()

res = chatvec.main.search(
    query="What do I have to consider when handing in my thesis?",
    k=5,
    degree_programs="BMT",
)

for hit in res:
    print(hit)
    print(hit.text.replace("\n", " "))
    print(hit.title)
    print(hit.url)
    print(hit.subtopic)
