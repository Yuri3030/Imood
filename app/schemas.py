from pydantic import BaseModel, EmailStr
from pydantic import Field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List

# -------- Users --------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    date_of_birth: Optional[date] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    date_of_birth: Optional[date] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}  # Pydantic v2

# -------- Moods --------
class MoodType(str, Enum):
    alegria = "alegria"
    tristeza = "tristeza"
    angustia = "angustia"
    magoa = "mágoa"
    ansiedade = "ansiedade"

class MoodCreate(BaseModel):
    score: int = Field(..., ge=1, le=5)
    mood_type: MoodType
    comment: Optional[str] = None

class MoodResponse(BaseModel):
    id: int
    score: int
    mood_type: MoodType
    comment: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}

# -------- Reminders --------
class ReminderCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=280)
    # ISO 8601 (ex.: "2025-08-10T14:00:00Z")
    due_at: datetime

class ReminderResponse(BaseModel):
    id: int
    message: str
    due_at: datetime
    done: bool
    created_at: datetime

    model_config = {"from_attributes": True}

# -------- Emergency Contacts --------
class EmergencyContactBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    phone: str = Field(..., min_length=2, max_length=30)
    category: Optional[str] = None

class EmergencyContactCreate(EmergencyContactBase):
    pass

class EmergencyContactResponse(EmergencyContactBase):
    id: int
    is_default: bool
    created_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
