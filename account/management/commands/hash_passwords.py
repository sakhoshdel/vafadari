from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password

class Command(BaseCommand):
    help = 'Hash plaintext passwords for users'

    def handle(self, *args, **kwargs):
        # Find users with non-hashed passwords
        users = User.objects.all()

        for user in users:
            if not user.password.startswith('pbkdf2_sha256$'):  # Check if password is not hashed
                plain_password = user.password
                self.stdout.write(f'Hashing password for user {user.username}')
                
                # Hash the password
                user.set_password(plain_password)
                user.save()
        
        self.stdout.write(self.style.SUCCESS('All plaintext passwords hashed successfully!'))
