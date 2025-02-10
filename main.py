from aiogram.filters import Command
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv
import os

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")  # Убедитесь, что ADMIN_ID корректно загружается из .env

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=MemoryStorage())

class OrderState(StatesGroup):
    waiting_for_task = State()
    waiting_for_deadline = State()

@dp.message(Command(commands=['start']))
async def command_start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Выбор университета")],
            [KeyboardButton(text="Отзывы")],
            [KeyboardButton(text="Техническая поддержка")]
        ],
        resize_keyboard=True
    )
    await message.answer("Добро пожаловать в MyPoints! Чем можем Вам помочь?", reply_markup=keyboard)

@dp.message()
async def process_choose_university(message: types.Message):
    if message.text == "Выбор университета":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="REU", callback_data="reu_btn")],
            [InlineKeyboardButton(text="HSE", callback_data="hse_btn")],
            [InlineKeyboardButton(text="MSU", callback_data="msu_btn")]
        ])
        await message.answer("Вы начали процесс выбора университета. Выберите свой университет:", reply_markup=keyboard)

@dp.callback_query()
async def process_callback(callback: CallbackQuery, state: FSMContext):
    data = callback.data

    if data in ["reu_btn", "hse_btn", "msu_btn"]:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Экономика", callback_data=f"{data}_economy")],
            [InlineKeyboardButton(text="Информатика", callback_data=f"{data}_cs")],
            [InlineKeyboardButton(text="Юриспруденция", callback_data=f"{data}_law")]
        ])
        await callback.message.edit_text("Выберите свою специальность:", reply_markup=keyboard)

    elif data.endswith("_economy") or data.endswith("_cs") or data.endswith("_law"):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Математика", callback_data=f"{data}_math")],
            [InlineKeyboardButton(text="Программирование", callback_data=f"{data}_prog")],
            [InlineKeyboardButton(text="Философия", callback_data=f"{data}_philo")]
        ])
        await callback.message.edit_text("Выберите дисциплину:", reply_markup=keyboard)

    elif data.endswith("_math") or data.endswith("_prog") or data.endswith("_philo"):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Эссе", callback_data=f"{data}_essay")],
            [InlineKeyboardButton(text="Доклад", callback_data=f"{data}_report")],
            [InlineKeyboardButton(text="Презентация", callback_data=f"{data}_presentation")],
            [InlineKeyboardButton(text="Домашняя работа", callback_data=f"{data}_homework")],
            [InlineKeyboardButton(text="Лабораторная", callback_data=f"{data}_lab")]
        ])
        await callback.message.edit_text("Выберите тип работы:", reply_markup=keyboard)

    elif any(data.endswith(suffix) for suffix in ["_essay", "_report", "_presentation", "_homework", "_lab"]):
        await state.set_state(OrderState.waiting_for_task)
        await callback.message.answer("Введите текст задания:")

@dp.message(OrderState.waiting_for_task)
async def process_task_description(message: types.Message, state: FSMContext):
    await state.update_data(task=message.text)
    await state.set_state(OrderState.waiting_for_deadline)
    await message.answer("Введите дедлайн (в формате ДД.ММ.ГГГГ):")


@dp.message(OrderState.waiting_for_deadline)
async def process_deadline(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    deadline = message.text
    user = message.from_user
    order_text = (
        f"Новый заказ!\n"
        f"👤 Пользователь: {user.full_name} (@{user.username})\n"
        f"📄 Задание: {user_data['task']}\n"
        f"📆 Дедлайн: {deadline}"
    )
    await bot.send_message(ADMIN_ID, order_text)
    await message.answer("Ваш заказ отправлен администратору. Он свяжется с вами для обсуждения стоимости.")
    await state.clear()

@dp.message()
async def process_review(message: types.Message):
    if message.text == "Отзывы":
        await message.answer("Вот один из отзывов: 'Отличный сервис, помог с выбором университета!'")

@dp.message()
async def process_help(message: types.Message):
    if message.text == "Техническая поддержка":
        await message.answer("📜 Документация:\n"
                             "1️⃣ Выберите университет\n"
                             "2️⃣ Выберите свою специальность\n"
                             "3️⃣ Укажите дисциплину и тип работы\n"
                             "4️⃣ Данные отправляются администратору для подтверждения заказа\n"
                             "5️⃣ Администратор свяжется с вами для оплаты и передачи заказа исполнителям.")

if __name__ == "__main__":
    dp.run_polling(bot)

