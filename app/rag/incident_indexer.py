
from sqlalchemy.orm import Session

from app.rag.incident_loader import load_incidents_as_documents
from app.rag.vector_store import get_incident_collection


def index_incidents(db: Session) -> int:
    """
    Load incidents from SQLite and index them in ChromaDB.

    Returns the number of indexed documents.
    """
    documents = load_incidents_as_documents(db)

    if not documents:
        return 0

    collection = get_incident_collection()

    ids = [
        document.metadata["incident_id"]
        for document in documents
    ]

    contents = [
        document.page_content
        for document in documents
    ]

    # ChromaDB does not accept None as a metadata value.
    metadatas = [
        {
            key: value
            for key, value in document.metadata.items()
            if value is not None
        }
        for document in documents
    ]

    # Upsert creates new records or updates existing ones.
    collection.upsert(
        ids=ids,
        documents=contents,
        metadatas=metadatas,
    )

    return len(documents)
