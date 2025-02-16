from django.core.management.base import BaseCommand
from moshtari.models import UserGiftData
from moshtari.views import DATA_KEY_LIST
from decimal import Decimal
import requests
from time import sleep
import time
from datetime import datetime
import logging
from jdatetime import datetime as jdatetime
from persian_tools import digits, separator
from moshtari.tasks import send_text_message
def to_jalalistamp(value):
    if value is None:
        return ''
    jalali_datetime = jdatetime.fromgregorian(datetime=datetime.fromisoformat(value))
    formatted_date = jalali_datetime.strftime(' %H:%M  ,%Y٫%m٫%d ')
    persian_digits = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
    formatted_date = formatted_date.translate(persian_digits)
    return formatted_date

timestamp = time.strftime('%Y%m%d-%H%M%S')
# log_file = f'/home/bm7/projects/vafadari/sending_11_message_logs/sended_messages_{timestamp}.log'
log_file = f'/home/vafa/stamp_system/sending_11_message_logs/sended_messages_{timestamp}.log'
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_file_handler = logging.FileHandler(log_file, mode='a')
log_file_handler.setFormatter(logging.Formatter(log_format))
logger = logging.getLogger('Send message logs')
logger.setLevel(logging.INFO)

logger.addHandler(log_file_handler)

def table_row_is_full_and_used_or_not(table_data):
    msg_is_sent = True
    unused_prize = 0
    columns_num = 0
    data = table_data
    for key , va in data.items():
        prize = key.split('_')[0]
        if prize not in DATA_KEY_LIST:
            
            if not columns_num:
                columns_num = sum(1 for column in va if column.startswith('column_'))
            # print('columns_number', columns_num)
            all_column_stamped_or_not = all([va[f'column_{i + 1}']['stamp'] for i in range(columns_num)])

            if all_column_stamped_or_not and not va['is_used']:
                if  not va['send_message_self_to_is_used']:
                    va['send_message_self_to_is_used'] = True 
                    msg_is_sent = False
                unused_prize += Decimal(prize)
                    
    
    return msg_is_sent,  data, unused_prize



class Command(BaseCommand):
    help = "Send message once in 11 pm if users didn't use them prize every day"
    
    def handle(self, *args, **options) :
        user_cards = UserGiftData.objects.select_related('user').all()
        for card in user_cards:
            card_data = card.award_tick_table
            try:
                msg_is_sent, changed_card_data, unused_award = table_row_is_full_and_used_or_not(card_data)
                if not msg_is_sent and unused_award:
                    first_name = card.user.first_name
                    last_name = card.user.last_name
                    phone_number = card.user.phone_number
                    unuserd_prize = separator.add(digits.convert_to_fa(unused_award))
                    full_name =f"{first_name} {last_name}"
                    msg =f"""
 {full_name} عزیز؛

🎁شما {unuserd_prize} تومان تخفیف دارید.🎁
میتوانید از آن در خرید بعدی خود استفاده نمایید.

مشاهده کارت وفاداری:
https://cc.bartardigital.com/

برتر دیجیتال
"""

                    data_msg = {'from': '500010609865', 'to':str(phone_number) , 'text': msg}
                    send_text_message.delay(data_msg, full_name)
                    # rs = requests.post('https://console.melipayamak.com/api/send/simple/a8b3b5300f9042b898815c3d83508d8a', json=data_msg)
                    # rs= {'status_code': '200'}
                    # response = rs.json()
                    # if rs.status_code == 200 and response.get('status') == "ارسال موفق بود":
                    card.award_tick_table = changed_card_data
                    card.save()
                    logger.info(f'message sent \n name:{full_name}\n award:{unuserd_prize} \n phone_number: {phone_number} \n time:{to_jalalistamp(datetime.now().isoformat())}\n\n')
                    print(msg)
                    
                        
                    # else :
                        # logger.info(f'{rs.status_code} \n {response.get("status")}\n\n')
            except Exception as e:
                logger.info(e)
