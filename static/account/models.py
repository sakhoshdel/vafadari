import base64
import uuid
from datetime import timedelta
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField
from moshtari.models import UserGiftData

DATA_KEY_LIST = ["send", "use", "is"]


class DateFields(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاریخ ثبت نام"), unique=True
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("آخرین تغییر"))

    class Meta:
        abstract = True


class VerificationCodeManager(models.Manager):
    def create_code(self, phone_number, code, expiration_minutes):
        expiration_time = timezone.now() + timedelta(minutes=expiration_minutes)
        return self.create(
            phone_number=phone_number, code=code, expiration_time=expiration_time
        )


class VerificationCode(models.Model):
    phone_number = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_time = models.DateTimeField()

    objects = VerificationCodeManager()

    def is_expired(self):
        return self.expiration_time < timezone.now()

    def __str__(self) -> str:
        return f"{self.phone_number}_{self.code}"


class User(AbstractUser):
    id_card_num = models.CharField(
        max_length=10,
        verbose_name=_("کد ملی"),
        error_messages={"required": "لطفا کد ملی را وارد کنید"},
        unique=True,
    )

    phone_number = PhoneNumberField(
        unique=True, region="IR", verbose_name=_("شماره موبایل")
    )
    email = models.EmailField(null=True, blank=True, verbose_name=_("ایمیل"))
    referral_code = models.CharField(
        max_length=25, verbose_name=_("کد دعوت"), unique=True
    )
    is_verified = models.BooleanField(
        default=False, blank=False, verbose_name=_("تایید شماره تلفن")
    )
    parent_user = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="referall_users",
        null=True,
        blank=True,
        verbose_name=_("دعوت کننده"),
    )
    customers = models.PositiveIntegerField(default=0, verbose_name=("تعداد مشتریان"))

    birth_date = models.DateField(null=True, blank=True, verbose_name=_("تاریخ تولد"))
    birth_date_status = models.BooleanField(
        default=False, verbose_name=_("تایید تاریخ تولد ")
    )

    REQUIRED_FIELDS = [
        "phone_number",
        "first_name",
        "last_name",
        "id_card_num",
        "email",
    ]

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     print('hello')

    def save(self, *args, **kwargs):
        if not self.referral_code:
            while True:
                new_referall_code = (
                    base64.urlsafe_b64encode(uuid.uuid4().bytes)
                    .decode("utf-8")
                    .rstrip()[:25]
                )
                if not User.objects.filter(referral_code=new_referall_code).exists():
                    self.referral_code = new_referall_code
                    break

        super(User, self).save(*args, **kwargs)
        # self.customers = self.update_customers()
        # self.save(update_fields=['customers'])

    # def update_customers(self):
    #     card_key_list = DATA_KEY_LIST

    #     try:
    #         all_invited_users_count = self.referall_users.count()
    #         if not all_invited_users_count: return 0

    #         users_did_firts_purchase = 0
    #         columns_num = 0
    #         for card in self.cards.all():
    #             print(card)
    #             user_card = card.award_tick_table
    #             for key, va in user_card.items():
    #                 if key.split('_')[0] in card_key_list: continue
    #                 if not columns_num:
    #                     columns_num = sum(1 for column in va if column.startswith('column_'))

    #                 users_did_firts_purchase += sum(1 for i in range(columns_num) if 'خرید نفر معرفی شده' in va[f'column_{i + 1}']['reason'] or 'دستی' in va[f'column_{i + 1}']['reason'] )

    #         return users_did_firts_purchase
    #     except Exception as error:
    #         print(error)

    def __str__(self):
        return self.first_name + " " + self.last_name
