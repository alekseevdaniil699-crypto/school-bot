import asyncio
import logging
import datetime
import os
from pathlib import Path
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

# ========== НАСТРОЙКА ПУТЕЙ ==========
# Получаем путь к папке, где лежит bot.py
BASE_DIR = Path(__file__).parent

# Загружаем переменные окружения из файла .env (если он есть)
load_dotenv(BASE_DIR / ".env")

# ========== ТОКЕН ==========
# Берём токен из переменных окружения (безопасно для хостинга)
TOKEN = os.getenv("BOT_TOKEN")

# Проверка: если токен не найден
if not TOKEN:
    raise ValueError("❌ Токен не найден! Создай файл .env и добавь BOT_TOKEN=твой_токен")

# Минимум логов
logging.basicConfig(level=logging.ERROR)

# Создаем объекты бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ========== ХРАНИЛИЩЕ ДЛЯ ФОТО РАСПИСАНИЯ ==========
# Для хранения фото можно использовать файл (опционально)
PHOTO_CACHE_FILE = BASE_DIR / "saved_photos.json"
saved_schedule_photos = {}

# ========== РАСПИСАНИЕ УРОКОВ ==========
SCHEDULE_DATA = {
    "понедельник": "📅 Расписание на Понедельник:\n\n1️⃣ \n2️⃣ Русский\n3️⃣ История\n4️⃣ История\n5️⃣ Математика\n6️⃣ Математика",
    "вторник": "📅 Расписание на Вторник:\n\n1️⃣ Общество\n2️⃣ Общество\n3️⃣ Биология\n4️⃣ Английский\n5️⃣ Химия\n6️⃣ Физра",
    "среда": "📅 Расписание на Среду:\n\n1️⃣ Русский\n2️⃣ Математика\n3️⃣ Математика\n4️⃣ Английский\n5️⃣ Кл.час\n6️⃣ Литература\n7️⃣ Семьевед",
    "четверг": "📅 Расписание на Четверг:\n\n1️⃣ Кл.час\n2️⃣ Английский\n3️⃣ Общество\n4️⃣ Общество\n5️⃣ География\n6️⃣ Физра",
    "пятница": "📅 Расписание на Пятницу:\n\n1️⃣ Литература\n2️⃣ Физика\n3️⃣ Физика\n4️⃣ Информатика\n5️⃣ Математика\n6️⃣ Математика",
    "суббота": "📅 Расписание на Субботу:\n\n1️⃣ Математика\n2️⃣ Математика\n3️⃣ Физра",
    "воскресенье": "🎉 Выходной день! Отдыхай!"
}

# ========== РАСПИСАНИЕ ЗВОНКОВ ==========
BELLS_SCHEDULE_WEEKDAYS = (
    "⏰ **РАСПИСАНИЕ ЗВОНКОВ (Будни)**\n\n"
    "1️⃣ урок: 8:00 - 8:40\n"
    "2️⃣ урок: 8:45 - 9:25\n"
    "3️⃣ урок: 9:30 - 10:10\n"
    "4️⃣ урок: 10:15 - 10:55\n"
    "5️⃣ урок: 11:00 - 11:40\n"
    "6️⃣ урок: 11:45 - 12:25\n"
    "7️⃣ урок: 12:30 - 13:10\n"
)

BELLS_SCHEDULE_SATURDAY = (
    "⏰ **РАСПИСАНИЕ ЗВОНКОВ (Суббота)**\n\n"
    "1️⃣ урок: 8:00 - 8:40\n"
    "2️⃣ урок: 8:45 - 9:25\n"
    "3️⃣ урок: 9:30 - 10:10\n"
    "4️⃣ урок: 10:15 - 10:55\n"
    "5️⃣ урок: 11:00 - 11:40\n"
    "6️⃣ урок: 11:45 - 12:25\n"
    "7️⃣ урок: 12:30 - 13:10\n"
)

# ========== ФУНКЦИИ СТАТУСА ==========

def get_time_until_school_start():
    now = datetime.datetime.now()
    school_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
    if now > school_start:
        school_start = school_start + datetime.timedelta(days=1)
    diff = school_start - now
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    seconds = diff.seconds % 60
    return hours, minutes, seconds

def get_time_until_vacation():
    today = datetime.datetime.now().date()
    vacation_start = datetime.date(2026, 5, 27)
    diff = vacation_start - today
    return diff.days

