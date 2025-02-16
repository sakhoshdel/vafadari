from .models import Festival
from datetime import date


def add_variable_to_context(request):
    festival = Festival.objects.last()
    # print(festival)
    # print(date.today() > festival.end_date )
    # print( not festival.lottery_was_done
    if not festival: return { 'show_form': True if not festival else False}
    return {
        'festival_excel_file_name': f'{festival.start_date}until{festival.end_date}',
        'festival_is_active': festival and festival.start_date <=  date.today() <= festival.end_date,
        'festival_is_not_active_and_was_not_done': festival and  festival.end_date < date.today() and not festival.lottery_was_done,
        'festival_is_not_active_and_was_done':festival and  festival.end_date < date.today() and festival.lottery_was_done,
        'calc_festival_chance_digits': True if festival.all_taken_stamps else False,
        'festival': festival,
        # 'request_user': request.user
    }   
    
