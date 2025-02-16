from celery import shared_task
from requests.exceptions import RequestException, ConnectionError
import requests 
from moshtari.models import SMSLog
from typing import Dict

def log_error(user_full_name, phone_number, error_message,response_message, status_code):
    """Utility function to log errors to SMSLog."""
    SMSLog.objects.create(
        receviver_full_name=user_full_name,
        recevier_phone_number=phone_number,
        message=error_message,
        is_successfull=False,
        status_code=status_code,
        response_message=response_message,
    )
    
    
url = 'https://console.melipayamak.com/api/send/simple/a8b3b5300f9042b898815c3d83508d8a'
@shared_task(max_retries=3)
def send_text_message(message_dict:Dict, user_full_name:str):
    message = message_dict.get('text')
    phone_number = message_dict.get('to')
    res = -1
    try:
        # message_dict['to'] = "09904336151"
        res= requests.post(url, json=message_dict)
        res_js = res.json() if res.content else {}
        SMSLog.objects.create(
            receviver_full_name=user_full_name,
            recevier_phone_number=phone_number,
            message=message,
            is_successfull=True if (res.status_code == 200 and res_js.get('status', '') == "ارسال موفق بود") else False,
            status_code =res.status_code,
            response_message=res_js.get('status', '')

        )
        
        
    except ConnectionError as ce:
        error_message = f"Connection error : {ce}"
        # save_error_to_log(url, error_message)
        print('33', error_message)
        log_error(user_full_name,
                  phone_number,
                  error_message,
                  'error',
                  res
                  )

        
    except RequestException as re:

        error_message = f"Other request error: {re}"
        print('22', error_message)

        log_error(user_full_name,
                  phone_number,
                  error_message,
                 'error',
                  res
                  )

    except Exception as e:

            error_message = f"Other request error: {e}"
            print('11', error_message)
            log_error(user_full_name,
                  phone_number,
                  error_message,
                  'error',
                  res
                  )
            
