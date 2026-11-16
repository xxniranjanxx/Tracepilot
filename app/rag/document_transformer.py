
from langchain_core.documents import Document

from app.models.incident import Incident


def incident_to_document(incident: Incident) -> Document:
    """
    Convert a validated Incident into a LangChain Document.
    """

    page_content = f"""
    Incident: {incident.short_description}

    Description:
    {incident.description}

    Resolution:
    {incident.resolution_notes}

    Priority: {incident.priority.value}
    Resolution Category: {incident.resolution_category.value}
    """

    metadata = {
        "incident_id": incident.incident_id,
        "priority": incident.priority.value,
        "resolution_category": incident.resolution_category.value,
        "sla_breached": incident.sla_breached,
    }

    return Document(
        page_content=page_content.strip(),
        metadata=metadata
    )


def incidents_to_documents(
    incidents: list[Incident]
) -> list[Document]:
    """
    Convert multiple Incident objects into LangChain Documents.
    """

    return [
        incident_to_document(incident)
        for incident in incidents
    ]
