import os 
import datetime
import asyncio
import aiohttp
import logging
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import BufferedInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler

 # Добавьте эту строку в самый верх

# ... ваши остальные импорты ...
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID')) if os.getenv('ADMIN_ID') else None




logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- СПИСКИ ДАННЫХ ---
PREDICTIONS = [
    "Сегодня — идеальный день для завершения старых дел! ✅",
    "Вас ждет неожиданная, но очень приятная встреча. 😊",
    "Будьте внимательны к деталям — в них скрыт ключ к успеху. 🔑",
    # Добавьте остальные предсказания по аналогии...
]

BALL_ANSWERS = [
    "Бесспорно! ✅", "Предрешено. ✨", "Никаких сомнений. 👍", "Определенно да. ✔️",
    "Можешь быть уверен в этом. 😎", "Мне кажется — «да». 🤔", "Вероятнее всего. 📈",
    # Добавьте остальные ответы по аналогии...
]

# --- СОСТОЯНИЯ ---
class BotStates(StatesGroup):
    waiting_for_message = State()  # Для рассылки
    waiting_for_ball_question = State()  # Для шара желаний

# --- ЛОГИКА БАЗЫ ---
def get_users():
    try:
        with open("users.txt", "r") as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []

def save_user(user_id):
    users = get_users()
    if str(user_id) not in users:
        with open("users.txt", "a") as f:
            f.write(f"{user_id}\n")

# --- ФУНКЦИЯ АВТО-РАССЫЛКИ ---
async def send_daily_prediction():
    users = get_users()
    prediction = random.choice(PREDICTIONS)
    for user_id in users:
        try:
            await bot.send_message(user_id, f"Доброе утро! ✨ Твое предсказание на сегодня:\n\n{prediction}")
            await asyncio.sleep(0.05)
        except Exception as e:
            logging.error(f"Не удалось отправить предсказание пользователю {user_id}: {e}")
            continue

# --- КЛАВИАТУРЫ ---
def main_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🔮 Предсказание"), types.KeyboardButton(text="🎱 Шар Желаний"))
    builder.row(types.KeyboardButton(text="🖼 Картинка"), types.KeyboardButton(text="ℹ️ Инфо"))
    builder.row(types.KeyboardButton(text="⚙️ Админка"))
    return builder.as_markup(resize_keyboard=True)

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    save_user(message.from_user.id)
    await message.answer(f"Привет, {message.from_user.first_name}! 🌟\nЯ твой магический помощник. Каждое утро я буду присылать тебе предсказание!", reply_markup=main_kb())

@dp.message(F.text == "🔮 Предсказание")
async def get_daily(message: types.Message):
    prediction = random.choice(PREDICTIONS)
    await message.answer(f"✨ **Твое предсказание:**\n\n{prediction}", parse_mode="Markdown")

@dp.message(F.text == "🎱 Шар Желаний")
async def ball_start(message: types.Message, state: FSMContext):
    await message.answer("🎱 Сосредоточься на своем вопросе, на который можно ответить 'Да' или 'Нет', и напиши его мне:")
    await state.set_state(BotStates.waiting_for_ball_question)

@dp.message(BotStates.waiting_for_ball_question)
async def ball_answer(message: types.Message, state: FSMContext):
    answer = random.choice(BALL_ANSWERS)
    await message.answer(f"🔮 Шар долго вращался и говорит:\n\n**{answer}**", parse_mode="Markdown")
    await state.clear()

@dp.message(F.text == "ℹ️ Инфо")
async def about(message: types.Message):
    await message.answer("Я бот Nina1978! Умею давать предсказания и отвечать на вопросы Шаром Судьбы. 🎱")

@dp.message(F.text == "⚙️ Админка")
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(f"Количество пользователей: {len(get_users())}")
    else:
        await message.answer("Доступ закрыт. ❌")

@dp.message(F.text == "🖼 Картинка")
async def send_image(message: types.Message):
    n = random.randint(1, 1000)
    url = f"https://loremflickr.com/800/600/all?lock={n}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    photo = BufferedInputFile(content, filename="image.jpg")
                    await message.answer_photo(photo=photo, caption="Вот твое фото! 🖼")
                else:
                    await message.answer("Не удалось загрузить изображение, попробуй позже.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при загрузке изображения: {e}")

# --- ЗАПУСК ---
async def main():
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(send_daily_prediction, "cron", hour=12, minute=0)
    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Выход")