# ========== КЛАВИАТУРЫ ==========

def get_main_keyboard():
    button_1 = KeyboardButton(text="📅 Расписание уроков")
    button_2 = KeyboardButton(text="⏰ Расписание звонков")
    button_3 = KeyboardButton(text="📷 Фото расписания")
    button_4 = KeyboardButton(text="📊 Статус")
    button_5 = KeyboardButton(text="ℹ️ Помощь")
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1, button_2], [button_3, button_4], [button_5]],
        resize_keyboard=True
    )
    return keyboard

def get_bells_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Будни (пн-пт)", callback_data="bells_weekdays")
    builder.button(text="📆 Суббота", callback_data="bells_saturday")
    builder.button(text="◀️ Назад в меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()

def get_days_keyboard():
    builder = InlineKeyboardBuilder()
    days = [
        ("Пн", "monday"), ("Вт", "tuesday"), ("Ср", "wednesday"),
        ("Чт", "thursday"), ("Пт", "friday"), ("Сб", "saturday"),
        ("Вс", "sunday")
    ]
    for day_name, day_code in days:
        builder.button(text=day_name, callback_data=day_code)
    builder.adjust(4, 3)
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back"))
    return builder.as_markup()

def get_photo_days_keyboard():
    builder = InlineKeyboardBuilder()
    days = [
        ("Пн", "photo_monday"), ("Вт", "photo_tuesday"), ("Ср", "photo_wednesday"),
        ("Чт", "photo_thursday"), ("Пт", "photo_friday"), ("Сб", "photo_saturday"),
        ("Вс", "photo_sunday"), ("📋 Общее", "photo_general")
    ]
    for day_name, day_code in days:
        builder.button(text=day_name, callback_data=day_code)
    builder.adjust(4, 4)
    builder.row(InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_main"))
    return builder.as_markup()

# ========== ОБРАБОТЧИКИ КОМАНД ==========

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я школьный бот-помощник!\n"
        "Выбери нужный раздел в меню 👇",
        reply_markup=get_main_keyboard() if message.chat.type == "private" else None
    )

@dp.message(Command("lessons"))
async def cmd_lessons(message: types.Message):
    await message.answer("📅 Выбери день:", reply_markup=get_days_keyboard())

@dp.message(Command("bells"))
async def cmd_bells(message: types.Message):
    await message.answer(
        "⏰ Выбери день недели:",
        reply_markup=get_bells_keyboard()
    )

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    h, m, s = get_time_until_school_start()
    days = get_time_until_vacation()
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    
    if days < 0:
        response = f"⏰ Время: {current_time}\n\n🏫 До школы: {h} ч {m} мин {s} сек\n🎉 Каникулы уже идут! 🎉"
    else:
        response = f"⏰ Время: {current_time}\n\n🏫 До школы: {h} ч {m} мин {s} сек\n🎉 До каникул: {days} дней"
    
    await message.answer(response)

@dp.message(Command("schedule_photo"))
async def cmd_schedule_photo(message: types.Message):
    await message.answer("📷 Выбери день:", reply_markup=get_photo_days_keyboard())

# ========== ОБРАБОТЧИК СООБЩЕНИЙ ИЗ ГРУППЫ (АВТО-ОПРЕДЕЛЕНИЕ ДНЯ) ==========

@dp.message()
async def handle_all_messages(message: types.Message):
    # Сообщения из группы — только сохраняем фото
    if message.chat.type in ["group", "supergroup", "channel"]:
        if message.photo:
            photo = message.photo[-1]
            file_id = photo.file_id
            
            # Определяем, какой сегодня день недели
            today = datetime.datetime.now().weekday()
            
            # Расписание присылают на следующий день
            next_day = (today + 1) % 7
            
            # Сопоставляем номер дня с названием для сохранения
            day_mapping = {
                0: "photo_monday",
                1: "photo_tuesday",
                2: "photo_wednesday",
                3: "photo_thursday",
                4: "photo_friday",
                5: "photo_saturday",
                6: "photo_sunday"
            }
            
            day_code = day_mapping.get(next_day, "photo_general")
            saved_schedule_photos[day_code] = file_id
            
            day_names_ru = {
                0: "понедельник", 1: "вторник", 2: "среда",
                3: "четверг", 4: "пятница", 5: "суббота", 6: "воскресенье"
            }
            day_name_ru = day_names_ru.get(next_day, "неизвестный день")
            
            print(f"✅ Сохранено фото расписания на {day_name_ru}")
            return
        
        elif message.document:
            saved_schedule_photos["photo_general"] = message.document.file_id
            print("✅ Сохранён документ с расписанием")
            return
        
        return
    
    # ========== ЛИЧНЫЕ СООБЩЕНИЯ (КНОПКИ) ==========
    if message.text == "📅 Расписание уроков":
        await cmd_lessons(message)
    elif message.text == "⏰ Расписание звонков":
        await cmd_bells(message)
    elif message.text == "📷 Фото расписания":
        await cmd_schedule_photo(message)
    elif message.text == "📊 Статус":
        await cmd_status(message)
    elif message.text == "ℹ️ Помощь":
        await message.answer(
            "ℹ️ Кнопки:\n"
            "• 📅 Расписание уроков — текст по дням\n"
            "• ⏰ Расписание звонков — выбор будни/суббота\n"
            "• 📷 Фото расписания — фото из группы\n"
            "• 📊 Статус — время до школы и каникул"
        )
    else:
        await message.answer("Используй кнопки внизу 👇", reply_markup=get_main_keyboard())

# ========== ОБРАБОТЧИКИ НАЖАТИЙ ==========

@dp.callback_query(lambda c: c.data and c.data.startswith("bells_"))
async def handle_bells_choice(callback: types.CallbackQuery):
    await callback.answer()
    
    if callback.data == "bells_weekdays":
        await callback.message.edit_text(BELLS_SCHEDULE_WEEKDAYS, parse_mode="Markdown")
    elif callback.data == "bells_saturday":
        await callback.message.edit_text(BELLS_SCHEDULE_SATURDAY, parse_mode="Markdown")
    
    await callback.message.answer("Вернуться в меню:", reply_markup=get_main_keyboard())

@dp.callback_query(lambda c: c.data and c.data == "back_to_main")
async def handle_back_to_main(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("Главное меню:", reply_markup=get_main_keyboard())

@dp.callback_query(lambda c: c.data and not c.data.startswith(("photo_", "bells_")) and c.data != "back_to_main")
async def handle_days(callback: types.CallbackQuery):
    await callback.answer()
    
    if callback.data == "back":
        await callback.message.delete()
        await callback.message.answer("Главное меню:", reply_markup=get_main_keyboard())
        return
    
    day_map = {
        "monday": "понедельник", "tuesday": "вторник",
        "wednesday": "среда", "thursday": "четверг",
        "friday": "пятница", "saturday": "суббота", "sunday": "воскресенье"
    }
    
    day_name = day_map.get(callback.data, "понедельник")
    response = SCHEDULE_DATA.get(day_name, "Нет расписания")
    
    try:
        await callback.message.edit_text(response)
    except Exception:
        pass
    
    await callback.message.answer("Выбери другой день:", reply_markup=get_days_keyboard())

@dp.callback_query(lambda c: c.data and c.data.startswith("photo_"))
async def handle_photo_callbacks(callback: types.CallbackQuery):
    await callback.answer()
    
    if callback.data in saved_schedule_photos:
        day_names = {
            "photo_monday": "понедельник", "photo_tuesday": "вторник",
            "photo_wednesday": "среда", "photo_thursday": "четверг",
            "photo_friday": "пятница", "photo_saturday": "суббота",
            "photo_sunday": "воскресенье", "photo_general": "общее расписание"
        }
        day_name = day_names.get(callback.data, "расписание")
        
        await callback.message.answer_photo(
            photo=saved_schedule_photos[callback.data],
            caption=f"📷 Фото расписания на {day_name}"
        )
    else:
        await callback.message.answer(
            f"❌ Нет фото для этого дня.\n\n"
            f"📌 Отправь фото в группу, и бот сам определит, на какой день оно"
        )
    
    await callback.message.answer("Выбери другой день:", reply_markup=get_photo_days_keyboard())

# ========== ЗАПУСК БОТА ==========

async def main():
    print("🚀 Бот запущен!")
    print(f"📁 Базовая директория: {BASE_DIR}")
    print("✅ Расписание уроков")
    print("✅ Расписание звонков (будни и суббота)")
    print("✅ Фото расписания — бот сам определяет день по дате отправки")
    print("✅ Статус (время до школы и каникул)")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
