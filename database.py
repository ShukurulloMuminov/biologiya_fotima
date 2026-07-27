import aiosqlite

from config import DB_PATH

_conn: aiosqlite.Connection = None


async def init_db():
    global _conn
    _conn = await aiosqlite.connect(DB_PATH)
    _conn.row_factory = aiosqlite.Row
    await _conn.execute("PRAGMA journal_mode=WAL")  # bir vaqtda o'qish/yozishni tezlashtiradi
    await _conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            referrer_id INTEGER,
            referral_counted INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            access_granted INTEGER DEFAULT 0,
            joined_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    await _conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    await _conn.commit()


async def user_exists(user_id: int) -> bool:
    async with _conn.execute("SELECT 1 FROM users WHERE user_id=?", (user_id,)) as cur:
        row = await cur.fetchone()
        return row is not None


async def add_user(user_id: int, username: str, full_name: str, referrer_id: int = None):
    await _conn.execute("""
        INSERT OR IGNORE INTO users (user_id, username, full_name, referrer_id)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, full_name, referrer_id))
    await _conn.commit()


async def get_user(user_id: int):
    async with _conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cur:
        return await cur.fetchone()


async def mark_referral_counted(user_id: int):
    await _conn.execute("UPDATE users SET referral_counted=1 WHERE user_id=?", (user_id,))
    await _conn.commit()


async def add_point(referrer_id: int):
    await _conn.execute("UPDATE users SET points = points + 1 WHERE user_id=?", (referrer_id,))
    await _conn.commit()
    async with _conn.execute("SELECT points FROM users WHERE user_id=?", (referrer_id,)) as cur:
        row = await cur.fetchone()
        return row["points"] if row else None


async def set_access_granted(user_id: int):
    await _conn.execute("UPDATE users SET access_granted=1 WHERE user_id=?", (user_id,))
    await _conn.commit()


async def get_all_user_ids():
    async with _conn.execute("SELECT user_id FROM users") as cur:
        rows = await cur.fetchall()
        return [r["user_id"] for r in rows]


async def count_users() -> int:
    async with _conn.execute("SELECT COUNT(*) AS c FROM users") as cur:
        row = await cur.fetchone()
        return row["c"]


async def top_referrers(limit: int = 10):
    async with _conn.execute(
        "SELECT user_id, username, full_name, points FROM users ORDER BY points DESC LIMIT ?",
        (limit,)
    ) as cur:
        return await cur.fetchall()


async def get_setting(key: str):
    async with _conn.execute("SELECT value FROM settings WHERE key=?", (key,)) as cur:
        row = await cur.fetchone()
        return row["value"] if row else None


async def set_setting(key: str, value: str):
    await _conn.execute("""
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, value))
    await _conn.commit()
