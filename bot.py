#!/usr/bin/env python3
"""
Простой Telegram бот для получения уведомлений от Telepets.
Запускается отдельно от основного API сервера.
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import aiohttp
from fastapi import FastAPI
import uvicorn
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен бота
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_PUBLIC_URL = os.getenv("API_PUBLIC_URL", "http://127.0.0.1:3000")

if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
    logger.error("❌ TELEGRAM_BOT_TOKEN не установлен в .env файле!")
    logger.info("📝 Создайте бота через @BotFather и добавьте токен в .env")
    exit(1)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Небольшое HTTP‑приложение для Render (healthcheck)
_http_app = FastAPI()

@_http_app.get("/health")
async def _health():
    return {"status": "ok"}

def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статус", callback_data="status")],
        [InlineKeyboardButton(text="🐾 Питомцы", callback_data="pets")],
        [InlineKeyboardButton(text="💰 Кошелёк", callback_data="wallet")],
    ])


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
    
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=main_keyboard())

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

🔗 API URL: {API_PUBLIC_URL}

📱 Для проверки питомца:
<code>curl "{API_PUBLIC_URL}/summary?user_id={user_id}"</code>

📋 Для всех питомцев:
<code>curl "{API_PUBLIC_URL}/summary/all?user_id={user_id}"</code>
    """
    
    await message.answer(status_text, parse_mode="HTML", reply_markup=main_keyboard())


async def fetch_json(session: aiohttp.ClientSession, url: str, params: dict | None = None):
    try:
        async with session.get(url, params=params, timeout=20) as resp:
            return await resp.json()
    except Exception as e:
        logger.error(f"HTTP error: {e}")
        return None


@dp.callback_query()
async def on_cb(query: CallbackQuery):
    user_id = str(query.from_user.id)
    data = query.data or ""
    async with aiohttp.ClientSession() as session:
        if data == "status":
            url = f"{API_PUBLIC_URL}/summary"
            js = await fetch_json(session, url, params={"user_id": user_id})
            if not js:
                await query.message.edit_text("⚠️ Не удалось получить статус.", reply_markup=main_keyboard())
                return
            status = js.get("status")
            total = js.get("total_pets") or js.get("total_pets", 0)
            alive = js.get("alive_pets", 0)
            coins = (js.get("wallet") or {}).get("coins", 0)
            txt = (
                f"📊 <b>Статус</b>: {status}\n"
                f"🐾 Питомцев: {total} (живых: {alive})\n"
                f"💰 Монеты: {coins}"
            )
            await query.message.edit_text(txt, parse_mode="HTML", reply_markup=main_keyboard())
            await query.answer()
            return
        
        if data == "pets":
            url = f"{API_PUBLIC_URL}/summary/all"
            js = await fetch_json(session, url, params={"user_id": user_id})
            if not js:
                await query.message.edit_text("⚠️ Не удалось получить список питомцев.", reply_markup=main_keyboard())
                return
            pets = js.get("pets", [])
            if not pets:
                await query.message.edit_text("🫥 У вас пока нет питомцев.", reply_markup=main_keyboard())
                await query.answer()
                return
            lines = ["🐾 <b>Ваши питомцы</b>:"]
            for p in pets[:10]:
                lines.append(f"• {p.get('name')} — {p.get('state')} ({p.get('health')}/100)")
            await query.message.edit_text("\n".join(lines), parse_mode="HTML", reply_markup=main_keyboard())
            await query.answer()
            return

        if data == "wallet":
            url = f"{API_PUBLIC_URL}/economy/wallet/{user_id}"
            js = await fetch_json(session, url)
            if not js:
                await query.message.edit_text("⚠️ Не удалось получить кошелёк.", reply_markup=main_keyboard())
                return
            coins = js.get("coins", 0)
            total_earned = js.get("total_earned", 0)
            total_spent = js.get("total_spent", 0)
            txt = (
                f"💰 <b>Кошелёк</b>\n"
                f"Баланс: {coins}\n"
                f"Заработано: {total_earned}\n"
                f"Потрачено: {total_spent}"
            )
            await query.message.edit_text(txt, parse_mode="HTML", reply_markup=main_keyboard())
            await query.answer()
            return
    
    await query.answer()

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
        # Параллельно поднимаем лёгкий HTTP‑сервер, чтобы Render видел открытый порт
        port = int(os.getenv("PORT", "3001"))
        http_server = uvicorn.Server(uvicorn.Config(app=_http_app, host="0.0.0.0", port=port, log_level="info"))
        await asyncio.gather(
            dp.start_polling(bot),
            http_server.serve(),
        )
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main()) 