import asyncio
import sqlite3
import os
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# ============================================
# LOGGING
# ============================================
logging.basicConfig(level=logging.INFO)

# ============================================
# TOKEN
# ============================================
BOT_TOKEN = "8965240923:AAGSgBJMdtOl4zCcgGUqW3RnXVPNoTCFvbE"

# ============================================
# SAYT LINKI
# ============================================
SAYT_LINKI = "https://nuriddin00009.github.io/kunlik.tizim_bot/"

# ============================================
# DATABASE
# ============================================
class Database:
    def __init__(self):
        try:
            self.conn = sqlite3.connect('finance.db')
            self.cursor = self.conn.cursor()
            self.create_tables()
            print("✅ Database ulandi!")
        except Exception as e:
            print(f"❌ Database xatosi: {e}")
    
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,
                amount REAL,
                category TEXT,
                description TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                card_name TEXT,
                card_number TEXT,
                balance REAL
            )
        ''')
        self.conn.commit()
        print("✅ Jadvallar yaratildi!")
    
    def add_user(self, user_id, username, first_name, last_name):
        self.cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        self.conn.commit()
    
    def add_transaction(self, user_id, type, amount, category, description):
        self.cursor.execute('''
            INSERT INTO transactions (user_id, type, amount, category, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, type, amount, category, description))
        self.conn.commit()
    
    def get_stats(self, user_id, days=1):
        date_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        self.cursor.execute('''
            SELECT type, SUM(amount) FROM transactions 
            WHERE user_id=? AND date >= ?
            GROUP BY type
        ''', (user_id, date_from))
        result = self.cursor.fetchall()
        income = 0
        expense = 0
        for row in result:
            if row[0] == 'kirim':
                income = row[1] or 0
            else:
                expense = row[1] or 0
        return income, expense
    
    def get_categories(self, user_id):
        self.cursor.execute('''
            SELECT category, type, SUM(amount) FROM transactions 
            WHERE user_id=?
            GROUP BY category, type
            ORDER BY SUM(amount) DESC
            LIMIT 10
        ''', (user_id,))
        return self.cursor.fetchall()
    
    def get_cards(self, user_id):
        self.cursor.execute('SELECT card_name, card_number, balance FROM cards WHERE user_id=?', (user_id,))
        return self.cursor.fetchall()
    
    def add_card(self, user_id, card_name, card_number, balance):
        self.cursor.execute('''
            INSERT INTO cards (user_id, card_name, card_number, balance)
            VALUES (?, ?, ?, ?)
        ''', (user_id, card_name, card_number, balance))
        self.conn.commit()

# ============================================
# DATABASE NI ISHGA TUSHIRISH
# ============================================
try:
    db = Database()
except Exception as e:
    print(f"❌ Database ishga tushmadi: {e}")
    exit()

# ============================================
# KEYBOARDS
# ============================================
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💰 Kirim"), KeyboardButton(text="💸 Chiqim")],
            [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="💳 Kartalar")],
            [KeyboardButton(text="📈 Budjet"), KeyboardButton(text="⚙️ Sozlamalar")],
            [KeyboardButton(text="🌐 Sayt"), KeyboardButton(text="🔄 Yangilash")]
        ],
        resize_keyboard=True
    )

def income_categories():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💰 Oylik maosh", callback_data="inc_maosh")],
            [InlineKeyboardButton(text="📈 Biznes", callback_data="inc_biznes")],
            [InlineKeyboardButton(text="🎁 Sovgʻa", callback_data="inc_sovga")],
            [InlineKeyboardButton(text="📌 Boshqa", callback_data="inc_boshqa")]
        ]
    )

def expense_categories():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Oziq-ovqat", callback_data="exp_ovqat")],
            [InlineKeyboardButton(text="🚕 Transport", callback_data="exp_transport")],
            [InlineKeyboardButton(text="🏠 Uy-joy", callback_data="exp_uy")],
            [InlineKeyboardButton(text="📱 Telefon", callback_data="exp_telefon")],
            [InlineKeyboardButton(text="💡 Kommunal", callback_data="exp_kommunal")],
            [InlineKeyboardButton(text="👕 Kiyim", callback_data="exp_kiyim")],
            [InlineKeyboardButton(text="💊 Salomatlik", callback_data="exp_salomatlik")],
            [InlineKeyboardButton(text="📚 Ta'lim", callback_data="exp_talim")],
            [InlineKeyboardButton(text="🎮 O'yin", callback_data="exp_oyin")],
            [InlineKeyboardButton(text="📌 Boshqa", callback_data="exp_boshqa")]
        ],
        row_width=2
    )

def stats_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Kunlik", callback_data="stats_day")],
            [InlineKeyboardButton(text="📈 Haftalik", callback_data="stats_week")],
            [InlineKeyboardButton(text="📉 Oylik", callback_data="stats_month")]
        ]
    )

def cards_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Karta qo'shish", callback_data="add_card")],
            [InlineKeyboardButton(text="📋 Kartalarim", callback_data="my_cards")]
        ]
    )

# ============================================
# WEB APP - SAYT TUGMASI (Open App uslubida) ✅
# ============================================
def web_app_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💰 Kirim"), KeyboardButton(text="💸 Chiqim")],
            [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="💳 Kartalar")],
            [KeyboardButton(text="📈 Budjet"), KeyboardButton(text="⚙️ Sozlamalar")],
            [
                KeyboardButton(
                    text="🚀 Open App",
                    web_app=WebAppInfo(url=SAYT_LINKI)
                )
            ],
            [KeyboardButton(text="🔄 Yangilash")]
        ],
        resize_keyboard=True
    )

# ============================================
# STATES
# ============================================
class IncomeStates(StatesGroup):
    amount = State()
    category = State()
    description = State()

class ExpenseStates(StatesGroup):
    amount = State()
    category = State()
    description = State()

class CardStates(StatesGroup):
    name = State()
    number = State()
    balance = State()

# ============================================
# BOT
# ============================================
try:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    print("✅ Bot yaratildi!")
except Exception as e:
    print(f"❌ Bot yaratishda xatolik: {e}")
    exit()

# ============================================
# HANDLERS
# ============================================

# START
@dp.message(Command("start"))
@dp.message(lambda m: m.text == "🔄 Yangilash")
async def cmd_start(message: types.Message, state: FSMContext):
    try:
        await state.clear()
        db.add_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name
        )
        await message.answer(
            f"👋 Assalomu alaykum, {message.from_user.first_name}!\n\n"
            f"💰 <b>kunlik.tizim</b> ga xush kelibsiz!\n\n"
            f"📊 Moliya tizimingizni boshqaring!\n"
            f"🚀 Saytni ochish uchun <b>'Open App'</b> tugmasini bosing.\n\n"
            f"Quyidagi menyudan tanlang:",
            reply_markup=web_app_menu(),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

# ============================================
# KIRIM
# ============================================
@dp.message(lambda m: m.text == "💰 Kirim")
async def cmd_income(message: types.Message, state: FSMContext):
    await state.set_state(IncomeStates.amount)
    await message.answer("💰 Kirim summasini kiriting:", reply_markup=types.ReplyKeyboardRemove())

@dp.message(IncomeStates.amount)
async def process_income_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(' ', ''))
        if amount <= 0:
            await message.answer("❌ Iltimos, 0 dan katta son kiriting!")
            return
        await state.update_data(amount=amount)
        await state.set_state(IncomeStates.category)
        await message.answer("Kategoriyani tanlang:", reply_markup=income_categories())
    except ValueError:
        await message.answer("❌ Iltimos, to'g'ri son kiriting!")

@dp.callback_query(lambda c: c.data.startswith('inc_'))
async def process_income_category(callback: types.CallbackQuery, state: FSMContext):
    cats = {'maosh': 'Oylik maosh', 'biznes': 'Biznes daromad', 'sovga': 'Sovgʻa', 'boshqa': 'Boshqa'}
    await state.update_data(category=cats.get(callback.data.replace('inc_', ''), 'Boshqa'))
    await state.set_state(IncomeStates.description)
    await callback.message.edit_text("📝 Izoh yozing (yoki '❌ Bekor qilish' deb yozing):")
    await callback.answer()

