from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.models.auth import (
    AccountRole,
    AuthAccountPublic,
    AuthBootstrapRequest,
    AuthCreateAccountRequest,
    AuthLoginRequest,
    AuthSessionInfo,
    AuthUpdateAccountRequest,
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


def _require_current_account(authorization: str | None = Header(default=None)) -> AuthAccountPublic:
    token = _extract_bearer_token(authorization)
    if token is None:
        raise HTTPException(status_code=401, detail="جلسة الدخول غير موجودة.")
    account = auth_repository.get_account_by_token(token)
    if account is None:
        raise HTTPException(status_code=401, detail="جلسة الدخول غير صالحة أو منتهية.")
    return account


def _require_owner_account(authorization: str | None = Header(default=None)) -> AuthAccountPublic:
    account = _require_current_account(authorization)
    if account.role != AccountRole.owner:
        raise HTTPException(status_code=403, detail="إدارة الحسابات متاحة لمالك المنصة فقط.")
    return account


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


@router.get("/accounts")
def list_accounts(owner: AuthAccountPublic = Depends(_require_owner_account)) -> list[AuthAccountPublic]:
    """List accounts for the owner dashboard."""

    return auth_repository.list_accounts()


@router.post("/accounts", status_code=status.HTTP_201_CREATED)
def create_account(payload: AuthCreateAccountRequest, owner: AuthAccountPublic = Depends(_require_owner_account)) -> AuthAccountPublic:
    """Create a lightweight user account in Phase 2-B3."""

    existing = auth_repository.get_account_by_username(payload.username)
    if existing is not None:
        raise HTTPException(status_code=409, detail="اسم المستخدم موجود سابقًا.")
    return auth_repository.create_account(
        username=payload.username,
        display_name=payload.display_name,
        password=payload.password,
        role=payload.role,
        is_active=payload.is_active,
    )


@router.patch("/accounts/{account_id}")
def update_account(
    account_id: str,
    payload: AuthUpdateAccountRequest,
    owner: AuthAccountPublic = Depends(_require_owner_account),
) -> AuthAccountPublic:
    """Update role/display/active state for a lightweight account."""

    target = auth_repository.get_account_by_id(account_id)
    if target is None:
        raise HTTPException(status_code=404, detail="الحساب غير موجود.")

    next_role = payload.role if payload.role is not None else target.role
    next_active = payload.is_active if payload.is_active is not None else target.is_active
    if target.id == owner.id and (next_role != AccountRole.owner or not next_active):
        raise HTTPException(status_code=400, detail="لا يمكن للمالك تعطيل نفسه أو إزالة دور المالك من حسابه.")
    if target.role == AccountRole.owner and (next_role != AccountRole.owner or not next_active):
        if auth_repository.count_active_owners() <= 1:
            raise HTTPException(status_code=400, detail="يجب أن يبقى مالك نشط واحد على الأقل.")

    updated = auth_repository.update_account(
        account_id=account_id,
        display_name=payload.display_name,
        role=payload.role,
        is_active=payload.is_active,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="الحساب غير موجود.")
    return updated


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
