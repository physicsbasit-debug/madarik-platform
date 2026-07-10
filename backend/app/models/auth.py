from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class AccountRole(str, Enum):
    owner = "owner"
    teacher = "teacher"
    reviewer = "reviewer"


class AuthAccountPublic(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    username: str
    display_name: str
    role: AccountRole = AccountRole.teacher
    is_active: bool = True
    created_at: datetime
    last_login_at: datetime | None = None


class AuthStatus(BaseModel):
    accounts_exist: bool
    requires_bootstrap: bool


class AuthBootstrapRequest(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    display_name: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=6, max_length=128)


class AuthLoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    password: str = Field(min_length=6, max_length=128)


class AuthSessionInfo(BaseModel):
    token: str
    account: AuthAccountPublic



class AuthCreateAccountRequest(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    display_name: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=6, max_length=128)
    role: AccountRole = AccountRole.teacher
    is_active: bool = True


class AuthUpdateAccountRequest(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=80)
    role: AccountRole | None = None
    is_active: bool | None = None
