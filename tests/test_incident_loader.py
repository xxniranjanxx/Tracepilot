
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base
from app.db.models import IncidentRecord
from app.rag.incident_loader import load_incidents_as_documents


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_load_incidents_as_documents(db_session):
    incident = IncidentRecord(
        incident_id="SYN-DB-001",
        short_description="SAP connection timeout",
        description="Automation failed while connecting to SAP.",
        resolution_notes="Restarted the SAP connection and retried.",
        priority="High",
        resolution_category="Integration Failure",
        resolution_time_hours=1.5,
        sla_breached=False,
    )

    db_session.add(incident)
    db_session.commit()

    documents = load_incidents_as_documents(db_session)

    assert len(documents) == 1
    assert documents[0].metadata["incident_id"] == "SYN-DB-001"
    assert documents[0].metadata["priority"] == "High"
    assert "SAP connection timeout" in documents[0].page_content


def test_load_documents_from_empty_database(db_session):
    documents = load_incidents_as_documents(db_session)

    assert documents == []
