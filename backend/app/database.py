import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- Database Setup ---
# We'll get the database URL from environment variables for flexibility.
# It defaults to a local SQLite database for easy development, just like in xecution.ai.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./clarity_pixel.db")

# The 'engine' is the core interface to the database.
# For SQLite, we need to add a special argument `check_same_thread`.
# This isn't needed for PostgreSQL but doesn't hurt.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

# The SessionLocal class is our "session factory." When we call it, it creates a new database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is our dependency generator. It's the "plumbing" that provides a database
# session to our API endpoints and ensures it's always closed correctly afterward.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()