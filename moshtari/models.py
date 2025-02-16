from django.db import models
from django.utils.translation import gettext_lazy as _ 
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator


class UserGiftData(models.Model):
    award_tick_table = models.JSONField(default=dict, verbose_name=_('جدول مشتری'))
    big_award = models.DecimalField(max_digits=9, decimal_places=0, default=0, verbose_name=_('جایزه بزرگ'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ایجاد جدول'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cards', verbose_name=_('کاربر'))

    class Meta:
        verbose_name = _("کارت مخصوص کاربر")
        verbose_name_plural = _("کارت های مخصوص کاربر")
    def __str__(self) -> str: 
        return f'کارت مخصوص   {self.user.first_name} {self.user.last_name} {self.id}'
    
class UserTableData(models.Model):
    award_tick_table = models.JSONField(default=dict, verbose_name=_('جدول مشتری'))
    big_award = models.DecimalField(max_digits=9, decimal_places=0, default=0, verbose_name=_('جایزه بزرگ'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ایجاد جدول'))

    class Meta:
        verbose_name = _("کارت  تنظیم شده سایت")
        verbose_name_plural = _("کارت های تنظیم شده سایت")


    def __str__(self) -> str:
        return u'جدول تنظیمات {}'.format(self.id)

class stamp_reasons(models.Model):
    reason = models.CharField(max_length=500, verbose_name=_('دلیل مهر'), null=True, blank=True)
    used_count = models.IntegerField(default=0,blank=True, verbose_name=_('تعداد استفاده شده'))
    limit = models.IntegerField(default=0,blank=True,validators=[MinValueValidator(0)], 
                                verbose_name=_('حداکثر تعداد مهر'),
                                help_text=_("اگر صفر باشد میتوانید مهر نامحدود با این دلیل بزنید!!"))
    


    class Meta:
        verbose_name = _("دلیل مهر")
        verbose_name_plural = _("دلیل های مهر زدن")

    def __str__(self) -> str:
        return str(f'{self.reason} {self.id}')

class Festival(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ایجاد جشنواره'))
    
    name = models.CharField(default=_('جشنواره'), max_length=300, verbose_name=_('نام جشنواره'))
    start_date = models.DateField(verbose_name=_('تاریخ شروع'))
    end_date = models.DateField(verbose_name=_('تاریخ پایان'))
    min_stamp = models.IntegerField(verbose_name=_('حداقل تعداد مهر'))
    number_of_winners = models.PositiveBigIntegerField(verbose_name=_('تعداد برندگان جشنواره'))
    
    # each winner prize such as [fist_one^prize,second^prize,third^pize....]
    winners_prizes = models.JSONField(default=dict, verbose_name=_('جایزه بدندگان'))
    
    # assighnment after start_end date and when take first_winner_number
    lottery_was_done = models.BooleanField(default=False, verbose_name=_(' قرعه کشی انجام شده'))
    first_winner_number =models.PositiveBigIntegerField(null=True, blank=True, verbose_name=_('شماره شانس اولین برنده'))
    all_taken_stamps = models.PositiveBigIntegerField(null=True, blank=True,  verbose_name=_('کل مهرهای اخذ شده در جشنواره'))
    step_number = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('عدد گام'))
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('لیست شرکت کنندگان'), through='FestivalMembers', through_fields=('festival', 'user'))
    number_one_stamps = models.IntegerField(default=0, verbose_name=_('مهرهای نفر اول جشنواره'))
    description_link = models.URLField(max_length=300, null=True, blank=True, verbose_name=_('لینک توضیحات'))
    excel_file = models.FileField(null=True, blank=True, upload_to='excel_files/', verbose_name=_("فایل اکسل"))
    winner_link = models.URLField(max_length=500, null=True, blank=True, verbose_name=_("لینک لیست برندگان"))

    


    class Meta:
        verbose_name = _("جشنواره")
        verbose_name_plural = _("جشنواره ها")

    def __str__(self) -> str:
        return str(f'{self.name} {self.id}')

# Model.m2mfield.through.objects.all()

class FestivalMembers(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    festival = models.ForeignKey(Festival, on_delete=models.CASCADE)
    festival_chance_number_list = models.TextField(null=True, blank=True, verbose_name=_('شماره های شانس در جشنواره'))
    win = models.BooleanField(default=False,  verbose_name=_('برنده هست؟'))
    taken_stamps = models.PositiveBigIntegerField(default=0 ,verbose_name=_('تعداد مهر گرفته شده در این جشنواره'))
    rank = models.PositiveBigIntegerField(default=0, verbose_name=_('رتبه در جشنواره'))
    message_status = models.CharField(max_length=3, null=True, blank=True, verbose_name=_('وضعیت ارسال پیامک'))
    message_content = models.CharField(max_length=500, null=True, blank=True,  verbose_name=_('متن پیام'))
    prize = models.CharField(max_length=500, null=True, blank=True,  verbose_name=_('جایزه'))
    
    
    class Meta:
        verbose_name = _(" مادل میانجی جشنواره یوزر")
        verbose_name_plural = _("مادل های میانجی حشنواره یورز")

    def __str__(self) -> str:
        return str(f'{self.festival} {self.user} {self.id}')

class OrderDetailRowVersion(models.Model):
    row_version_person = models.BigIntegerField(default=0, verbose_name=_(" راو ورژن شخصی"), help_text=_("برای گرفتن OrderDetail از این ورژن"))
    row_version_company = models.BigIntegerField(default=0, verbose_name=_("راو ورژن شرکت"), help_text=_("برای گرفتن OrderDetail از این ورژن"))
#through_fields = {}
class SMSLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ارسال پیامک'))
    receviver_full_name = models.CharField(_('نام و نام خانوادگی گیرنده'), max_length=100, )
    recevier_phone_number = PhoneNumberField(region='IR', verbose_name=_('شماره موبایل گیرنده'))
    message = models.CharField(_('متن پیام'),  max_length=1000) 
    is_successfull= models.BooleanField(_('ارسال موفق'), default=False)
    response_message = models.CharField(_("ریسپانس پیامک ارسالی"), max_length=500)
    status_code = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = _("پیامک ارسالی")
        verbose_name_plural = _("پیامک های ارسالی")

    def __str__(self) -> str:
        return self.message[:20]