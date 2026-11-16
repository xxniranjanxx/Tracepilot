
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import IncidentRecord
from app.models.incident import Incident
from app.rag.document_transformer import incidents_to_documents


def load_incidents_as_documents(db: Session):
    """
    Retrieve incidents from SQLite and convert them
    into LangChain Documents.
    """

    statement = select(IncidentRecord).order_by(IncidentRecord.id)

    records = db.scalars(statement).all()

    incidents = [
        Incident(
            incident_id=record.incident_id,
            short_description=record.short_description,
            description=record.description,
            resolution_notes=record.resolution_notes,
            priority=record.priority,
            resolution_category=record.resolution_category,
            resolution_time_hours=record.resolution_time_hours,
            sla_breached=record.sla_breached,
        )
        for record in records
    ]

    return incidents_to_documents(incidents)
