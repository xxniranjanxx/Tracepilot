
from app.db.database import Base, engine
from app.db import models

def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("TracePilot database initialized successfully.")


if __name__ == "__main__":
    initialize_database()
