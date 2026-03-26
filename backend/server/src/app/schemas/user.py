import uuid

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class UserRead(BaseModel):
    id: uuid.UUID
    name: str
    username: str
    email: str
    is_superuser: bool
    is_deleted: bool

    model_config = {"from_attributes": True}
