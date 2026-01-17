# --- SQLite fix for Azure App Service ---
import sys
import pysqlite3
sys.modules["sqlite3"] = pysqlite3
# --------------------------------------

import os
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from dotenv import load_dotenv
import uuid

load_dotenv()
client = OpenAI()


# -------------------------
# FORCE PERSIST DIRECTORY
# -------------------------
PERSIST_PATH = "vector_db_store"
os.makedirs(PERSIST_PATH, exist_ok=True)

COLLECTION_NAME = "company_knowledge"

openai_client = OpenAI()

# -------------------------
# SINGLE PERSISTENT CLIENT
# -------------------------
chroma_client = chromadb.Client(
    Settings(
        persist_directory=PERSIST_PATH,
        anonymized_telemetry=False
    )
)

# -------------------------
# EMBEDDINGS
# -------------------------
def embed_text(text: str):
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# -------------------------
# INGESTION (RUN ONCE)
# -------------------------
def load_company_docs(folder_path: str):
    # FORCE CREATE COLLECTION
    collections = [c.name for c in chroma_client.list_collections()]

    if COLLECTION_NAME not in collections:
        collection = chroma_client.create_collection(
            name=COLLECTION_NAME
        )
        print("✅ Created new Chroma collection")
    else:
        collection = chroma_client.get_collection(
            name=COLLECTION_NAME
        )
        print("ℹ️ Using existing Chroma collection")

    files_loaded = 0

    for filename in os.listdir(folder_path):
        if not filename.endswith(".md"):
            continue

        filepath = os.path.join(folder_path, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            continue

        collection.add(
            documents=[content],
            embeddings=[embed_text(content)],
            ids=[filename]
        )

        files_loaded += 1

    print(f"✅ Loaded {files_loaded} company document(s)")
    print(f"📂 Vector DB path: {PERSIST_PATH}")

# -------------------------
# QUERY
# -------------------------
from chromadb.errors import NotFoundError

def query_company_knowledge(query: str, top_k: int = 3) -> str:
    try:
        collection = chroma_client.get_collection(
            name=COLLECTION_NAME
        )
    except NotFoundError:
        # Collection not created yet (safe fallback)
        print("⚠️ Vector DB collection not found. Returning empty context.")
        return ""

    results = collection.query(
        query_embeddings=[embed_text(query)],
        n_results=top_k
    )

    print("DEBUG: Retrieved documents:", results["documents"])

    if not results["documents"] or not results["documents"][0]:
        return ""

    return "\n".join(results["documents"][0])



def ensure_company_knowledge_loaded(folder_path: str):
    """
    Ensures the company knowledge collection exists and is populated.
    Safe to call multiple times.
    """
    try:
        collection = chroma_client.get_collection(name=COLLECTION_NAME)
        count = collection.count()

        if count == 0:
            print("ℹ️ Vector DB collection empty. Loading company knowledge...")
            load_company_docs(folder_path)
        else:
            print(f"✅ Vector DB ready. Documents count: {count}")

    except Exception:
        print("ℹ️ Vector DB collection missing. Creating and loading knowledge...")
        load_company_docs(folder_path)
