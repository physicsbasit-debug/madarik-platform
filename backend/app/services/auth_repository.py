from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.core.config import settings
from app.models.auth import AccountRole, AuthAccountPublic


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_username(username: str) -> str:
    return username.strip().lower()


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        180_000,
    ).hex()


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _row_to_account(row: sqlite3.Row) -> AuthAccountPublic:
    return AuthAccountPublic(
        id=row["id"],
        username=row["username"],
        display_name=row["display_name"],
        role=AccountRole(row["role"]),
        is_active=bool(row["is_active"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        last_login_at=datetime.fromisoformat(row["last_login_at"]) if row["last_login_at"] else None,
    )


class AuthRepository:
    """SQLite-backed account/session repository for Phase 2-B1.

    This is an authentication foundation, not a full school identity system.
    The aim is to introduce accounts and roles without yet tying every project
    endpoint to ownership rules. One disaster at a time, please.
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path or settings.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS auth_accounts (
                    id TEXT PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    display_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    password_salt TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    last_login_at TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS auth_sessions (
                    token_hash TEXT PRIMARY KEY,
                    account_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    FOREIGN KEY(account_id) REFERENCES auth_accounts(id) ON DELETE CASCADE
                )
                """
            )
            connection.execute("CREATE INDEX IF NOT EXISTS idx_auth_accounts_username ON auth_accounts(username)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_auth_sessions_account_id ON auth_sessions(account_id)")

    def accounts_exist(self) -> bool:
        with self._connect() as connection:
            row = connection.execute("SELECT 1 FROM auth_accounts LIMIT 1").fetchone()
        return row is not None

    def create_owner_if_empty(self, username: str, display_name: str, password: str) -> AuthAccountPublic | None:
        if self.accounts_exist():
            return None

        now = _utc_now()
        account_id = secrets.token_hex(16)
        salt = secrets.token_hex(16)
        username_normalized = _normalize_username(username)
        password_hash = _hash_password(password, salt)

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO auth_accounts (
                    id, username, display_name, role, password_hash, password_salt,
                    is_active, created_at, last_login_at
                )
                VALUES (?, ?, ?, ?, ?, ?, 1, ?, NULL)
                """,
                (
                    account_id,
                    username_normalized,
                    display_name.strip(),
                    AccountRole.owner.value,
                    password_hash,
                    salt,
                    now.isoformat(),
                ),
            )

        account = self.get_account_by_username(username_normalized)
        if account is None:
            raise RuntimeError("Owner account was not created")
        return account

    def list_accounts(self) -> list[AuthAccountPublic]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM auth_accounts ORDER BY created_at ASC"
            ).fetchall()
        return [_row_to_account(row) for row in rows]

    def create_account(
        self,
        username: str,
        display_name: str,
        password: str,
        role: AccountRole,
        is_active: bool = True,
    ) -> AuthAccountPublic:
        now = _utc_now()
        account_id = secrets.token_hex(16)
        salt = secrets.token_hex(16)
        username_normalized = _normalize_username(username)
        password_hash = _hash_password(password, salt)

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO auth_accounts (
                    id, username, display_name, role, password_hash, password_salt,
                    is_active, created_at, last_login_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL)
                """,
                (
                    account_id,
                    username_normalized,
                    display_name.strip(),
                    role.value,
                    password_hash,
                    salt,
                    1 if is_active else 0,
                    now.isoformat(),
                ),
            )

        account = self.get_account_by_id(account_id)
        if account is None:
            raise RuntimeError("Account was not created")
        return account

    def update_account(
        self,
        account_id: str,
        display_name: str | None = None,
        role: AccountRole | None = None,
        is_active: bool | None = None,
    ) -> AuthAccountPublic | None:
        account = self.get_account_by_id(account_id)
        if account is None:
            return None

        next_display_name = display_name.strip() if display_name is not None else account.display_name
        next_role = role.value if role is not None else account.role.value
        next_is_active = account.is_active if is_active is None else is_active

        with self._connect() as connection:
            connection.execute(
                """
                UPDATE auth_accounts
                SET display_name = ?, role = ?, is_active = ?
                WHERE id = ?
                """,
                (
                    next_display_name,
                    next_role,
                    1 if next_is_active else 0,
                    account_id,
                ),
            )

            if is_active is False:
                connection.execute("DELETE FROM auth_sessions WHERE account_id = ?", (account_id,))

        return self.get_account_by_id(account_id)

    def count_active_owners(self) -> int:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM auth_accounts WHERE role = ? AND is_active = 1",
                (AccountRole.owner.value,),
            ).fetchone()
        return int(row["count"] if row else 0)


    def get_account_by_username(self, username: str) -> AuthAccountPublic | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM auth_accounts WHERE username = ?",
                (_normalize_username(username),),
            ).fetchone()
        return _row_to_account(row) if row else None

    def get_account_by_id(self, account_id: str) -> AuthAccountPublic | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM auth_accounts WHERE id = ?",
                (account_id,),
            ).fetchone()
        return _row_to_account(row) if row else None

    def authenticate(self, username: str, password: str) -> tuple[str, AuthAccountPublic] | None:
        username_normalized = _normalize_username(username)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM auth_accounts WHERE username = ?",
                (username_normalized,),
            ).fetchone()

            if row is None or not bool(row["is_active"]):
                return None

            expected_hash = row["password_hash"]
            actual_hash = _hash_password(password, row["password_salt"])
            if not hmac.compare_digest(expected_hash, actual_hash):
                return None

            token = secrets.token_urlsafe(40)
            token_hash = _hash_token(token)
            now = _utc_now()
            expires_at = now + timedelta(days=7)
            connection.execute(
                "INSERT INTO auth_sessions (token_hash, account_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
                (token_hash, row["id"], now.isoformat(), expires_at.isoformat()),
            )
            connection.execute(
                "UPDATE auth_accounts SET last_login_at = ? WHERE id = ?",
                (now.isoformat(), row["id"]),
            )

        account = self.get_account_by_id(row["id"])
        if account is None:
            raise RuntimeError("Authenticated account disappeared")
        return token, account

    def get_account_by_token(self, token: str) -> AuthAccountPublic | None:
        token_hash = _hash_token(token)
        now = _utc_now()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT account_id, expires_at
                FROM auth_sessions
                WHERE token_hash = ?
                """,
                (token_hash,),
            ).fetchone()

            if row is None:
                return None

            expires_at = datetime.fromisoformat(row["expires_at"])
            if expires_at <= now:
                connection.execute("DELETE FROM auth_sessions WHERE token_hash = ?", (token_hash,))
                return None

        return self.get_account_by_id(row["account_id"])

    def logout(self, token: str) -> bool:
        token_hash = _hash_token(token)
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM auth_sessions WHERE token_hash = ?", (token_hash,))
            return cursor.rowcount > 0


auth_repository = AuthRepository()
