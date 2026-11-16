
from pathlib import Path
from tempfile import TemporaryDirectory

import chromadb

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base
from app.db.models import IncidentRecord
from app.rag import incident_indexer


def main():
    # Create an isolated, in-memory SQLite database.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)

    try:
        with SessionLocal() as db:

            # Insert one synthetic incident.
            incident = IncidentRecord(
                incident_id="SYN-CHROMA-001",
                short_description="Database connection timeout",
                description=(
                    "The application cannot establish "
                    "a connection with the SQL database."
                ),
                resolution_notes=(
                    "Database service was restarted "
                    "and connectivity was restored."
                ),
                priority="High",
                resolution_category="Integration Failure",
                resolution_time_hours=1.5,
                sla_breached=False,
            )

            db.add(incident)
            db.commit()

            # Create a temporary, real ChromaDB database.
            with TemporaryDirectory() as temp_dir:

                client = chromadb.EphemeralClient()

                collection = client.get_or_create_collection(
                    name="tracepilot_integration_test",
                    configuration={
                        "hnsw": {"space": "cosine"}
                    },
                )

                # Route the indexer to our temporary collection.
                original_function = (
                    incident_indexer.get_incident_collection
                )

                incident_indexer.get_incident_collection = (
                    lambda: collection
                )

                try:
                    indexed_count = incident_indexer.index_incidents(db)
                finally:
                    incident_indexer.get_incident_collection = (
                        original_function
                    )

                print(f"Indexed incidents: {indexed_count}")

                # Verify that ChromaDB stored the document.
                assert indexed_count == 1
                assert collection.count() == 1

                # Search using different wording.
                results = collection.query(
                    query_texts=[
                        "The application cannot communicate "
                        "with the SQL server."
                    ],
                    n_results=1,
                )

                retrieved_id = results["ids"][0][0]

                print(f"Retrieved incident: {retrieved_id}")
                print(f"Retrieved document: {results['documents'][0][0]}")

                assert retrieved_id == "SYN-CHROMA-001"

                # Inspect the generated embedding.
                stored = collection.get(
                    ids=["SYN-CHROMA-001"],
                    include=["embeddings"],
                )

                embedding = stored["embeddings"][0]

                print(f"Embedding dimensions: {len(embedding)}")

                assert len(embedding) == 384

                print("\nChromaDB integration verification passed!")

    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


if __name__ == "__main__":
    main()
