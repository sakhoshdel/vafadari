from django import template
from jdatetime import datetime as jdatetime
from datetime import datetime
from persian_tools import separator, digits
from decimal import Decimal
from django.core.paginator import Paginator
from jalali_date import  datetime2jalali
from django.utils import timezone
from moshtari.views import DATA_KEY_LIST


register = template.Library()


@register.filter
def split_befor_underscore(value):

    return value.split('_')[0]

persian_day_names = {
    'Monday': 'دوشنبه',
    'Tuesday': 'سه‌شنبه',
    'Wednesday': 'چهارشنبه',
    'Thursday': 'پنج‌شنبه',
    'Friday': 'جمعه',
    'Saturday': 'شنبه',
    'Sunday': 'یک‌شنبه',
}


@register.filter
def to_jalali(value):
    if value is None:
        return ''
    jalali_datetime = jdatetime.fromgregorian(datetime=value)
    formatted_date = jalali_datetime.strftime('  %H:%M  ,%Y٫%m٫%d ')
    persian_digits = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
    formatted_date = formatted_date.translate(persian_digits)
    return formatted_date


@register.filter
def to_jalalistamp(value):
    if value is None:
        return ''
    jalali_datetime = jdatetime.fromgregorian(datetime=datetime.fromisoformat(value))
    formatted_date = jalali_datetime.strftime(' %H:%M  ,%Y٫%m٫%d ')
    persian_digits = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
    formatted_date = formatted_date.translate(persian_digits)
    return formatted_date


@register.filter
def to_jalali_without_hour(value):
    if value is None:
        return ''
    jalali_datetime = jdatetime.fromgregorian(datetime=value)
    formatted_date = jalali_datetime.strftime('%Y٫%m٫%d ')
    persian_digits = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
    formatted_date = formatted_date.translate(persian_digits)
    return formatted_date

@register.filter
def to_jalali_without_hour_stamp(value):
    if value is None:
        return ''
    jalali_datetime = jdatetime.fromgregorian(datetime=datetime.fromisoformat(value))
    formatted_date = jalali_datetime.strftime('%Y٫%m٫%d ')
    persian_digits = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
    formatted_date = formatted_date.translate(persian_digits)
    return formatted_date



@register.filter
def number_to_persian(number):
    if type(number) != Decimal:
        number = number.split('_')[0]
    persion_number = digits.convert_to_fa(number)
    separate = separator.add(persion_number)

    return separate


@register.filter
def digit_to_persion(value):
    return digits.convert_to_fa(value)

@register.filter
def phone_number_to_persian(value):
    number = '0' + str(value)[3:]
    return digits.convert_to_fa(number)

@register.filter
def secret_phone_num(value):
    number = '0' + str(value)[3:]
    number = number[:4] + '***' + number[7:]
    return digits.convert_to_fa(number)

    

@register.filter
def digit_to_word(value):
    return digits.convert_to_word(value)

@register.filter
def split_str_list(value):
    if not value: return 'بیشترین تعداد مهر (بدون قرعه کشی)'
    chance_list =  value.replace('[', '').replace(']', '').split(', ')
    return f'از {chance_list[0]} تا {chance_list[-1]}'



@register.simple_tag
def get_proper_elided_page_range(p, number, on_each_side=1, on_ends=2):
    paginator = Paginator(p.object_list, p.per_page)
    return paginator.get_elided_page_range(number=number, 
                                           on_each_side=on_each_side,
                                           on_ends=on_ends)
    
@register.filter
def invited_customer_users(user):
    card_key_list = DATA_KEY_LIST
    all_invited_users_count = user.referall_users.count()
    if not all_invited_users_count: return 0
    
    users_did_firts_purchase = 0 
    columns_num = 0
    for card in user.cards.all():
        user_card = card.award_tick_table
        for key, va in user_card.items():
            if key.split('_')[0] in card_key_list: continue
            if not columns_num:
                columns_num = sum(1 for column in va if column.startswith('column_'))
            
            users_did_firts_purchase += sum(1 for i in range(columns_num) if 'خرید نفر معرفی شده' in va[f'column_{i + 1}']['reason'] or 'دستی' in va[f'column_{i + 1}']['reason'] )

    return users_did_firts_purchase
 
@register.filter   
def calculate_age(b_date:datetime) -> str:
        if b_date is not None:  
            today = timezone.now().date()  # Get today's date  
            age = today.year - b_date.year  # Calculate age in years  
            # Check if the birthday has occurred this year yet  
            if (today.month, today.day) < (b_date.month, b_date.day):  
                age -= 1  # Subtract 1 if the birthday hasn't occurred yet this year  
            return digits.convert_to_fa(str(age))  
        return ''  # Return '-' if there is no birth date  


@register.filter   
def convert_birth_date_to_jalali(b_date:datetime) -> str:
        if b_date is not None:  

            birth_date = datetime.combine(b_date, datetime.min.time())
            return digits.convert_to_fa(datetime2jalali(birth_date).strftime('%Y٫%m٫%d'))  
        return '-'
    