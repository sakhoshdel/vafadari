from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

DATA_KEY_LIST = settings.DATA_KEY_LIST

def user_invites_and_user_customers(user, card_key_list):
    all_invited_users_count = user.referall_users.count()
    # if not all_invited_users_count: return 0, 0
    
    users_did_firts_purchase = 0 
    columns_num = 0
    for card in user.cards.all():
        user_card = card.award_tick_table
        for key, va in user_card.items():
            if key.split('_')[0] in card_key_list: continue
            if not columns_num:
                columns_num = sum(1 for column in va if column.startswith('column_'))
            
            users_did_firts_purchase += sum(1 for i in range(columns_num) if 'خرید نفر معرفی شده' in va[f'column_{i + 1}']['reason'] or 'دستی' in va[f'column_{i + 1}']['reason'] )

    # users_did_not_first_purchase =  all_invited_users_count - users_did_firts_purchase
    return users_did_firts_purchase , all_invited_users_count
    
    

    
    
    
class Command(BaseCommand):
    help = "This command just use once for set customers field in User model"

    def handle(self, *args, **options):
        # user = get_user_model().objects.get(first_name='عزیز')
        # print(user.cards.all().first().award_tick_table)
        # print(invited_customer_users(user))
        try:
            users = get_user_model().objects.prefetch_related('referall_users', 'cards')
            for user in users:
                print(user.first_name)
                # print(user.cards.all())
                user.customers , _ =  user_invites_and_user_customers(user, DATA_KEY_LIST)
                print(user_invites_and_user_customers(user, DATA_KEY_LIST))
                user.save()
                
        except Exception as error:
            print(error)
