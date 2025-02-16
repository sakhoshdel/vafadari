from django import forms
from django.contrib import admin
from .models import User
from jalali_date import  datetime2jalali
from jalali_date.admin import ModelAdminJalaliMixin
from datetime import datetime, timedelta
from django.utils import timezone  
# from persian_tools import separator, digits
# from jalali_date.fields import JalaliDateField

class UserAdminForm(forms.ModelForm):  
    class Meta:  
        model = User  
        fields = '__all__'  # or list the specific fields you want  

    # birth_date = forms.DateField(  
    #     widget=forms.DateInput(attrs={  
    #         'type': 'date',  
    #         'autocomplete': 'off',  # Disable autocomplete  
    #     })  
    # )  

    def clean_birth_date(self):  
        birth_date = self.cleaned_data.get('birth_date')  
        
        if birth_date:  
            # Calculate the minimum valid date (1 years ago)  
            # min_date = timezone.now().date() - timedelta(days=1*365)  # Approximation  
            if birth_date > timezone.now().date():  
                raise forms.ValidationError("تاریخ تولد شما تا امروز میتواند باشد.")  
        
        return birth_date  




@admin.register(User) 
class UserAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    form = UserAdminForm
    list_display = ["get_full_name",  'get_birth_date_jalali','get_age',  'id_card_num', 'get_phone_number', 'is_verified']  
    readonly_fields = ['password']  

    @admin.display(description='تاریخ تولد (جلالی)')  
    def get_birth_date_jalali(self, obj):  
        if obj.birth_date is not None:  
        
            birth_date = datetime.combine(obj.birth_date, datetime.min.time())
            return datetime2jalali(birth_date).strftime('%Y/%m/%d')  
 # Format as needed  
        return '-'
    
    
    @admin.display(description='سن')  
    def get_age(self, obj):  
        if obj.birth_date is not None:  
            today = timezone.now().date()  # Get today's date  
            age = today.year - obj.birth_date.year  # Calculate age in years  
            # Check if the birthday has occurred this year yet  
            if (today.month, today.day) < (obj.birth_date.month, obj.birth_date.day):  
                age -= 1  # Subtract 1 if the birthday hasn't occurred yet this year  
            return age  
        return '-'  # Return '-' if there is no birth date  
    
    @admin.display(description="موبایل")
    def get_phone_number(self, obj):
        return (str(obj.phone_number).replace("+98", "0"))
    
    @admin.display(description="نام و نام خانوادگی")
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"