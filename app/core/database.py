from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings
from app.core.logging import logger


logger.info("Initializing database connection")


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db():
    """
    Provide a SQLAlchemy database session
    for the duration of a request.
    """

    db = SessionLocal()

    logger.info("Database session created")

    try:
        yield db

    finally:
        db.close()

        logger.info("Database session closed")


logger.info("Database configuration loaded successfully")