import json
from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget
from .models import Festival
from django.utils import timezone
from django.contrib.auth import get_user_model
DATA_KEY_LIST = ["send", "use", "is"]


# def each_user_stamps_and_all_stamps_in_active_festival(festival_model, user_model, card_key_list):
#     try:
#         festival = festival_model.objects.all().last()
#         if not festival: return False
#         s_date = festival.start_date
#         e_date = festival.end_date

#         users = user_model.objects.prefetch_related('cards').all()
#         users_cards = tuple(map(lambda user: (user, user.cards.all()), users))

#         all_stamps_in_festival = 0
#         users_festival_stamps_count = []
#         for user, cards in users_cards:
#             stamp_count_in_festival = 0
#             columns_num = 0
#             for card in cards:
#                 user_card = card.award_tick_table
#                 for key, va in user_card.items():
#                     if key.split('_')[0] in card_key_list: continue
#                     if not columns_num:
#                         columns_num = sum(1 for column in va if column.startswith('column_'))

#                     stamp_count_in_festival += sum(1 for i in range(columns_num) if va[f'column_{i + 1}']['stamp'] and (s_date <= datetime.fromisoformat(va[f'column_{i + 1}']['date']).date() <= e_date))
#             all_stamps_in_festival += stamp_count_in_festival
#             users_festival_stamps_count.append((user, stamp_count_in_festival))
#     except Exception as e:
#         print(e)
#         users_festival_stamps_count = tuple(filter(lambda elem: elem ,map(lambda x: x if x[1] >= festival.min_stamp else None  , users_festival_stamps_count)))
#     return sorted(users_festival_stamps_count, key=lambda elem: elem[1], reverse=True), all_stamps_in_festival


class StampReasonForm(forms.Form):
    def __init__(self, reasons, *args, **kwargs):
        super(StampReasonForm, self).__init__(*args, **kwargs)
        reasons = reasons
        self.fields["selected_option"] = forms.ChoiceField(
            label=_("دلیل مهر زدن خود را انتخاب کنید"),
            choices=[(reason.id, reason.reason) for reason in reasons],
            widget=forms.Select(
                attrs={"class": "form-select mb-3", "menuPlacement": "bottom"}
            ),
            required=False,
        )


class SettingTableForm(forms.Form):
    row_number = forms.IntegerField(
        min_value=0,
        max_value=10,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "input100 input100-right", "required": True}
        ),
        error_messages={
            "invalid": _("لطفا عدد وارد کنید"),
            "min_value": _("عدد نمیتواند منفی باشد"),
            "max_value": _("عدد نمیتواند بیشتر از ۱۰ باشد"),
        },
    )

    column_number_per_row = forms.IntegerField(
        min_value=0,
        max_value=10,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "input100 input100-right", "required": True}
        ),
        error_messages={
            "invalid": _("لطفا عدد وارد کنید"),
            "min_value": _("عدد نمیتواند منفی باشد"),
            "max_value": _("عدد نمیتواند بیشتر از ۱۰ باشد"),
        },
    )

    price_of_each_row = forms.DecimalField(
        max_digits=9,
        decimal_places=0,
        widget=forms.TextInput(
            attrs={"class": "input100 input100-right", "required": True}
        ),
        required=True,
    )

    last_row_value = forms.DecimalField(
        required=True,
        widget=forms.TextInput(
            attrs={"class": "input100 input100-right", "required": True}
        ),
        error_messages={"invalid": _("لطفا عدد وارد کنید")},
    )

    def clean_row_number(self):
        cleaned_data = super().clean()
        price_of_each_row = cleaned_data.get("price_of_each_row")
        row_number = cleaned_data.get("row_number")
        if row_number == 1:
            raise forms.ValidationError(_("تعداد سطر باید بیشتر از یک باشد"))

        return row_number


class StampForm(forms.Form):
    reason = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "input100 input100-right", "required": True}
        ),
        error_messages={"max_length": _("نمی تواند بیشتر از ۱۰۰ کاراکتر باشد")},
    )

    limit = forms.IntegerField(
        min_value=0,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "input100 input100-right", "required": True}
        ),
        error_messages={"min_value": _("نمی تواند کمتر از صفر باشد")},
    )