@dp.message(IncomeStates.description)
async def process_income_description(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi!", reply_markup=web_app_menu())
        return
    
    data = await state.get_data()
    db.add_transaction(
        message.from_user.id,
        'kirim',
        data['amount'],
        data['category'],
        message.text or ''
    )
    await state.clear()
    await message.answer(
        f"✅ Kirim qo'shildi!\n💰 {data['amount']:,.0f} so'm\n📂 {data['category']}",
        reply_markup=web_app_menu()
    )

# ============================================
# CHIQIM
# ============================================
@dp.message(lambda m: m.text == "💸 Chiqim")
async def cmd_expense(message: types.Message, state: FSMContext):
    await state.set_state(ExpenseStates.amount)
    await message.answer("💸 Chiqim summasini kiriting:", reply_markup=types.ReplyKeyboardRemove())

@dp.message(ExpenseStates.amount)
async def process_expense_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(' ', ''))
        if amount <= 0:
            await message.answer("❌ Iltimos, 0 dan katta son kiriting!")
            return
        await state.update_data(amount=amount)
        await state.set_state(ExpenseStates.category)
        await message.answer("Kategoriyani tanlang:", reply_markup=expense_categories())
    except ValueError:
        await message.answer("❌ Iltimos, to'g'ri son kiriting!")

@dp.callback_query(lambda c: c.data.startswith('exp_'))
async def process_expense_category(callback: types.CallbackQuery, state: FSMContext):
    cats = {
        'ovqat': 'Oziq-ovqat', 'transport': 'Transport', 'uy': 'Uy-joy',
        'telefon': 'Telefon', 'kommunal': 'Kommunal', 'kiyim': 'Kiyim-kechak',
        'salomatlik': 'Salomatlik', 'talim': "Ta'lim", 'oyin': "O'yin-kulgi", 'boshqa': 'Boshqa'
    }
    await state.update_data(category=cats.get(callback.data.replace('exp_', ''), 'Boshqa'))
    await state.set_state(ExpenseStates.description)
    await callback.message.edit_text("📝 Izoh yozing (yoki '❌ Bekor qilish' deb yozing):")
    await callback.answer()

@dp.message(ExpenseStates.description)
async def process_expense_description(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi!", reply_markup=web_app_menu())
        return
    
    data = await state.get_data()
    db.add_transaction(
        message.from_user.id,
        'chiqim',
        data['amount'],
        data['category'],
        message.text or ''
    )
    await state.clear()
    await message.answer(
        f"✅ Chiqim qo'shildi!\n💸 {data['amount']:,.0f} so'm\n📂 {data['category']}",
        reply_markup=web_app_menu()
    )

# ============================================
# STATISTIKA
# ============================================
@dp.message(lambda m: m.text == "📊 Statistika")
async def cmd_stats(message: types.Message):
    await message.answer("📊 Qaysi davr?", reply_markup=stats_menu())

@dp.callback_query(lambda c: c.data == "stats_day")
async def show_day_stats(callback: types.CallbackQuery):
    income, expense = db.get_stats(callback.from_user.id, 1)
    await callback.message.edit_text(
        f"📊 Kunlik statistika\n\n💰 Kirim: {income:,.0f} so'm\n💸 Chiqim: {expense:,.0f} so'm\n📈 Balans: {income-expense:,.0f} so'm",
        reply_markup=stats_menu()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "stats_week")
async def show_week_stats(callback: types.CallbackQuery):
    income, expense = db.get_stats(callback.from_user.id, 7)
    await callback.message.edit_text(
        f"📊 Haftalik statistika\n\n💰 Kirim: {income:,.0f} so'm\n💸 Chiqim: {expense:,.0f} so'm\n📈 Balans: {income-expense:,.0f} so'm",
        reply_markup=stats_menu()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "stats_month")
async def show_month_stats(callback: types.CallbackQuery):
    income, expense = db.get_stats(callback.from_user.id, 30)
    text = f"📊 Oylik statistika\n\n💰 Kirim: {income:,.0f} so'm\n💸 Chiqim: {expense:,.0f} so'm\n📈 Balans: {income-expense:,.0f} so'm\n\n"
    
    categories = db.get_categories(callback.from_user.id)
    text += "🥧 Kategoriyalar:\n"
    for cat, type, amount in categories:
        emoji = "💰" if type == "kirim" else "💸"
        text += f"{emoji} {cat}: {amount:,.0f} so'm\n"
    
    await callback.message.edit_text(text, reply_markup=stats_menu())
    await callback.answer()

# ============================================
# KARTALAR
# ============================================
@dp.message(lambda m: m.text == "💳 Kartalar")
async def cmd_cards(message: types.Message):
    await message.answer("💳 Kartalar:", reply_markup=cards_menu())

@dp.callback_query(lambda c: c.data == "add_card")
async def add_card(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CardStates.name)
    await callback.message.edit_text("💳 Karta nomini kiriting:")
    await callback.answer()

@dp.message(CardStates.name)
async def process_card_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CardStates.number)
    await message.answer("🔢 Karta raqami (16 ta):")

