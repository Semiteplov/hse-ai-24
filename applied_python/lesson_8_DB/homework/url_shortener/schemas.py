from datetime import datetime

from pydantic import BaseModel


class LinkCreate(BaseModel):
    original_url: str
    custom_alias: str | None = None
    expires_at: datetime | None = None


class LinkResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    created_at: datetime
    expires_at: datetime | None


class VisitResponse(BaseModel):
    id: int
    visited_at: datetime


class LinkStatsResponse(BaseModel):
    original_url: str
    short_code: str
    created_at: datetime
    visits: list[VisitResponse]


class LinkUpdate(BaseModel):
    new_url: str


class UserCreate(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
