# Initialize SQLite database using SQLAlchemy ORM
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Import models - handle both relative and absolute imports
try:
    from .models import Author, Article, Base
except ImportError:
    from models import Author, Article, Base

# Global engine and session factory
engine = None
SessionLocal = None

def create_connection(db_file: str):
    """Create a database engine and session factory for SQLite.
    
    :param db_file: Path to the SQLite database file
    :return: SessionLocal (session factory) or None on error
    """
    global engine, SessionLocal
    try:
        engine = create_engine(f'sqlite:///{db_file}', echo=False)
        SessionLocal = sessionmaker(bind=engine)
        return SessionLocal
    except SQLAlchemyError as e:
        print(f"Failed to create database connection: {e}")
        return None

def create_tables():
    """Create all tables defined in the models using SQLAlchemy."""
    try:
        Base.metadata.create_all(engine)
        print("Tables created successfully using SQLAlchemy.")
    except SQLAlchemyError as e:
        print(f"Error creating tables: {e}")
def main():
    """Initialize the SQLAlchemy database and create tables."""
    database = "scraper_data.db"
    
    # Create connection and session factory
    SessionLocal = create_connection(database)
    if SessionLocal is None:
        print("Error! Cannot create the database connection.")
        return
    
    try:
        # Create all tables
        create_tables()
        print(f"Database '{database}' initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")


if __name__ == '__main__':
    main()
