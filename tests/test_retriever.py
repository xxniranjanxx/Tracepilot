
import pytest

from app.rag import retriever


class FakeCollection:
    def __init__(self, count=1):
        self.record_count = count
        self.query_arguments = None

    def count(self):
        return self.record_count

    def query(self, **kwargs):
        self.query_arguments = kwargs

        return {
            "ids": [["SYN-001"]],
            "documents": [["Database connection timeout"]],
            "metadatas": [[
                {
                    "priority": "High",
                    "resolution_category": "Integration Failure",
                }
            ]],
            "distances": [[0.15]],
        }


def test_retrieve_incidents(monkeypatch):
    collection = FakeCollection()

    monkeypatch.setattr(
        retriever,
        "get_incident_collection",
        lambda: collection,
    )

    results = retriever.retrieve_incidents(
        query="Database connection is failing",
        top_k=3,
    )

    assert len(results) == 1
    assert results[0]["incident_id"] == "SYN-001"
    assert results[0]["metadata"]["priority"] == "High"
    assert results[0]["distance"] == 0.15


def test_retrieve_with_metadata_filters(monkeypatch):
    collection = FakeCollection()

    monkeypatch.setattr(
        retriever,
        "get_incident_collection",
        lambda: collection,
    )

    retriever.retrieve_incidents(
        query="Database connection failure",
        priority="High",
        resolution_category="Integration Failure",
    )

    assert collection.query_arguments["where"] == {
        "$and": [
            {"priority": "High"},
            {"resolution_category": "Integration Failure"},
        ]
    }


def test_retrieve_with_single_filter(monkeypatch):
    collection = FakeCollection()

    monkeypatch.setattr(
        retriever,
        "get_incident_collection",
        lambda: collection,
    )

    retriever.retrieve_incidents(
        query="Database connection failure",
        priority="High",
    )

    assert collection.query_arguments["where"] == {
        "priority": "High"
    }


def test_retrieve_from_empty_collection(monkeypatch):
    collection = FakeCollection(count=0)

    monkeypatch.setattr(
        retriever,
        "get_incident_collection",
        lambda: collection,
    )

    results = retriever.retrieve_incidents(
        query="Database connection failure"
    )

    assert results == []


def test_reject_empty_query():
    with pytest.raises(ValueError):
        retriever.retrieve_incidents("   ")


def test_reject_invalid_top_k():
    with pytest.raises(ValueError):
        retriever.retrieve_incidents(
            query="Database connection failure",
            top_k=0,
        )
