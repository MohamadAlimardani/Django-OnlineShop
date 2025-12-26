from kavenegar import KavenegarAPI, APIException, HTTPException

def send_Otp_Code(phone_number, code):
    try:
        api = KavenegarAPI('68754B77473772516E6A783132492B737153586D2F5764395753557A4E67703077447055347267753477493D')
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
