from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./land_records.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


class LandRecord(Base):
    __tablename__ = "land_records"

    id = Column(Integer, primary_key=True, index=True)

    owner_name = Column(String)
    survey_number = Column(String)
    land_area = Column(String)
    location = Column(String)

    ocr_text = Column(String)

    owner_confidence = Column(Float)
    survey_confidence = Column(Float)
    area_confidence = Column(Float)
    location_confidence = Column(Float)

    status = Column(String, default="Approved")

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


Base.metadata.create_all(bind=engine)