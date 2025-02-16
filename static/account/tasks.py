from celery import shared_task
from account.models import User
import requests
from django.utils import timezone
from typing import Dict, Optional, Callable, Tuple
import copy
from datetime import datetime
from jalali_date import date2jalali
from django.conf import settings
from moshtari.models import UserTableData, UserGiftData, SMSLog
import traceback
from django.db import transaction
import json
from requests.exceptions import RequestException, ConnectionError



DATA_KEY_LIST = settings.DATA_KEY_LIST

def table_is_full_or_not(table_data) -> bool:
    """
    If result be True mean that card is full.
    """
    columns_num = 0
    counter = 0
    row_number = 0
    for key , va in table_data.items():
        if key.split('_')[0] not in DATA_KEY_LIST:
            row_number += 1
            
            if not columns_num:
                columns_num = sum(1 for column in va if column.startswith('column_'))
            # print('columns_number', columns_num)
            all_column_stamped_or_not = all([va[f'column_{i + 1}']['stamp'] for i in range(columns_num)])
            if all_column_stamped_or_not:
                counter += 1 
    # print(row_number)
    if counter == row_number:
        return True
        
    return False


def make_stamp(card: Dict, stamp_reason:str, admin_name:str) -> Tuple[Dict, bool]:
    updated_card = copy.deepcopy(card)
    breaker = False
    for key, value in updated_card.items():      
        if type(value) == dict:

            for key_in, value_in in reversed(value.items()):
                if 'column' in key_in:
                    
                    if not value_in['stamp']:
                        value_in['stamp'] = True
                        value_in['reason'] = stamp_reason
                        value_in['admin'] = f'{admin_name} (سیستمی)'
                        value_in['date'] = datetime.now().isoformat()
                        
                        if table_is_full_or_not(updated_card):
                            updated_card['is_table_full'] = True
                        
                        breaker = True
                        break 
            
        if breaker: 
            break
    
    return updated_card, breaker


def create_new_card_for_user(user) -> Optional[UserGiftData]:
    """
    If rais error when creating new card return None 
        else return UserGiftData ojbect

    """
    try:
        last_created_card = UserTableData.objects.last()
        
        new_card = UserGiftData.objects.create(user=user, 
                    award_tick_table=last_created_card.award_tick_table,
                    big_award=last_created_card.big_award)
    
        return new_card
    except Exception as e:
        print(e)
        return None

def save_make_stamp(card:UserGiftData,
                    reason:str,
                    make_stamp:Callable[[Dict, str, str], Tuple[Dict, bool]],
                    new_card:bool,
                    admin_user:str,
                    ):
    
        # db_stamped_user_entry = next((entry for entry in db_stamped_user if national_code == entry.get('national_code', None)), None)
        updated_card, is_table_full = make_stamp(card.award_tick_table, reason, admin_user)
        card.award_tick_table = updated_card
        card.save()
        # if not db_stamped_user_entry:
        #     db_stamped_user.append({**person_info,'new_register':new_register, 'new_card':new_card})
        
        return updated_card, is_table_full
          
          
           
def stamp_card_automatic(user:User, stamp_count:int, admin_name:str='') -> bool:
    """
    This function stamp user card and if user card is 
    full it genarate new card and stamp it
    
    return : True if stamping is successfuly else False
    """
    try:
        with transaction.atomic():
            make_new_card = False
            for _ in range(stamp_count):
                user_last_card = user.cards.last()
                last_card_data = user_last_card.award_tick_table
                if last_card_data.get('is_table_full', ''):
                    make_new_card = True
                    new_card = create_new_card_for_user(user)
                    save_make_stamp(
                        card=new_card,
                        reason='هدیه تولد',
                        make_stamp=make_stamp,
                        new_card=make_new_card,
                        admin_user=admin_name,
                        )
        
                else:
                    # If user card not full
                    save_make_stamp(
                        card=user_last_card,
                        reason='هدیه تولد',
                        make_stamp=make_stamp,
                        new_card=make_new_card,
                        admin_user=admin_name,
            
                    )
            return True
    except Exception as e:
        m = f"Error processing person_info: {user.first_name}, error: {traceback.format_exc()}"
        print(m)
        return False

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
def send_text_message(message_dict:Dict, user_full_name:str, extra_message:str):
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
            message=message + extra_message,
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
                  error_message + extra_message,
                  'error',
                  res
                  )

        
    except RequestException as re:

        error_message = f"Other request error: {re}"
        print('22', error_message)

        log_error(user_full_name,
                  phone_number,
                  error_message + extra_message,
                 'error',
                  res
                  )

    except Exception as e:

            error_message = f"Other request error: {e}"
            print('11', error_message)
            log_error(user_full_name,
                  phone_number,
                  error_message + extra_message,
                  'error',
                  res
                  )
            

@shared_task
def send_birthday_msg_and_stamp_card(stamp_count:int):
    all_users = User.objects.filter(birth_date__isnull=False)\
        .prefetch_related('cards')

    
    for user in all_users:
        message_text = f"""
{user.first_name} عزیز;

🎂از طرف برتر دیجیتال زادروزتان را تبریک میگوییم.
🎁سه مهر در کارت وفاداری شما بعنوان هدیه تولد ثبت گردید.

مشاهده:
https://cc.bartardigital.com/

برتر دیجیتال - رضایت پس از خرید
"""
        message_data = {'from': '500010609865', 'to': str(user.phone_number) , 'text': message_text}

        birth_date = date2jalali(user.birth_date)
        now = date2jalali(timezone.now().date())
        if ((birth_date.month, birth_date.day)
            == (now.month, now.day)) and user.birth_date_status:
            
            # Stamp birthday
            success_stamp = stamp_card_automatic(user, stamp_count)

            extra_message = """""" if success_stamp else """⛔مهر های هدیه تولد کاربد زده نشدند⛔"""

            # Send Birthday message
            send_text_message.delay(message_data, f"{user.first_name} {user.last_name}", extra_message=extra_message)
     