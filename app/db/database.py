from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./sales_leads.db"

engine = create_engine(
    DATABASE_URL,
    # allows SQLite connections to be shared across multiple threads, which helps compatibility with FastAPI's threaded/concurrent request handling
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
