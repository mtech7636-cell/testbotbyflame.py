Import os
import asyncio
import logging
import requests
from threading import Thread
from flask import Flask

from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
)

# ═══════════════════════════════════════════
#  🚀 FLASK KEEP-ALIVE SERVER (Render Support)
# ═══════════════════════════════════════════

app = Flask('')

@app.route('/')
def home():
    return "CPM 2 Bot is Alive & Running!"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# ═══════════════════════════════════════════
#  ⚙️  CONFIG
# ═══════════════════════════════════════════

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8913967230:AAEORwsmBmDPkjlH5FmECPZQR7DFk3ZSY_U")
ADMIN_ID  = int(os.environ.get("ADMIN_ID", 7212602902))

API_KEY  = 'AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ'
BASE_URL = 'https://europe-west1-cpm-2-7cea1.cloudfunctions.net/'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())
router = Router()

# ═══════════════════════════════════════════
#  🎮 CPM 2 API LOGIC (Fully Synced Version)
# ═══════════════════════════════════════════

class CPM2API:
    @staticmethod
    def login(email, password):
        url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}'
        payload = {"email": email, "password": password, "returnSecureToken": True}
        try:
            r = requests.post(url, json=payload, timeout=15)
            if r.status_code == 200:
                data = r.json()
                return {
                    "ok": True,
                    "token": data['idToken'],
                    "local_id": data['localId']
                }
            return {"ok": False, "msg": r.text}
        except Exception as e:
            return {"ok": False, "msg": str(e)}

    @staticmethod
    def inject_coins(token, local_id, amount):
        url = BASE_URL + "BuyCoins21_1"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "data": {
                "accountLocalId": local_id,
                "amount": int(amount),
                "version": "1.1.5",
                "platform": "android"
            }
        }
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=15)
            if r.status_code == 200 and "result" in r.text:
                return f"✅ **{amount} Coins Injected!**"
            return f"❌ Response: `{r.text}`"
        except Exception as e:
            return str(e)

    @staticmethod
    def inject_car(token, local_id, car_id):
        url = BASE_URL + "SaveCar23_1"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "data": {
                "accountLocalId": local_id,
                "carId": int(car_id),
                "action": "add",
                "isPremium": True,
                "version": "1.1.5",
                "platform": "android"
            }
        }
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=15)
            if r.status_code == 200 and "result" in r.text:
                return f"✅ **Car ID {car_id} Successfully Unlocked!**"
            return f"❌ Response: `{r.text}`"
        except Exception as e:
            return str(e)

    @staticmethod
    def inject_money(token, local_id, amount):
        url = BASE_URL + "SaveWalletData23_1"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "data": {
                "accountLocalId": local_id,
                "money": int(amount),
                "version": "1.1.5",
                "platform": "android"
            }
        }
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=15)
            if r.status_code == 200 and "result" in r.text:
                return f"✅ **Money set to ${amount}!**"
            return f"❌ Response: `{r.text}`"
        except Exception as e:
            return str(e)

# ═══════════════════════════════════════════
#  📋 FSM STATES
# ═══════════════════════════════════════════

class CPMState(StatesGroup):
    waiting_email    = State()
    waiting_password = State()
    waiting_coins    = State()
    waiting_car_id   = State()
    waiting_money    = State()

# ═══════════════════════════════════════════
#  ⌨️ KEYBOARDS
# ═══════════════════════════════════════════

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🪙 Inject Coins",       callback_data="act_coins")],
        [InlineKeyboardButton(text="🚗 Inject Car by ID",   callback_data="act_car")],
        [InlineKeyboardButton(text="💵 Set Money (50M Max)", callback_data="act_money")],
        [InlineKeyboardButton(text="🚪 Sign Out",           callback_data="act_logout")]
    ])

def cancel_btn():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✗ Cancel", callback_data="act_cancel")]
    ])

# ═══════════════════════════════════════════
#  🤖 HANDLERS
# ═══════════════════════════════════════════

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    if user_id != ADMIN_ID:
        await message.answer("⚠️ **Access Denied!** നിങ്ങൾക്ക് ഈ ബോട്ട് ഉപയോഗിക്കാൻ അനുവാദമില്ല.")
        return

    data = await state.get_data()
    if data.get("token"):
        await message.answer("🔥 **CPM 2 TOOL BOT** 🔥\n\nമെനുവിൽ നിന്ന് ആവശ്യമുള്ള സേവനം തിരഞ്ഞെടുക്കുക:", reply_markup=main_menu(), parse_mode=ParseMode.MARKDOWN)
    else:
        await message.answer("🔥 **CPM 2 TOOL BOT** 🔥\n\nനിങ്ങളുടെ CPM 2 **Email** അയക്കുക:")
        await state.set_state(CPMState.waiting_email)

