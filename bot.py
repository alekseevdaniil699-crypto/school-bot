import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ТВОЙ ТОКЕН
TOKEN = "8782536892:AAGtM2a-NP-zN--xpehjQqjWvwzNMGfm0rw"

# Отключаем лишние логи
logging.basicConfig(level=logging.ERROR)

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
BELLS_SCHEDULE = (
    "⏰ РАСПИСАНИЕ ЗВОНКОВ:\n\n"
    "1️⃣ урок: 8:00 - 8:40 (5 мин)\n"
    "2️⃣ урок: 8:45 - 9:25 (15 мин)\n"
    "3️⃣ урок: 9:40 - 10:20 (15 мин)\n"
    "4️⃣ урок: 10:35 - 11:15 (5 мин)\n"
    "5️⃣ урок: 11:20 - 12:00 (5 мин)\n"
    "6️⃣ урок: 12:05 - 12:45 (5 мин)\n"
    "7️⃣ урок: 12:50 - 13:30"
)

# ========== КЛАВИАТУРЫ ==========
def get_main_keyboard():
    button_1 = KeyboardButton(text="📅 Расписание уроков")
    button_2 = KeyboardButton(text="⏰ Расписание звонков")
    button_3 = KeyboardButton(text="ℹ️ Помощь")
    return ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_2], [button_3]],
        resize_keyboard=True
    )

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

# ========== ЗАПУСК ==========
async def main():
    print("🚀 Запуск бота...")
    
    # Создаем бота
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    # Проверяем подключение
    try:
        me = await bot.get_me()
        print(f"✅ Бот подключен: @{me.username}")
    except Exception as e:
        print(f"\n❌ НЕ УДАЛОСЬ ПОДКЛЮЧИТЬСЯ К TELEGRAM!")
        print(f"Ошибка: {e}")
        print("\n💡 РЕШЕНИЕ:")
        print("1. Включи VPN на компьютере")
        print("2. Раздай интернет с телефона с VPN")
        print("3. Для защиты используй скриншоты")
        return
    
    # Обработчики
    @dp.message(Command("start"))
    async def start(message: types.Message):
        await message.answer(
            "👋 Привет! Я школьный бот-помощник!\nВыбери раздел в меню 👇",
            reply_markup=get_main_keyboard()
        )
    
    @dp.message(Command("lessons"))
    async def lessons(message: types.Message):
        await message.answer("📅 Выбери день:", reply_markup=get_days_keyboard())
    
    @dp.message(Command("bells"))
    async def bells(message: types.Message):
        await message.answer(BELLS_SCHEDULE)
    
    @dp.callback_query()
    async def days(callback: types.CallbackQuery):
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
        except:
            pass
        await callback.message.answer("Выбери другой день:", reply_markup=get_days_keyboard())
    
    @dp.message()
    async def buttons(message: types.Message):
        if message.text == "📅 Расписание уроков":
            await lessons(message)
        elif message.text == "⏰ Расписание звонков":
            await bells(message)
        elif message.text == "ℹ️ Помощь":
            await message.answer("ℹ️ Нажми кнопку с расписанием")
        else:
            await message.answer("Используй кнопки 👇", reply_markup=get_main_keyboard())
    
    print("✅ Бот готов! Ожидаю команды...")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен")