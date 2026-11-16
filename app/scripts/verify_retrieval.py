
from app.rag.retriever import retrieve_incidents


def main():
    query = "The application is unable to connect to its SQL database because requests are timing out."

    print("\n--- Semantic retrieval ---")

    results = retrieve_incidents(
        query=query,
        top_k=3,
    )

    for result in results:
        print(f"\nIncident ID: {result['incident_id']}")
        print(f"Document: {result['document']}")
        print(f"Metadata: {result['metadata']}")
        print(f"Cosine distance: {result['distance']:.4f}")

    assert results, "No incidents were retrieved."

    print("\n--- High-priority filter ---")

    high_priority_results = retrieve_incidents(
        query=query,
        top_k=3,
        priority="High",
    )

    for result in high_priority_results:
        print(
            f"{result['incident_id']} - "
            f"{result['metadata']['priority']}"
        )

    assert all(
        result["metadata"]["priority"] == "High"
        for result in high_priority_results
    )

    print("\n--- Resolution-category filter ---")

    category_results = retrieve_incidents(
        query=query,
        top_k=3,
        resolution_category="Integration Failure",
    )

    for result in category_results:
        print(
            f"{result['incident_id']} - "
            f"{result['metadata']['resolution_category']}"
        )

    assert all(
        result["metadata"]["resolution_category"] == "Integration Failure"
        for result in category_results
    )

    print("\nRetrieval verification passed!")


if __name__ == "__main__":
    main()
