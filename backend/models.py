import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, ForeignKey, Table, Enum
)
from sqlalchemy.orm import relationship
from backend.database import Base
import enum


class InteractionType(str, enum.Enum):
    FACE_TO_FACE = "face_to_face"
    VIRTUAL = "virtual"
    PHONE = "phone"
    EMAIL = "email"
    CONFERENCE = "conference"
    LUNCH_MEETING = "lunch_meeting"


class InteractionChannel(str, enum.Enum):
    IN_CLINIC = "in_clinic"
    HOSPITAL = "hospital"
    VIRTUAL_MEETING = "virtual_meeting"
    PHONE_CALL = "phone_call"
    EMAIL = "email"
    CONFERENCE = "conference"
    DINNER_EVENT = "dinner_event"


class InteractionStatus(str, enum.Enum):
    COMPLETED = "completed"
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    FOLLOW_UP_REQUIRED = "follow_up_required"


# Many-to-many junction table
interaction_products = Table(
    "interaction_products",
    Base.metadata,
    Column("interaction_id", Integer, ForeignKey("interactions.id"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
)


class HCP(Base):
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    specialty = Column(String(200), nullable=False)
    institution = Column(String(300))
    email = Column(String(255))
    phone = Column(String(50))
    npi_number = Column(String(20), unique=True)
    territory = Column(String(100))
    city = Column(String(100))
    state = Column(String(100))
    tier = Column(String(10), default="B")  # A, B, C tier
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    interactions = relationship("Interaction", back_populates="hcp")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100))
    description = Column(Text)
    key_messages = Column(Text)  # JSON string of key messages
    therapeutic_area = Column(String(200))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    interactions = relationship("Interaction", secondary=interaction_products, back_populates="products")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=False)
    rep_name = Column(String(200), default="Field Rep")
    interaction_type = Column(String(50), nullable=False)
    channel = Column(String(50))
    interaction_date = Column(DateTime, default=datetime.datetime.utcnow)
    duration_minutes = Column(Integer)
    raw_notes = Column(Text)
    ai_summary = Column(Text)
    sentiment = Column(String(20))  # positive, neutral, negative
    key_topics = Column(Text)  # JSON string
    follow_up_actions = Column(Text)
    follow_up_date = Column(DateTime, nullable=True)
    status = Column(String(30), default="completed")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    hcp = relationship("HCP", back_populates="interactions")
    products = relationship("Product", secondary=interaction_products, back_populates="interactions")
