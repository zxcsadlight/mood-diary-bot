import asyncio
print("ЗАПУСК БОТА...")
import logging
import ssl

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession

from config import BOT_TOKEN
from database import init_db
from handlers import common, diary, stats


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    await init_db()

    # 1. Создаем стандартную сессию с прокси
    proxy_url = "socks5://127.0.0.1:10808"
    session = AiohttpSession(proxy=proxy_url)

    # 2. Создаем SSL-контекст, отключающий проверку
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # 3. ПРИНУДИТЕЛЬНО подменяем внутренние настройки коннектора
    # aiogram использует этот словарь при создании aiohttp.ClientSession
    session._connector_init['ssl'] = ssl_context

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )
    dp = Dispatcher()

    dp.include_router(common.router)
    dp.include_router(stats.router)
    dp.include_router(diary.router)

    logging.info("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен")