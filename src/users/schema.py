from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime 
from src.db.models import UserRole 
from pydantic import BaseModel, EmailStr, field_validator





class UserLoginModel(BaseModel):
		email: str = Field(max_length=20, min_length=2)
		password: str = Field(min_length=3)

class UserCreateModel(BaseModel):
		username: str = Field(max_length=50, min_length=3)
		surname: str = Field(max_length=50, min_length=3)
		email: str = Field(max_length=20,min_length=2)
		password: str = Field(min_length=3)
		phone: str = Field(min_length=5, max_length=30)
		role: UserRole = UserRole.passenger

		@field_validator("role")
		@classmethod
		def validate_role(cls, value: UserRole) -> UserRole:
			if value == UserRole.admin:
				raise ValueError("Admin role cannot be assigned during registration")
			return value

class UserUpdate(BaseModel):
	username: Optional[str] = Field(default=None, min_length=3, max_length=50)
	surname: Optional[str] = Field(max_length=50, min_length=3)
	phone: Optional[str] = Field(min_length=5, max_length=30)

class UserRead(BaseModel):
	username: str
	surname: Optional[str]
	phone: str
	created_at: datetime