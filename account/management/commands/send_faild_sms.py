from django.core.management.base import BaseCommand
from account.models import User
from moshtari.tasks import send_text_message

class Command(BaseCommand):
    help = 'Hash plaintext passwords for users'

    def handle(self, *args, **kwargs):
        # Find users with non-hashed passwords
        users = User.objects.all().order_by('-date_joined')[:11]

        for user in users:
            full_name = f"{user.first_name} {user.last_name}"
            message_text = f"""
                                     {full_name} عزیز؛
😍🤩
                        
کارت وفاداری برتر دیجیتال برای شما صادر شد.
برای اطلاع از نحوه دریافت تخفیف در خریدهای بعدی خود، حتما ویدئوی زیر را ببینید:
                                            https://bartardigital.com/loyalty-card-guide/
                                            
با تشکر."""
            send_text_message.delay({'from': '500010609865', 'to': str(user.phone_number) , 'text': message_text}, full_name)
        
        self.stdout.write(self.style.SUCCESS('All plaintext passwords hashed successfully!'))
