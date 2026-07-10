from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, status

from app.models.auth import (
    AuthAccountPublic,
    AuthBootstrapRequest,
    AuthLoginRequest,
    AuthSessionInfo,
    AuthStatus,
)
from app.services.auth_repository import auth_repository

router = APIRouter(prefix="/auth", tags=["auth"])


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token.strip()


@router.get("/status")
def get_auth_status() -> AuthStatus:
    accounts_exist = auth_repository.accounts_exist()
    return AuthStatus(accounts_exist=accounts_exist, requires_bootstrap=not accounts_exist)


@router.post("/bootstrap", status_code=status.HTTP_201_CREATED)
def bootstrap_owner(payload: AuthBootstrapRequest) -> AuthSessionInfo:
    account = auth_repository.create_owner_if_empty(
        username=payload.username,
        display_name=payload.display_name,
        password=payload.password,
    )
    if account is None:
        raise HTTPException(status_code=409, detail="تم إنشاء حساب المالك سابقًا.")

    authenticated = auth_repository.authenticate(payload.username, payload.password)
    if authenticated is None:
        raise HTTPException(status_code=500, detail="تعذر إنشاء جلسة الدخول بعد التهيئة.")
    token, account = authenticated
    return AuthSessionInfo(token=token, account=account)


@router.post("/login")
def login(payload: AuthLoginRequest) -> AuthSessionInfo:
    authenticated = auth_repository.authenticate(payload.username, payload.password)
    if authenticated is None:
        raise HTTPException(status_code=401, detail="اسم المستخدم أو كلمة المرور غير صحيحة.")
    token, account = authenticated
    return AuthSessionInfo(token=token, account=account)


@router.get("/me")
def get_current_account(authorization: str | None = Header(default=None)) -> AuthAccountPublic:
    token = _extract_bearer_token(authorization)
    if token is None:
        raise HTTPException(status_code=401, detail="جلسة الدخول غير موجودة.")
    account = auth_repository.get_account_by_token(token)
    if account is None:
        raise HTTPException(status_code=401, detail="جلسة الدخول غير صالحة أو منتهية.")
    return account


@router.post("/logout")
def logout(authorization: str | None = Header(default=None)) -> dict[str, bool]:
    token = _extract_bearer_token(authorization)
    if token is None:
        return {"logged_out": False}
    return {"logged_out": auth_repository.logout(token)}
