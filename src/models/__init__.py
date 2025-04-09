"""Data models for the application."""

from typing import Optional

from pydantic import UUID4, BaseModel


class UserSettingsBase(BaseModel):
    theme: Optional[str] = "light"
    language: Optional[str] = "en"
    timezone: Optional[str] = "UTC"


class UserSettings(UserSettingsBase):
    id: UUID4
