from datetime import datetime
import enum

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date,
    ForeignKey, CheckConstraint, func
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Enum as SqlEnum

from app.database import Base


# ---------- Users ----------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    # REMOVIDO: password_hash
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    deleted_at = Column(DateTime, nullable=True)


# ---------- Moods ----------
class MoodType(str, enum.Enum):
    alegria = "alegria"
    tristeza = "tristeza"
    angustia = "angustia"
    magoa = "mágoa"
    ansiedade = "ansiedade"


class Mood(Base):
    __tablename__ = "moods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    mood_type = Column(SqlEnum(MoodType), nullable=False)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("score >= 1 AND score <= 5", name="ck_moods_score_range"),
    )

    user = relationship("User", backref=backref("moods", cascade="all, delete-orphan"))


# ---------- Reminders ----------
class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    message = Column(String, nullable=False)
    due_at = Column(DateTime(timezone=True), nullable=False)
    done = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", backref=backref("reminders", cascade="all, delete-orphan"))


# ---------- Emergency Contacts ----------
class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id = Column(Integer, primary_key=True, index=True)
    # Contato global (padrão): user_id = NULL e is_default = True
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    category = Column(String, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User", backref="emergency_contacts")
