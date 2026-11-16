
import chromadb


COLLECTION_NAME = "tracepilot_retrieval_evaluation"
TOP_K = 3


# Synthetic benchmark incidents.
INCIDENTS = [
    {
        "id": "SYN-EVAL-001",
        "document": (
            "The application cannot connect to the SQL database. "
            "Database connection attempts are timing out."
        ),
        "metadata": {"category": "Database"},
    },
    {
        "id": "SYN-EVAL-002",
        "document": (
            "Users cannot log in because authentication requests "
            "are failing with invalid credentials."
        ),
        "metadata": {"category": "Authentication"},
    },
    {
        "id": "SYN-EVAL-003",
        "document": (
            "File uploads are failing because the application "
            "cannot write files to the storage directory."
        ),
        "metadata": {"category": "File Storage"},
    },
    {
        "id": "SYN-EVAL-004",
        "document": (
            "The API service is unavailable. Requests are returning "
            "HTTP 503 Service Unavailable errors."
        ),
        "metadata": {"category": "API"},
    },
    {
        "id": "SYN-EVAL-005",
        "document": (
            "The scheduled background job is failing and "
            "reports execution errors."
        ),
        "metadata": {"category": "Scheduled Job"},
    },
]


# Queries deliberately use different wording from the documents.
EVALUATION_QUERIES = [
    {
        "query": "The system is unable to establish a connection with its database.",
        "expected_id": "SYN-EVAL-001",
    },
    {
        "query": "Employees are unable to sign in to their accounts.",
        "expected_id": "SYN-EVAL-002",
    },
    {
        "query": "Documents cannot be uploaded to the application.",
        "expected_id": "SYN-EVAL-003",
    },
    {
        "query": "The backend endpoint is returning service unavailable errors.",
        "expected_id": "SYN-EVAL-004",
    },
    {
        "query": "An automated task did not execute successfully.",
        "expected_id": "SYN-EVAL-005",
    },
]


def evaluate():
    # Use an isolated in-memory collection.
    client = chromadb.EphemeralClient()

    collection = client.create_collection(
        name=COLLECTION_NAME,
        configuration={
            "hnsw": {
                "space": "cosine"
            }
        },
    )

    try:
        # Index benchmark incidents.
        collection.add(
            ids=[incident["id"] for incident in INCIDENTS],
            documents=[
                incident["document"] for incident in INCIDENTS
            ],
            metadatas=[
                incident["metadata"] for incident in INCIDENTS
            ],
        )

        print(f"Indexed benchmark incidents: {collection.count()}")
        print(f"Retrieval limit: Top {TOP_K}\n")

        hits = 0
        reciprocal_ranks = []

        for test_case in EVALUATION_QUERIES:
            query = test_case["query"]
            expected_id = test_case["expected_id"]

            results = collection.query(
                query_texts=[query],
                n_results=TOP_K,
            )

            retrieved_ids = results["ids"][0]

            print(f"Query: {query}")
            print(f"Expected incident: {expected_id}")
            print(f"Retrieved incidents: {retrieved_ids}")

            if expected_id in retrieved_ids:
                rank = retrieved_ids.index(expected_id) + 1
                reciprocal_rank = 1 / rank

                hits += 1
                reciprocal_ranks.append(reciprocal_rank)

                print(f"Expected incident found at rank: {rank}")
            else:
                reciprocal_ranks.append(0)
                print("Expected incident not found in top 3.")

            print("-" * 65)

        hit_at_3 = hits / len(EVALUATION_QUERIES)

        mrr = (
            sum(reciprocal_ranks) / len(reciprocal_ranks)
        )

        print("\n========== EVALUATION RESULTS ==========")
        print(f"Total queries: {len(EVALUATION_QUERIES)}")
        print(f"Successful hits: {hits}")
        print(f"Hit@3: {hit_at_3:.2%}")
        print(f"MRR: {mrr:.4f}")
        print("========================================")

    finally:
        # Remove the temporary collection.
        client.delete_collection(name=COLLECTION_NAME)


if __name__ == "__main__":
    evaluate()
