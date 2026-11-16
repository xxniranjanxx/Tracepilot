
from app.rag.vector_store import get_incident_collection


def retrieve_incidents(
    query: str,
    top_k: int = 3,
    priority: str | None = None,
    resolution_category: str | None = None,
) -> list[dict]:
    """
    Retrieve semantically similar incidents from ChromaDB.

    Optional metadata filters can narrow the search by priority
    and resolution category.
    """
    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    collection = get_incident_collection()

    total_records = collection.count()

    if total_records == 0:
        return []

    # Build ChromaDB metadata filters.
    filters = []

    if priority is not None:
        filters.append({"priority": priority})

    if resolution_category is not None:
        filters.append({"resolution_category": resolution_category})

    where = None

    if len(filters) == 1:
        where = filters[0]
    elif len(filters) > 1:
        where = {"$and": filters}

    # Do not request more results than the collection contains.
    results = collection.query(
        query_texts=[query],
        n_results=min(top_k, total_records),
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    retrieved_incidents = []

    for index, incident_id in enumerate(results["ids"][0]):
        retrieved_incidents.append(
            {
                "incident_id": incident_id,
                "document": results["documents"][0][index],
                "metadata": results["metadatas"][0][index],
                "distance": results["distances"][0][index],
            }
        )

    return retrieved_incidents
