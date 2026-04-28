import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# ВАШИ ДАННЫЕ
TOKEN = "8768485744:AAHrHcv1vKWyDm8cWIn59jiRqnO41YYOc3o"
ADMIN_ID = 6147800990  # Ваш ID теперь вписан правильно

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Состояния для рассылки
class BroadcastState(StatesGroup):
    waiting_for_message = State()

# --- Логика базы пользователей (в файле) ---
def save_user(user_id):
    try:
        users = get_users()
        if str(user_id) not in users:
            with open("users.txt", "a") as f:
                f.write(f"{user_id}\n")
    except Exception as e:
        print(f"Ошибка сохранения: {e}")

def get_users():
    try:
        with open("users.txt", "r") as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []

# --- Клавиатуры ---
def main_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🖼 Картинка"))
    builder.row(types.KeyboardButton(text="ℹ️ Инфо"), types.KeyboardButton(text="⚙️ Админка"))
    return builder.as_markup(resize_keyboard=True)

def admin_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📢 Рассылка", callback_data="start_broadcast"))
    return builder.as_markup()

# --- Обработчики ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    save_user(message.from_user.id)
    await message.answer(f"Привет, {message.from_user.first_name}! Бот запущен.", reply_markup=main_kb())

@dp.message(F.text == "ℹ️ Инфо")
async def about(message: types.Message):
    await message.answer("Я бот Nina1978, работаю на Linux через aiogram 3!")

@dp.message(F.text == "⚙️ Админка")
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Панель управления:", reply_markup=admin_kb())
    else:
        await message.answer("У вас нет прав доступа. ❌")

@dp.message(F.text == "🖼 Картинка")
async def send_image(message: types.Message):
    await message.answer_photo(photo="https://picsum.photos", caption="Вот случайное фото!")

# --- Рассылка (только для вас) ---
@dp.callback_query(F.data == "start_broadcast", F.from_user.id == ADMIN_ID)
async def broadcast_prompt(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите текст рассылки:")
    await state.set_state(BroadcastState.waiting_for_message)
    await callback.answer()

@dp.message(BroadcastState.waiting_for_message, F.from_user.id == ADMIN_ID)
async def broadcast_send(message: types.Message, state: FSMContext):
    users = get_users()
    count = 0
    for user_id in users:
        try:
            await bot.send_message(chat_id=user_id, text=message.text)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    await message.answer(f"✅ Готово! Сообщение получили {count} человек(а).")
    await state.clear()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")

