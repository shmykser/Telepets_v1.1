#!/usr/bin/env python3
"""
Простой Telegram бот для получения уведомлений от Telepets.
Запускается отдельно от основного API сервера.
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен бота
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
    logger.error("❌ TELEGRAM_BOT_TOKEN не установлен в .env файле!")
    logger.info("📝 Создайте бота через @BotFather и добавьте токен в .env")
    exit(1)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    user_id = str(message.from_user.id)
    
    welcome_text = f"""
🎮 Добро пожаловать в Telepets!

Ваш ID: <code>{user_id}</code>

📱 Используйте этот ID для создания питомца через API:
<code>curl -X POST "http://127.0.0.1:3000/create?user_id={user_id}&name=МойПитомец"</code>

🔔 Теперь вы будете получать уведомления о:
• Низком здоровье питомца
• Переходах между стадиями
• Смерти питомца

🎯 Начните игру, создав питомца!
    """
    
    await message.answer(welcome_text, parse_mode="HTML")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = """
📚 Помощь по Telepets:

🎮 <b>Как играть:</b>
1. Создайте питомца через API
2. Поддерживайте его здоровье
3. Следите за переходами между стадиями

📱 <b>API Endpoints:</b>
• POST /create - создать питомца
• POST /health_up - увеличить здоровье
• GET /summary - получить информацию
• GET /summary/all - все питомцы

🔔 <b>Уведомления:</b>
• ⚠️ Низкое здоровье (≤20)
• 🎉 Переход стадии
• 💀 Смерть питомца

🎯 <b>Стадии развития:</b>
• 🥚 Яйцо (10 мин)
• 👶 Детеныш (10 мин)
• 🧒 Подросток (10 мин)
• 👨 Взрослый (финал)
    """
    
    await message.answer(help_text, parse_mode="HTML")

@dp.message(Command("status"))
async def cmd_status(message: Message):
    """Обработчик команды /status"""
    user_id = str(message.from_user.id)
    
    status_text = f"""
📊 Статус вашего аккаунта:

🆔 User ID: <code>{user_id}</code>

🔗 API URL: http://127.0.0.1:3000

📱 Для проверки питомца:
<code>curl "http://127.0.0.1:3000/summary?user_id={user_id}"</code>

📋 Для всех питомцев:
<code>curl "http://127.0.0.1:3000/summary/all?user_id={user_id}"</code>
    """
    
    await message.answer(status_text, parse_mode="HTML")

@dp.message()
async def echo_message(message: Message):
    """Обработчик всех остальных сообщений"""
    await message.answer(
        "🤖 Я бот для уведомлений Telepets!\n\n"
        "Используйте /start для начала или /help для помощи."
    )

async def main():
    """Главная функция запуска бота"""
    logger.info("🚀 Запуск Telegram бота для Telepets...")
    logger.info(f"🤖 Бот: @{(await bot.me()).username}")
    logger.info("📱 Бот готов к получению уведомлений!")
    logger.info("💡 Отправьте /start в боте для начала")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main()) 