class FestivalForm(forms.ModelForm):
    start_date = JalaliDateField(widget=AdminJalaliDateWidget)
    start_date.widget.attrs.update(
        {"class": "jalali_date-date form-control mt-1", "autocomplete": "off"}
    )

    end_date = JalaliDateField(widget=AdminJalaliDateWidget)
    end_date.widget.attrs.update(
        {"class": "jalali_date-date form-control mt-1", "autocomplete": "off"}
    )

    winners_prizes = forms.JSONField(
        error_messages={"invalid": _("لطفا جایزه تمام برنده ها را وارد کنید")},
        required=False,
        widget=forms.TextInput(attrs={"class": "d-none", "required": False}),
    )

    class Meta:
        model = Festival
        fields = [
            "name",
            "start_date",
            "end_date",
            "min_stamp",
            "number_of_winners",
            "description_link",
            "winners_prizes",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control ",
                    "required": True,
                    "autocomplete": "off",
                }
            ),
            "min_stamp": forms.TextInput(
                attrs={
                    "class": "form-control mt-1",
                    "required": True,
                    "autocomplete": "off",
                    "maxlength": 2,
                },
            ),
            "description_link": forms.TextInput(
                attrs={
                    "class": "form-control mt-1",
                    "autocomplete": "off",
                    "maxlength": 2,
                },
            ),
            "number_of_winners": forms.TextInput(
                attrs={"class": "form-control mb-3", "required": True, "maxlength": 2}
            ),
        }

    def clean_winners_prizes(self):
        winner_prizes = self.cleaned_data["winners_prizes"]
        # print('winner_prizes', winner_prizes)

        if not winner_prizes:
            raise ValidationError(_("لطفا جایزه هر برنده را وارد کنید"))

        for key, v in winner_prizes.items():
            if not winner_prizes[key].strip():
                return ValidationError(_("لطفا جایزه تمام برنده ها را وارد کنید"))
        return winner_prizes

    def clean_number_of_winners(self):
        number_of_winners = self.cleaned_data["number_of_winners"]
        if number_of_winners == 1:
            raise ValidationError(_("تعداد برندگان باید از ۱ بیشتر باشد"))

        return number_of_winners


class FestivalFirstWinner(forms.Form):
    def __init__(self, *args, **kwargs):
        self.participiant_stamps = kwargs.pop("participiant_stamps_1", None)
        super().__init__(*args, **kwargs)

    first_winner_number = forms.IntegerField(
        widget=forms.TextInput(attrs={"class": "form-control fa-num"})
    )

    def clean_first_winner_number(self):
        number = self.cleaned_data["first_winner_number"]
        participiant_stamps = self.participiant_stamps
        # print('type(number)',type(number))

        # festival = Festival.objects.last()
        # each_user_stamp , ـ = each_user_stamps_and_all_stamps_in_active_festival(Festival, User, DATA_KEY_LIST)
        # participiant_stamps = sum(x[1] for x in filter(lambda x: x,  map(lambda elem: elem if elem[1] >=  festival.min_stamp else None, each_user_stamp[1:])))

        # if number > participiant_stamps:
        #     raise ValidationError(f'عدد قرعه کشی نمیتواند از ({participiant_stamps})  بیشتر باشد ')

        # if  number == 0 or number < 0 :
        #     raise ValidationError(f'عدد قرعه کشی نمیتواند صفر یا کوچکتر باشد  ')

        if number < 0 or number > participiant_stamps:
            raise ValidationError(
                f"شماره قرعه کشی باید بین [ ۰ , { participiant_stamps} ] باشد! ⛔"
            )

        return number

class BirthDateForm(forms.Form):
    birth_date = JalaliDateField(
        widget=AdminJalaliDateWidget,
    )
    birth_date.widget.attrs.update(
        {
            "class": "form-control jalali_date-date",
            "id": "birth_date",
            "autocomplete": "off",
            "placeholder": "تاریخ تولدتان را وارد کنید",
        }
    )

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')  

        if birth_date:  
            if birth_date > timezone.now().date():  
                raise forms.ValidationError("تاریخ تولد تا امروز میتواند باشد.")  

        return birth_date  
