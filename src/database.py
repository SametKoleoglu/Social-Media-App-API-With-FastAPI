from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./src/database.db"

engine = create_engine(DATABASE_URL,pool_pre_ping=True, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker( autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
     db = SessionLocal()
     try:
          yield db
     finally:
          db.close()