from sqlalchemy import text

from app.core.database import Base, engine


def init_db():
    Base.metadata.create_all(bind=engine)
    _run_migrations()


def _run_migrations():
    with engine.connect() as conn:
        conn.execute(text(
            "ALTER TABLE leads ADD COLUMN IF NOT EXISTS "
            "last_enriched_at TIMESTAMP WITH TIME ZONE"
        ))
        conn.commit()
