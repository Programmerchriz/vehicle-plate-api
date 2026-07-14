from pydantic import BaseModel, EmailStr

from app.models.enums import UserRole


class UserResponse(BaseModel):
  id: int
  full_name: str
  email: EmailStr
  role: UserRole
  is_active: bool

  model_config = {
    "from_attributes": True,
  }