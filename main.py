import datetime 
import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- КОНФИГУРАЦИЯ ---
TOKEN = 
ADMIN_ID = 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- СПИСКИ ДАННЫХ ---
PREDICTIONS = [
    "Сегодня — идеальный день для завершения старых дел! ✅",
    "Вас ждет неожиданная, но очень приятная встреча. 😊",
    "Будьте внимательны к деталям — в них скрыт ключ к успеху. 🔑",
    "Звезды советуют вам отдохнуть. Позвольте себе чашечку кофе! ☕",
    "Ваша энергия сегодня способна свернуть горы. Действуйте! 💪",
    "Не бойтесь рисковать — удача на стороне смелых. 🎲",
    "Маленький сюрприз поднимет вам настроение вечером. ✨",
    "Самое время изучить что-то новое в Linux! 🐧",
    "Сегодняшний день принесет ответы на важные вопросы. 💡",
    "Будьте открыты для новых знакомств, одно из них станет важным. 🤝",
    "Ваше финансовое положение скоро улучшится. 💰",
    "Доверяйте своей интуиции, она вас не подведет. 🧠",
    "Кто-то очень ждет вашего звонка или сообщения. 📱",
    "Сегодня удача будет преследовать вас по пятам! 🍀",
    "Ваша улыбка — главный ключ к решению проблем сегодня. 😁",
    "Проведите вечер в тишине, это даст вам новые силы. 🧘",
    "Сегодня отличный день, чтобы начать заниматься спортом. 🏃",
    "Вас ждет успех в делах, которые вы долго откладывали. 📈",
    "Будьте добрее к окружающим, и мир ответит вам тем же. ❤️",
    "Смело воплощайте в жизнь свои самые безумные идеи! 🌈",
    "Сегодня день приятных покупок и обновок. 🛍"
]

BALL_ANSWERS = [
    "Бесспорно! ✅", "Предрешено. ✨", "Никаких сомнений. 👍", "Определенно да. ✔️",
    "Можешь быть уверен в этом. 😎", "Мне кажется — «да». 🤔", "Вероятнее всего. 📈",
    "Хорошие перспективы. 🌤", "Знаки говорят — «да». 🌟", "Да. ✅",
    "Пока не ясно, попробуй снова. 🔄", "Спроси позже. ⏳", "Лучше не рассказывать сейчас. 🙊",
    "Сейчас нельзя предсказать. 🌫", "Сконцентрируйся и спроси опять. 🧘",
    "Даже не думай. ❌", "Мой ответ — «нет». 👎", "По моим данным — «нет». 📉",
    "Перспективы не очень хорошие. ☁️", "Весьма сомнительно. 🤨"
]

# --- СОСТОЯНИЯ ---
class BotStates(StatesGroup):
    waiting_for_message = State() # Для рассылки
    waiting_for_ball_question = State() # Для шара желаний

# --- ЛОГИКА БАЗЫ ---
def get_users():
    try:
        with open("users.txt", "r") as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError: return []

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
        except Exception: continue

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
    await message.answer(f"✨ **Твое предсказание:**\n\n{random.choice(PREDICTIONS)}", parse_mode="Markdown")

# Логика Волшебного Шара
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
    await message.answer_photo(photo="https://picsum.photos", caption="Случайный момент вдохновения! 🖼")

# --- ЗАПУСК ---
async def main():
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(send_daily_prediction, "cron", hour=9, minute=0)
    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Выход")
