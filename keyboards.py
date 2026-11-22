from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
)


def mood_keyboard() -> InlineKeyboardMarkup:
    """Оценка 1–10 в 2 ряда по 5."""
    rows = []
    for start in (1, 6):
        rows.append([
            InlineKeyboardButton(text=str(i), callback_data=f"mood:{i}")
            for i in range(start, start + 5)
        ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def existing_entry_keyboard() -> InlineKeyboardMarkup:
    """Кнопки, если запись за сегодня уже есть."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Обновить", callback_data="entry:update")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="entry:stats")],
    ])


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Записать день")],
            [KeyboardButton(text="📊 Статистика")],
        ],
        resize_keyboard=True,
    )

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def stats_period_keyboard(active_period: str = "week") -> InlineKeyboardMarkup:
    week_text = "✅ Неделя" if active_period == "week" else "Неделя"
    month_text = "✅ Месяц" if active_period == "month" else "Месяц"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=week_text, callback_data="stats_week"),
            InlineKeyboardButton(text=month_text, callback_data="stats_month")
        ]
    ])