@router.message(CPMState.waiting_email)
async def process_email(message: Message, state: FSMContext):
    email = message.text.strip()
    await state.update_data(email=email)
    await message.answer("🔑 ഇനി നിങ്ങളുടെ **Password** അയക്കുക:\n*(സുരക്ഷക്കായി മെസ്സേജ് ഓട്ടോ ഡിലീറ്റ് ആകും)*")
    await state.set_state(CPMState.waiting_password)

@router.message(CPMState.waiting_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text.strip()
    try: await message.delete()
    except: pass

    user_data = await state.get_data()
    email = user_data.get("email")

    msg = await message.answer("⏳ Logging in to CPM 2...")
    res = CPM2API.login(email, password)

    if res["ok"]:
        await state.update_data(token=res["token"], local_id=res["local_id"])
        await msg.edit_text(
            f"✅ **Login Success!**\n\n🆔 **Local ID:** `{res['local_id']}`\n📧 **Email:** `{email}`",
            reply_markup=main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await state.clear()
        await msg.edit_text(f"❌ **Login Failed!**\n\n`{res['msg']}`\n\nവീണ്ടും ലോഗിൻ ചെയ്യാൻ /start അയക്കുക.", parse_mode=ParseMode.MARKDOWN)

# --- ACTIONS ---

@router.callback_query(F.data == "act_coins")
async def ask_coins(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CPMState.waiting_coins)
    await callback.message.edit_text("🪙 ആഡ് ചെയ്യേണ്ട **Coins Amount** ടൈപ്പ് ചെയ്ത് അയക്കുക:", reply_markup=cancel_btn())
    await callback.answer()

@router.message(CPMState.waiting_coins)
async def do_coins(message: Message, state: FSMContext):
    data = await state.get_data()
    token = data.get("token")
    local_id = data.get("local_id")
    
    if not token or not local_id:
        await message.answer("⚠️ Session expired. /start ഉപയോഗിക്കുക.")
        return

    amt = message.text.strip()
    msg = await message.answer("⏳ Injecting coins...")
    resp = CPM2API.inject_coins(token, local_id, amt)
    await msg.edit_text(f"{resp}", reply_markup=main_menu(), parse_mode=ParseMode.MARKDOWN)

@router.callback_query(F.data == "act_car")
async def ask_car(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CPMState.waiting_car_id)
    await callback.message.edit_text("🚗 ആഡ് ചെയ്യേണ്ട **Car ID** അയക്കുക:", reply_markup=cancel_btn())
    await callback.answer()

@router.message(CPMState.waiting_car_id)
async def do_car(message: Message, state: FSMContext):
    data = await state.get_data()
    token = data.get("token")
    local_id = data.get("local_id")

    cid = message.text.strip()
    msg = await message.answer("⏳ Injecting car...")
    resp = CPM2API.inject_car(token, local_id, cid)
    await msg.edit_text(f"{resp}", reply_markup=main_menu(), parse_mode=ParseMode.MARKDOWN)

@router.callback_query(F.data == "act_money")
async def ask_money(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CPMState.waiting_money)
    await callback.message.edit_text("💵 ആഡ് ചെയ്യേണ്ട **Money Amount** അയക്കുക (Max 50M):", reply_markup=cancel_btn())
    await callback.answer()

@router.message(CPMState.waiting_money)
async def do_money(message: Message, state: FSMContext):
    data = await state.get_data()
    token = data.get("token")
    local_id = data.get("local_id")

    mny = message.text.strip()
    msg = await message.answer("⏳ Setting money...")
    resp = CPM2API.inject_money(token, local_id, mny)
    await msg.edit_text(f"{resp}", reply_markup=main_menu(), parse_mode=ParseMode.MARKDOWN)

@router.callback_query(F.data == "act_cancel")
async def cancel_act(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🔥 **CPM 2 TOOL BOT** 🔥\n\nമെനുവിൽ നിന്ന് ആവശ്യമുള്ള സേവനം തിരഞ്ഞെടുക്കുക:", reply_markup=main_menu())
    await callback.answer()

@router.callback_query(F.data == "act_logout")
async def logout_act(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("🚪 Logged out. വീണ്ടും ലോഗിൻ ചെയ്യാൻ /start ഉപയോഗിക്കുക.")
    await callback.answer()

# ═══════════════════════════════════════════
#  🚀 MAIN
# ═══════════════════════════════════════════

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
