import pymysql
from typing import Optional
from datetime import datetime
from backend.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
from backend.infrastructure.token_store import TokenSet

class DBTokenStore:
    def __init__(self,
                 host: str = DB_HOST,
                 port: int = DB_PORT,
                 user: str = DB_USER,
                 password: str = DB_PASSWORD,
                 database: str = DB_NAME):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database

    def _conn(self):
        return pymysql.connect(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            database=self._database,
            charset="utf8mb4",
            autocommit=True,
        )

    def _resolve_user_id(self, cursor, user_key: str) -> Optional[int]:
        if user_key.isdigit():
            return int(user_key)
        cursor.execute("SELECT id FROM users WHERE email=%s", (user_key,))
        row = cursor.fetchone()
        return row[0] if row else None

    def get_tokens(self, user_key: str) -> Optional[TokenSet]:
        with self._conn() as conn:
            with conn.cursor() as cursor:
                uid = self._resolve_user_id(cursor, user_key)
                if uid is None:
                    return None
                cursor.execute(
                    "SELECT access_token, refresh_token, expires_at "
                    "FROM auth_tokens WHERE user_id=%s "
                    "ORDER BY expires_at DESC LIMIT 1",
                    (uid,),
                )
                row = cursor.fetchone()
                if not row:
                    return None
                access_token, refresh_token, expires_at = row
                # PyMySQL 会把 TIMESTAMP 转为 datetime.datetime
                expiry: Optional[datetime] = expires_at
                return TokenSet(access_token=access_token, refresh_token=refresh_token or "", expiry=expiry)

    def save_tokens(self, user_key: str, access_token: str, refresh_token: str, expiry: Optional[datetime] = None):
        with self._conn() as conn:
            with conn.cursor() as cursor:
                uid = self._resolve_user_id(cursor, user_key)
                # 如传的是邮箱且不存在，则创建用户行
                if uid is None and "@" in user_key:
                    cursor.execute(
                        "INSERT INTO users (email) VALUES (%s)",
                        (user_key,),
                    )
                    cursor.execute("SELECT id FROM users WHERE email=%s", (user_key,))
                    uid_row = cursor.fetchone()
                    uid = uid_row[0] if uid_row else None
                if uid is None:
                    raise RuntimeError(f"User not found and cannot create: {user_key}")
                cursor.execute(
                    "INSERT INTO auth_tokens (user_id, access_token, refresh_token, expires_at) "
                    "VALUES (%s, %s, %s, %s)",
                    (uid, access_token, refresh_token or "", expiry),
                )

    def update_tokens(self, user_key: str, access_token: Optional[str] = None,
                      refresh_token: Optional[str] = None, expiry: Optional[datetime] = None):
        with self._conn() as conn:
            with conn.cursor() as cursor:
                uid = self._resolve_user_id(cursor, user_key)
                if uid is None:
                    return
                cursor.execute(
                    "SELECT id FROM auth_tokens WHERE user_id=%s ORDER BY expires_at DESC LIMIT 1",
                    (uid,),
                )
                row = cursor.fetchone()
                if not row:
                    # 没有历史记录则插入一条（需要至少 access_token）
                    if access_token:
                        cursor.execute(
                            "INSERT INTO auth_tokens (user_id, access_token, refresh_token, expires_at) "
                            "VALUES (%s, %s, %s, %s)",
                            (uid, access_token, refresh_token or "", expiry),
                        )
                    return
                token_row_id = row[0]
                # 动态构造 UPDATE 语句
                sets = []
                params = []
                if access_token is not None:
                    sets.append("access_token=%s")
                    params.append(access_token)
                if refresh_token is not None:
                    sets.append("refresh_token=%s")
                    params.append(refresh_token or "")
                if expiry is not None:
                    sets.append("expires_at=%s")
                    params.append(expiry)
                if not sets:
                    return
                params.append(token_row_id)
                cursor.execute(
                    f"UPDATE auth_tokens SET {', '.join(sets)} WHERE id=%s",
                    tuple(params),
                )