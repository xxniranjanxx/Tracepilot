
from app.models.incident import Incident, Priority, ResolutionCategory
from app.rag.document_transformer import (
    incident_to_document,
    incidents_to_documents,
)


def sample_incident():
    return Incident(
        incident_id="SYN-RAG-001",
        short_description="SAP connection timeout",
        description="Automation failed while connecting to SAP.",
        resolution_notes="Restarted the SAP connection and retried.",
        priority=Priority.HIGH,
        resolution_category=ResolutionCategory.INTEGRATION_FAILURE,
        resolution_time_hours=1.5,
        sla_breached=False,
    )


def test_incident_to_document():
    incident = sample_incident()

    document = incident_to_document(incident)

    assert "SAP connection timeout" in document.page_content
    assert "Restarted the SAP connection" in document.page_content

    assert document.metadata["incident_id"] == "SYN-RAG-001"
    assert document.metadata["priority"] == "High"
    assert document.metadata["resolution_category"] == "Integration Failure"


def test_incidents_to_documents():
    incident1 = sample_incident()

    incident2 = sample_incident().model_copy(
        update={"incident_id": "SYN-RAG-002"}
    )

    documents = incidents_to_documents([incident1, incident2])

    assert len(documents) == 2
    assert documents[0].metadata["incident_id"] == "SYN-RAG-001"
    assert documents[1].metadata["incident_id"] == "SYN-RAG-002"


def test_empty_incident_list():
    documents = incidents_to_documents([])

    assert documents == []
