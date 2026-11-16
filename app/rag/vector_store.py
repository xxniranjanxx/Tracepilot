
from pathlib import Path

import chromadb


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHROMA_DB_DIR = PROJECT_ROOT / "data" / "chroma"

COLLECTION_NAME = "incident_records"


def get_chroma_client():
    """Create a persistent ChromaDB client."""
    return chromadb.PersistentClient(
        path=str(CHROMA_DB_DIR)
    )


def get_incident_collection():
    """Get or create the incident vector collection."""
    client = get_chroma_client()

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        configuration={
            "hnsw": {
                "space": "cosine"
            }
        },
    )

    return collection
