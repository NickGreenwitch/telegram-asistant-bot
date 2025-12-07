from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DB_PATH

Base = declarative_base()
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    kind = Column(String(50))
    query = Column(Text)
    answer = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(engine)

def save_log(kind, query, answer):
    s = Session()
    s.add(Log(kind=kind, query=query, answer=answer))
    s.commit()
    s.close()