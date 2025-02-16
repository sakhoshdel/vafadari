from django import forms
from phonenumber_field.formfields import PhoneNumberField
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _ 
from unidecode import unidecode
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget
from django.utils import timezone



def valid_id(id):
    control_num = id[-1]
    body = id[:-1]
    body_sum_with_position = sum(int(body[abs(i - 10)]) * i  for i in range(10, 1, -1))
    remind = body_sum_with_position % 11

    if remind < 2:
        return remind == int(control_num)
    return (11 - remind) == int(control_num)


class UserRegistrationForm(UserCreationForm):

    birth_date = JalaliDateField(widget=AdminJalaliDateWidget, required=False)
    birth_date.widget.attrs.update({'class': 'input100  jalali_date-date  mt-1','id':'birth_date', 'autocomplete':"off",
                                    "requierd": False})

    phone_number = PhoneNumberField(
        region='IR',
        widget=forms.TextInput(attrs={'class': 'input100', 'maxlength':"11"}),    
        error_messages = {
                'required': _('لطفا شماره تلفن را وارد کنید'),
                'unique':_( 'این شماره تلفن قبلا ثبت نام کرده'),
                'invalid': _('طول شماره تلفن باید ۱۱ باشد'),
                
            }
    )
    send_otp = forms.BooleanField(required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-check-input',
                                                                'type':"checkbox",
                                                                'value':"True",
                                                                'checked':'',
                                                                'id':"flexCheckDefault" ,
                                                                'required': False}))
    
    # def __init__(self, *args, **kwargs):
    #     kwargs.setdefault('label_suffix', '')
    #     super(UserRegistrationForm, self).__init__(*args, **kwargs)

    #     # changing error messages:
    #     for field in self.fields.values():
    #         field.error_messages = {'required':'The field {fieldname} is required'.format(fieldname=field.label)}

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'id_card_num', 'phone_number', 'email', 'username', 'birth_date']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input100 input100-right','required': True }),
            'last_name': forms.TextInput(attrs={'class': 'input100 input100-right',  'required': True},),
            'id_card_num': forms.TextInput(attrs={'class': 'input100'}),
            'email': forms.EmailInput(attrs={'class': 'input100'}),
        }

        error_messages = {
            'last_name': {
                'required': _("لطفا نام خانوادگی را وارد کنید"),
            },


            'id_card_num': {
                'required' : _(''),
                'unique':_( 'این کد ملی قبلا ثبت نام کرده')
            },
            'email': {
                'required' : _(''),
                'unique':_( 'این ایمیل  قبلا ثبت نام کرده'),
                'invalid': _('فرم ایمیلتان را تصحیح کنید')
            },}

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')  

        if birth_date:  
            # Calculate the minimum valid date (1 years ago)
            # min_date = timezone.now().date() - timedelta(days=1*365)  # Approximation
            if birth_date > timezone.now().date():  
                raise forms.ValidationError("تاریخ تولد تا امروز میتواند باشد.")  

        return birth_date  

    def clean_id_card_num(self):
        id_card_number = self.cleaned_data['id_card_num']
        id_card_number = unidecode(u"{}".format(id_card_number))
        if not id_card_number.isdigit():       
            raise ValidationError(_('لطفا عدد وارد کنید')) 
        elif len(id_card_number) != 10:

            raise ValidationError(_('طول کد ملی باید ۱۰ رقم باشد')) 

        if not valid_id(id_card_number):
            raise ValidationError('لطفا کدملی معتبر خودتان را وارد کنید')
        return id_card_number


class LoginForm(forms.Form):
    username = forms.CharField(max_length=65,
                               widget=forms.TextInput(attrs={'class': 'input100',
                                                            'required': True,
                                                            'placeholder':'۰۹xxxxxxxxx'}))
    password = forms.CharField(max_length=65,
                               widget=forms.TextInput(attrs={'class': 'input100',
                                                            'type': 'password',
                                                            'name': 'pass',
                                                            'placeholder':'پیش فرض: کد ملی'}))


class ChangePasswordForm(forms.Form):
    old_pass = forms.CharField(widget=forms.TextInput(attrs={'type':'password', 'class': 'form-control class_pass','required': True }))
    new_pass =  forms.CharField(widget=forms.TextInput(attrs={'type':'password', 'class': 'form-control class_pass ','required': True }))
    repeat_pass = forms.CharField(widget=forms.TextInput(attrs={'type':'password', 'class': 'form-control class_pass','required': True }))
    
    
    
    def clean(self):

        new_pass = self.cleaned_data.get('new_pass')
        repeat_pass = self.cleaned_data.get('repeat_pass')
        print(repeat_pass)
        print(new_pass)
        if not new_pass == repeat_pass:
            raise ValidationError(_('تکرار رمز درست نیست'))


class ChangePhoneForm(forms.Form):
    
    new_phone = PhoneNumberField(
        region='IR',
        widget=forms.TextInput(attrs={'class': 'form-control',' ':"11"}),    
        error_messages = {
                'required': _('لطفا شماره تلفن را وارد کنید'),
                'unique':_( 'این شماره تلفن قبلا ثبت نام کرده'),
                'invalid': _('شماره معتبر نمی باشد'),})
   
    password =  forms.CharField(widget=forms.TextInput(attrs={'type':'password', 'class': 'form-control class_pass ' }))

                
    # def clean(self):
    #     print(self.cleaned_data.get('password'))
    #     print(self.cleaned_data.get('new_phone'))
