from kavenegar import KavenegarAPI, APIException, HTTPException
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("API_KEY", "")

def send_Otp_Code(phone_number, code):
    try:
        api = KavenegarAPI(API_KEY)
        params = { 'sender' : '2000660110', 
                'receptor': phone_number,
                'message' : f'You\'re Confirmation Code: {code}' 
                }
        
        response = api.sms_send(params)
        print(response)
        
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)