@dp.message(CardStates.number)
async def process_card_number(message: types.Message, state: FSMContext):
    number = message.text.replace(' ', '')
    if len(number) != 16 or not number.isdigit():
        await message.answer("❌ 16 ta raqam kiriting!")
        return
    await state.update_data(number=number)
    await state.set_state(CardStates.balance)
    await message.answer("💰 Balansni kiriting:")

@dp.message(CardStates.balance)
async def process_card_balance(message: types.Message, state: FSMContext):
    try:
        balance = float(message.text.replace(' ', ''))
        if balance < 0:
            await message.answer("❌ Balans manfiy bo'lishi mumkin emas!")
            return
        data = await state.get_data()
        db.add_card(message.from_user.id, data['name'], data['number'], balance)
        await state.clear()
        await message.answer(
            f"✅ Karta qo'shildi!\n💳 {data['name']}\n💰 {balance:,.0f} so'm",
            reply_markup=web_app_menu()
        )
    except ValueError:
        await message.answer("❌ To'g'ri son kiriting!")

@dp.callback_query(lambda c: c.data == "my_cards")
async def my_cards(callback: types.CallbackQuery):
    cards = db.get_cards(callback.from_user.id)
    if not cards:
        await callback.message.edit_text("❌ Karta yo'q", reply_markup=cards_menu())
        await callback.answer()
        return
    
    text = "💳 Mening kartalarim\n\n"
    for card in cards:
        text += f"🏦 {card[0]}\n🔢 {card[1][:4]}****{card[1][-4:]}\n💰 {card[2]:,.0f} so'm\n\n"
    
    await callback.message.edit_text(text, reply_markup=cards_menu())
    await callback.answer()

# ============================================
# BUDJET
# ============================================
@dp.message(lambda m: m.text == "📈 Budjet")
async def cmd_budget(message: types.Message):
    await message.answer(
        "📈 <b>Budjet</b>\n\n"
        "Budjet funksiyasi tez orada!\n\n"
        "Hozirda quyidagilar mavjud:\n"
        "💰 Kirim qo'shish\n"
        "💸 Chiqim qo'shish\n"
        "📊 Statistika\n"
        "💳 Kartalar\n"
        "🚀 Open App",
        parse_mode="HTML",
        reply_markup=web_app_menu()
    )

# ============================================
# SOZLAMALAR
# ============================================
@dp.message(lambda m: m.text == "⚙️ Sozlamalar")
async def cmd_settings(message: types.Message):
    await message.answer(
        "⚙️ <b>Sozlamalar</b>\n\n"
        "🌐 Til: O'zbekcha\n"
        "💰 Valyuta: UZS\n"
        "🔔 Ogohlantirishlar: Yoqilgan\n"
        "🌐 Sayt: kunlik.tizim\n\n"
        "📱 Bot: @kunlik_tizimbot",
        parse_mode="HTML",
        reply_markup=web_app_menu()
    )

# ============================================
# BACK
# ============================================
@dp.callback_query(lambda c: c.data == "back")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text("🔙 Asosiy menyu", reply_markup=web_app_menu())
    await callback.answer()

# ============================================
# RUN BOT
# ============================================
async def main():
    try:
        print("="*50)
        print("💰 MOLIYA TIZIMI PRO")
        print("="*50)
        print("🤖 Bot ishga tushmoqda...")
        print("✅ Barcha funksiyalar tayyor!")
        print(f"🌐 Sayt linki: {SAYT_LINKI}")
        print("="*50)
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Bot ishga tushmadi: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Bot to'xtatildi!")
    except Exception as e:
        print(f"\n❌ Xatolik: {e}")