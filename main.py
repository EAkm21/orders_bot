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
            [KeyboardButton(text="Оформление заказа.")],
        ],
        resize_keyboard=True
    )
    await message.answer("Добро пожаловать в MyPoints! Чем можем Вам помочь?", reply_markup=keyboard)

@dp.message(Command(commands=['rate']))
async def process_review(message: types.Message):
     await message.answer("Скоро здесь появится Ваш отзыв.")

@dp.message(Command(commands=['help']))
async def process_help(message: types.Message):

       await message.answer("📜 Документация:\n"
                            "1️⃣ Выберите университет\n"
                            "2️⃣ Выберите свою специальность\n"
                            "3️⃣ Укажите дисциплину и тип работы\n"
                            "4️⃣ Данные отправляются администратору для подтверждения заказа\n"
                            "5️⃣ Администратор свяжется с вами для оплаты и передачи заказа исполнителям.")

@dp.message(Command(commands=['price']))
async def price_list(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Реферат", callback_data='ref')],
        [InlineKeyboardButton(text="📝 Эссе", callback_data='es')],
        [InlineKeyboardButton(text="📊 Презентация", callback_data='pres')],
        [InlineKeyboardButton(text="📚 Курсовая", callback_data='course')],
        [InlineKeyboardButton(text='📚 Самостоятельная | 📑 Контрольная | 🎓 Экзамен', callback_data='sm')]
    ])
    await message.answer("Прейскурант услуг.", reply_markup=keyboard)

@dp.callback_query()
async def prices_callback(callback: CallbackQuery, state: FSMContext):
    if callback.data not in ['ref', 'es', 'pres', 'course', 'sm']:
        # Если это не колбэк с ценами, пропускаем обработку
        return
    user_data = await state.get_data()
    last_message_id = user_data.get("last_message_id")  # Получаем ID последнего сообщения

    # Удаляем предыдущее сообщение, если оно есть
    if last_message_id:
        try:
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Не удалось удалить сообщение: {e}")

    message = None  # Инициализируем переменную перед условиями

    price_texts = {
        'ref': "📖 *Рефераты на заказ*\n\n"
               "✅ *Реферат от 8 дней* — _Оригинальность: от 60%_ — 💰 *2500 руб*\n"
               "✅ *Реферат от 4-7 дней* — _Оригинальность: от 60%_ — 💰 *3000 руб*\n"
               "✅ *Реферат от 1-3 дней* — _Оригинальность: от 60%_ — 💰 *4000 руб*\n"
               "🔥 *Экспресс (1 день)* — _Оригинальность: от 60%_ — 💰 *6000 руб*\n\n"
               "📊 *Реферат + презентация*:\n"
               "   - от 8 дней — 💰 *3000 руб*\n"
               "   - от 4-7 дней — 💰 *3700 руб*\n"
               "   - от 1-3 дней — 💰 *5000 руб*\n"
               "   - 🚀 *Экспресс (1 день)* — 💰 *7000 руб*\n",

        'es': "📝 *Эссе на заказ*\n\n"
              "✅ *Эссе от 8 дней* — _Оригинальность: от 60%_ — 💰 *1250 руб*\n"
              "✅ *Эссе от 4-7 дней* — _Оригинальность: от 60%_ — 💰 *1500 руб*\n"
              "✅ *Эссе от 1-3 дней* — _Оригинальность: от 60%_ — 💰 *2000 руб*\n"
              "🔥 *Экспресс (1 день)* — _Оригинальность: от 60%_ — 💰 *2500 руб*\n",

        'pres': "📊 *Презентации на заказ*\n\n"
                "🎨 *Объем: 5-10 слайдов*:\n"
                "   - от 8 дней — 💰 *500 руб*\n"
                "   - от 4-7 дней — 💰 *700 руб*\n"
                "   - от 1-3 дней — 💰 *1000 руб*\n"
                "   - 🚀 *Экспресс (1 день)* — 💰 *2000 руб*\n",

        'course': "📚 *Курсовые работы*\n\n"
                  "✅ *От 15 дней* — _Оригинальность: от 60%_ — 💰 *5000 руб*\n"
                  "✅ *От 5-14 дней* — _Оригинальность: от 60%_ — 💰 *6500 руб*\n"
                  "✅ *От 1-4 дней* — _Оригинальность: от 60%_ — 💰 *9000 руб*\n"
                  "🔥 *Экспресс (1 день)* — _Оригинальность: от 60%_ — 💰 *15000 руб*\n",

        'sm': "⚡ *Срочные работы*\n\n"
              "✍ Данный тип работ выполняется в день написания и согласовывается индивидуально с исполнителем."
    }

    if callback.data in price_texts:
        message = await callback.message.answer(price_texts[callback.data])

    if message:
        await state.update_data(last_message_id=message.message_id)  # Обновляем состояние только если сообщение было отправлено

    await callback.answer()

