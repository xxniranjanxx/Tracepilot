
from langchain_core.documents import Document

from app.rag import incident_indexer


class FakeCollection:
    def __init__(self):
        self.upserted_data = None

    def upsert(self, ids, documents, metadatas):
        self.upserted_data = {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
        }


def test_index_incidents(monkeypatch):
    fake_collection = FakeCollection()

    documents = [
        Document(
            page_content="Database connection timeout",
            metadata={
                "incident_id": "SYN-001",
                "priority": "High",
                "sla_breached": None,
            },
        )
    ]

    monkeypatch.setattr(
        incident_indexer,
        "load_incidents_as_documents",
        lambda db: documents,
    )

    monkeypatch.setattr(
        incident_indexer,
        "get_incident_collection",
        lambda: fake_collection,
    )

    result = incident_indexer.index_incidents(db=None)

    assert result == 1
    assert fake_collection.upserted_data["ids"] == ["SYN-001"]

    # None metadata values should be excluded.
    assert fake_collection.upserted_data["metadatas"] == [
        {
            "incident_id": "SYN-001",
            "priority": "High",
        }
    ]


def test_index_empty_incidents(monkeypatch):
    monkeypatch.setattr(
        incident_indexer,
        "load_incidents_as_documents",
        lambda db: [],
    )

    result = incident_indexer.index_incidents(db=None)

    assert result == 0
