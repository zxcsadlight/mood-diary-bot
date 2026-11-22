import aiosqlite
from datetime import date, datetime, timedelta
from config import DB_PATH


async def init_db() -> None:
    """Создаёт таблицу, если её нет."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mood INTEGER NOT NULL CHECK (mood BETWEEN 1 AND 10),
                note TEXT NOT NULL,
                entry_date TEXT NOT NULL,          -- 'YYYY-MM-DD'
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(user_id, entry_date)
            )
        """)
        await db.commit()


async def get_today_entry(user_id: int) -> dict | None:
    """Возвращает запись за сегодня или None."""
    today = date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM entries WHERE user_id = ? AND entry_date = ?",
            (user_id, today),
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def save_entry(user_id: int, mood: int, note: str) -> None:
    """
    Сохраняет запись за сегодня.
    Если уже есть — обновляет (UPSERT).
    """
    today = date.today().isoformat()
    now = datetime.now().isoformat(timespec="seconds")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO entries (user_id, mood, note, entry_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, entry_date) DO UPDATE SET
                mood = excluded.mood,
                note = excluded.note,
                updated_at = excluded.updated_at
        """, (user_id, mood, note, today, now, now))
        await db.commit()


async def get_entries_for_period(user_id: int, days: int) -> list[dict]:
    """
    Возвращает записи за последние N дней (включая сегодня),
    отсортированные по дате по возрастанию.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM entries
            WHERE user_id = ?
              AND entry_date >= date('now', ?)
            ORDER BY entry_date ASC
        """, (user_id, f"-{days - 1} days")) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def get_streak(user_id: int) -> int:
    """Считает, сколько дней подряд пользователь делал записи."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT entry_date FROM entries WHERE user_id = ? ORDER BY entry_date DESC",
            (user_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            
    if not rows:
        return 0
        
    dates = [datetime.strptime(row[0], "%Y-%m-%d").date() for row in rows]
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    if dates[0] != today and dates[0] != yesterday:
        return 0
        
    streak = 1
    for i in range(len(dates) - 1):
        if dates[i] - dates[i+1] == timedelta(days=1):
            streak += 1
        else:
            break
            
    return streak


async def get_all_entries(user_id: int) -> list[dict]:
    """Возвращает вообще все записи пользователя для экспорта."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM entries WHERE user_id = ? ORDER BY entry_date ASC",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]