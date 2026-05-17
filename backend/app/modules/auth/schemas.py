from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6)
    preferences: str | None = None
    allergies: str | None = None
    diet: str | None = None
    favorite_dishes: str | None = None
    weekly_budget: float | None = None
    monthly_budget: float | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    preferences: str | None = None
    allergies: str | None = None
    diet: str | None = None
    favorite_dishes: str | None = None
    weekly_budget: float | None = None
    monthly_budget: float | None = None

    model_config = ConfigDict(from_attributes=True)


class UserRoleUpdate(BaseModel):
    role: Literal["user", "admin"]
