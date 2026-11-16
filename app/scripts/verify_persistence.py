
import sys

from app.rag.vector_store import get_incident_collection


INCIDENT_ID = "SYN-PERSIST-001"


def write_test():
    collection = get_incident_collection()

    collection.upsert(
        ids=[INCIDENT_ID],
        documents=[
            "Application cannot connect to the SQL database. "
            "The database connection is timing out."
        ],
        metadatas=[
            {
                "priority": "High",
                "resolution_category": "Integration Failure",
            }
        ],
    )

    print("Incident indexed successfully.")
    print(f"Collection record count: {collection.count()}")


def read_test():
    collection = get_incident_collection()

    results = collection.query(
        query_texts=[
            "Database connectivity failure"
        ],
        n_results=1,
    )

    assert results["ids"][0][0] == INCIDENT_ID

    print("Incident retrieved after process restart.")
    print(f"Retrieved ID: {results['ids'][0][0]}")
    print(f"Document: {results['documents'][0][0]}")
    print(f"Collection record count: {collection.count()}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: verify_persistence.py [write|read]")

    mode = sys.argv[1]

    if mode == "write":
        write_test()
    elif mode == "read":
        read_test()
    else:
        raise SystemExit("Mode must be 'write' or 'read'")
