from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from database import get_today_entry, save_entry
from keyboards import mood_keyboard, existing_entry_keyboard, main_menu

router = Router()


class DiaryStates(StatesGroup):
    waiting_mood = State()
    waiting_note = State()


# ---------- /start ----------
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    entry = await get_today_entry(message.from_user.id)

    if entry:
        await message.answer(
            f"Привет! 👋 Сегодня ты уже записал день:\n\n"
            f"Оценка: <b>{entry['mood']}/10</b>\n"
            f"Запись: {entry['note']}\n\n"
            f"Хочешь обновить или посмотреть статистику?",
            reply_markup=existing_entry_keyboard(),
        )
    else:
        await message.answer(
            "Привет! 👋 Давай запишем, как прошёл день.\n\n"
            "Оцени его от 1 до 10:",
            reply_markup=mood_keyboard(),
        )
        await state.set_state(DiaryStates.waiting_mood)


# ---------- Кнопка "Обновить" ----------
@router.callback_query(F.data == "entry:update")
async def cb_update(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Ок, давай обновим запись.\n\nОцени день от 1 до 10:",
        reply_markup=mood_keyboard(),
    )
    await state.set_state(DiaryStates.waiting_mood)
    await callback.answer()


# ---------- Выбор оценки ----------
@router.callback_query(DiaryStates.waiting_mood, F.data.startswith("mood:"))
async def cb_mood(callback: CallbackQuery, state: FSMContext):
    mood = int(callback.data.split(":")[1])
    await state.update_data(mood=mood)
    await callback.message.edit_text(
        f"Оценка: <b>{mood}/10</b>\n\n"
        f"Теперь напиши пару слов о том, как прошёл день:"
    )
    await state.set_state(DiaryStates.waiting_note)
    await callback.answer()


# ---------- Ввод текста ----------
@router.message(DiaryStates.waiting_note, F.text)
async def msg_note(message: Message, state: FSMContext):
    data = await state.get_data()
    mood = data.get("mood")
    note = message.text.strip()

    if not note:
        await message.answer("Напиши хоть пару слов 🙂")
        return
    if len(note) > 500:
        await message.answer("Слишком длинно, уложись в 500 символов.")
        return

    await save_entry(message.from_user.id, mood, note)
    await state.clear()

    await message.answer(
        f"✅ Записано!\n\n"
        f"Оценка: <b>{mood}/10</b>\n"
        f"Заметка: {note}\n\n"
        f"Команды: /stats — статистика, /start — меню",
        reply_markup=main_menu(),
    )


# ---------- Кнопка "📝 Записать день" ----------
@router.message(F.text == "📝 Записать день")
async def btn_record(message: Message, state: FSMContext):
    await cmd_start(message, state)