@dp.message(StateFilter(None))
async def process_choose_university(message: types.Message, state: FSMContext):
    if message.text == "Оформление заказа.":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="REU", callback_data="reu_btn")],
            [InlineKeyboardButton(text="HSE", callback_data="hse_btn")],
            [InlineKeyboardButton(text="MSU", callback_data="msu_btn")]
        ])
        await message.answer("Вы начали процесс выбора университета. Выберите свой университет:", reply_markup=keyboard)
    await state.set_state(OrderState.waiting_for_task)

@dp.callback_query(lambda c: c.data in ['reu_btn', 'hse_btn', 'msu_btn'])
async def process_callback(callback: CallbackQuery, state: FSMContext):
    data = callback.data
    logging.debug(f"Получен callback: {data}")
    if data in ["reu_btn", "hse_btn", "msu_btn"]:
        kkeyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ВШЭиБ", callback_data=f"{data}_economy")],
            [InlineKeyboardButton(text="ВШКМиС, Форсайт", callback_data=f"{data}_cs")],
            [InlineKeyboardButton(text="ВШСГН", callback_data=f"{data}_sgn")],
            [InlineKeyboardButton(text="ВШП", callback_data=f"{data}_pr")],
            [InlineKeyboardButton(text="ВШФ", callback_data=f"{data}_fin")],
            [InlineKeyboardButton(text="ВШМ", callback_data=f"{data}_men")],
            [InlineKeyboardButton(text="ВШКИ", callback_data=f"{data}_ind")],
            [InlineKeyboardButton(text='ВИШ"НМиТ"', callback_data=f"{data}_tech")],
            [InlineKeyboardButton(text="ИПАМ", callback_data=f"{data}_med")],
            [InlineKeyboardButton(text="Капитаны", callback_data=f"{data}_cap")]
        ])
        await callback.message.edit_text("Выберите свою специальность:", reply_markup=keyboard)

    elif (data.endswith("_economy") or data.endswith("_cs") or data.endswith("_sgn") or data.endswith("_pr")
          or data.endswith("_fin") or data.endswith("_men") or data.endswith("_ind") or data.endswith("_tech")
          or data.endswith("_med") or data.endswith("_cap")):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Математика", callback_data=f"{data}_math")],
            [InlineKeyboardButton(text="Программирование", callback_data=f"{data}_prog")],
            [InlineKeyboardButton(text="Прочее", callback_data=f"{data}_other")]
        ])
        await callback.message.edit_text("Выберите дисциплину:", reply_markup=keyboard)

    elif data.endswith("_math") or data.endswith("_prog") or data.endswith("_other"):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Эссе", callback_data=f"{data}_essay")],
            [InlineKeyboardButton(text="Реферат", callback_data=f"{data}_report")],
            [InlineKeyboardButton(text="Презентация", callback_data=f"{data}_presentation")],
            [InlineKeyboardButton(text="Самостоятельные и контрольные работы", callback_data=f"{data}_independ")],
            [InlineKeyboardButton(text="Курсовая работа", callback_data=f"{data}_course")]
        ])
        await callback.message.edit_text("Выберите тип работы:", reply_markup=keyboard)

    elif any(data.endswith(suffix) for suffix in ["_essay", "_report", "_presentation", "_independ", "_course"]):
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

if __name__ == "__main__":
    dp.run_polling(bot)

