
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import IncidentRecord
from app.models.incident import Incident, IncidentUpdate

app = FastAPI(
    title="TracePilot API",
    description="AI-powered RPA Incident Response and Troubleshooting",
    version="0.3.0"
)


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "service": "tracepilot"
    }


def serialize_incident(incident: IncidentRecord):
    return {
        "id": incident.id,
        "incident_id": incident.incident_id,
        "short_description": incident.short_description,
        "description": incident.description,
        "resolution_notes": incident.resolution_notes,
        "priority": incident.priority,
        "resolution_category": incident.resolution_category,
        "resolution_time_hours": incident.resolution_time_hours,
        "sla_breached": incident.sla_breached
    }


@app.post(
    "/incidents",
    tags=["Incidents"],
    status_code=status.HTTP_201_CREATED
)
def create_incident(
    incident: Incident,
    db: Session = Depends(get_db)
):
    db_incident = IncidentRecord(
        **incident.model_dump(mode="json")
    )

    try:
        db.add(db_incident)
        db.commit()
        db.refresh(db_incident)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An incident with this ID already exists."
        )

    return {
        "message": "Incident saved successfully",
        "incident": serialize_incident(db_incident)
    }


@app.get("/incidents", tags=["Incidents"])
def get_incidents(db: Session = Depends(get_db)):
    statement = select(IncidentRecord).order_by(
        IncidentRecord.id.desc()
    )

    incidents = db.scalars(statement).all()

    return {
        "total": len(incidents),
        "incidents": [
            serialize_incident(incident)
            for incident in incidents
        ]
    }


@app.patch("/incidents/{incident_id}", tags=["Incidents"])
def update_incident(
    incident_id: str,
    updates: IncidentUpdate,
    db: Session = Depends(get_db)
):
    # Find the incident
    statement = select(IncidentRecord).where(
        IncidentRecord.incident_id == incident_id
    )

    incident = db.scalar(statement)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    # Extract only fields provided by the client
    update_data = updates.model_dump(exclude_unset=True)

    # Apply the changes
    for field, value in update_data.items():
        setattr(incident, field, value)

    # Save changes
    db.commit()
    db.refresh(incident)

    return {
        "message": "Incident updated successfully",
        "incident": serialize_incident(incident)
    }

@app.delete("/incidents/{incident_id}", status_code=204, tags=["Incidents"])
def delete_incident(
    incident_id: str,
    db: Session = Depends(get_db)
):
    statement = select(IncidentRecord).where(
        IncidentRecord.incident_id == incident_id
    )

    incident = db.scalar(statement)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    db.delete(incident)
    db.commit()

    return None
