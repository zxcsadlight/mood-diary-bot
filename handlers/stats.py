from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from database import get_entries_for_period, get_streak
from keyboards import stats_period_keyboard # <-- Импортируем наши новые кнопки

router = Router()

def build_stats_text(entries: list[dict], streak: int, period_label: str) -> str:
    if not entries:
        return f"За {period_label} записей пока нет. Начни с /start 🙂"

    moods = [e["mood"] for e in entries]
    avg = sum(moods) / len(moods)
    best = max(entries, key=lambda e: e["mood"])
    worst = min(entries, key=lambda e: e["mood"])

    lines = [
        f"📊 <b>Статистика за {period_label}</b>\n",
        f"Записей: <b>{len(entries)}</b>",
        f"Средняя оценка: <b>{avg:.1f}/10</b>",
        f"🔥 Текущий стрик: <b>{streak} дн.</b>\n",
        f"<i>График настроения:</i>",
    ]

    # Для месяца показываем последние 15 дней, чтобы сообщение не было слишком длинным
    display_entries = entries[-15:] if len(entries) > 15 else entries
    
    for e in display_entries:
        day_str = e["entry_date"][5:].replace("-", ".")
        mood = e["mood"]
        bar = "█" * mood
        empty = "░" * (10 - mood)
        lines.append(f"{day_str} | <code>{bar}{empty}</code> {mood}")

    lines.append("")
    lines.append(f"🏆 Лучший день: <b>{best['mood']}/10</b> ({best['entry_date']})")
    lines.append(f"📉 Худший день: <b>{worst['mood']}/10</b> ({worst['entry_date']})")

    return "\n".join(lines)


# --- Хелпер для отправки и редактирования ---
async def _send_stats(target, days: int, period_label: str, active_period: str, edit=False):
    user_id = target.from_user.id
    entries = await get_entries_for_period(user_id, days)
    streak = await get_streak(user_id)
    
    text = build_stats_text(entries, streak, period_label)
    kb = stats_period_keyboard(active_period)

    if edit and isinstance(target, CallbackQuery):
        # Редактируем сообщение, если нажали кнопку
        await target.message.edit_text(text, reply_markup=kb)
    else:
        # Отправляем новое, если вызвали командой
        await target.answer(text, reply_markup=kb)


# --- Обработчики команд ---
@router.message(Command("stats"))
async def cmd_stats(message: Message):
    await _send_stats(message, days=7, period_label="неделю", active_period="week")

@router.message(F.text == "📊 Статистика")
async def btn_stats(message: Message):
    await cmd_stats(message)


# --- Обработчики инлайн-кнопок ---
@router.callback_query(F.data == "stats_week")
async def cb_stats_week(callback: CallbackQuery):
    await _send_stats(callback, days=7, period_label="неделю", active_period="week", edit=True)
    await callback.answer()

@router.callback_query(F.data == "stats_month")
async def cb_stats_month(callback: CallbackQuery):
    await _send_stats(callback, days=30, period_label="месяц", active_period="month", edit=True)
    await callback.answer()

@router.callback_query(F.data == "entry:stats")
async def cb_stats_from_menu(callback: CallbackQuery):
    # Это старая кнопка из меню "Обновить / Статистика"
    await _send_stats(callback, days=7, period_label="неделю", active_period="week", edit=False)
    await callback.answer()