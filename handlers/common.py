import io
import csv
from aiogram.types import BufferedInputFile
from database import get_all_entries
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📖 <b>Что умеет бот</b>\n\n"
        "/start — записать день или открыть меню\n"
        "/stats — статистика настроения\n"
        "/help — эта справка\n"
        "/cancel — отменить ввод\n\n"
        "Каждый день можно записать одну оценку (1–10) и заметку. "
        "Если запись за сегодня уже есть — её можно обновить."
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    current = await state.get_state()
    await state.clear()
    if current is None:
        await message.answer("Нечего отменять 🙂")
    else:
        await message.answer("Ок, отменил. Можешь начать заново: /start")

        import io
import csv
from aiogram.types import BufferedInputFile
from database import get_all_entries

# ... (внутри вашего common.py)

@router.message(Command("export"))
async def cmd_export(message: Message):
    entries = await get_all_entries(message.from_user.id)
    if not entries:
        await message.answer("У вас пока нет записей для экспорта.")
        return

    # Создаем CSV файл в памяти
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';') # ; удобнее для Excel
    
    # Заголовки
    writer.writerow(["Дата", "Оценка", "Заметка", "Создано", "Обновлено"])
    for e in entries:
        writer.writerow([e['entry_date'], e['mood'], e['note'], e['created_at'], e['updated_at']])

    # Кодируем в байты (utf-8-sig нужен, чтобы Excel не ломал русские буквы)
    file_bytes = output.getvalue().encode('utf-8-sig')
    
    # Отправляем документ
    file = BufferedInputFile(file_bytes, filename=f"mood_export_{message.from_user.id}.csv")
    await message.answer_document(file, caption="📁 Ваши записи в формате CSV. Можно открыть в Excel!")