import copy
import json
# from django.core.serializers import serialize
import random
import re
import time
import traceback
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional
from urllib.parse import unquote

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import IntegrityError, transaction
# from django.db.models import F ,ExpressionWrapper ,IntegerField, Count, When, Case, Value
from django.db.models import Value
from django.db.models.functions import Coalesce, Concat
from django.http import HttpRequest, JsonResponse
from django.shortcuts import HttpResponse, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from jalali_date import date2jalali, jdatetime
from openpyxl import Workbook
from persian_tools import digits
from requests import Response
from requests.exceptions import ConnectionError, RequestException

from moshtari.tasks import send_text_message

from .forms import (BirthDateForm, Festival, FestivalFirstWinner, FestivalForm,
                    SettingTableForm, StampForm, StampReasonForm)
from .models import *

ResponseType = Optional[Response]


def retry_request(
    url: str,
    headers: Optional[Dict] = None,
    data: Optional[Dict] = None,
    max_retries: int = 3,
    retry_delay: int = 1,
    method: str = "get",
) -> ResponseType:
    for i in range(max_retries):
        try:
            if method == "get":
                response = requests.get(url, headers=headers)

            if method == "post":
                response = requests.post(url, headers=headers, data=data)
            # response.raise_for_status()
            print("res", response)
            print("Connection successful")
            return response
        except ConnectionError as ce:
            error_message = f"Connection error on attempt {i+1}: {ce}"
            # save_error_to_log(url, error_message)
            print(url, error_message)
            if i < max_retries - 1:
                print("Retrying...")
                time.sleep(retry_delay)
        except RequestException as re:
            error_message = f"Other request error: {re}"
            print(url, error_message)
            return None
    return None


DATA_KEY_LIST = settings.DATA_KEY_LIST


is_staff_user = lambda user: user.is_staff
is_authenticated_user = lambda user: user.is_authenticated

NOT_FESTIVAL_stamps = ["فیزیکی", "هدیه تولد"]


def add_leading_zeros(input_str):
    input_str = str(input_str)
    num_zeros = max(0, 10 - len((input_str)))
    result_str = "0" * num_zeros + input_str
    # print(result_str)
    return result_str


def get_user_with_id_card_num(id_card_num, user_obj):
    return (
        user_obj.objects.filter(id_card_num=id_card_num)
        .select_related("parent_user")
        .first()
    )


def table_is_full_or_not(table_data) -> bool:
    """
    If result be True mean that card is full.
    """
    columns_num = 0
    counter = 0
    row_number = 0
    for key, va in table_data.items():
        if key.split("_")[0] not in DATA_KEY_LIST:
            row_number += 1

            if not columns_num:
                columns_num = sum(1 for column in va if column.startswith("column_"))
            # print('columns_number', columns_num)
            all_column_stamped_or_not = all(
                [va[f"column_{i + 1}"]["stamp"] for i in range(columns_num)]
            )
            if all_column_stamped_or_not:
                counter += 1
    # print(row_number)
    if counter == row_number:
        return True

    return False


def calculate_user_unuzed_discount(all_cards):
    unused_prize = 0
    columns_num = 0
    for card in all_cards:
        for key, va in card.award_tick_table.items():
            prize = key.split("_")[0]
            if prize not in DATA_KEY_LIST:

                if not columns_num:
                    columns_num = sum(
                        1 for column in va if column.startswith("column_")
                    )
                # print('columns_number', columns_num)
                all_column_stamped_or_not = all(
                    [va[f"column_{i + 1}"]["stamp"] for i in range(columns_num)]
                )

                if all_column_stamped_or_not and not va.get("is_used", ""):
                    unused_prize += Decimal(prize)

    return unused_prize


def get_count_user_tables(user):
    return UserGiftData.objects.filter(user=user).count()


def buy_product_count(table_data):
    columns_num = 0
    buy_product_count = 0
    for key, va in table_data.items():

        if key.split("_")[0] not in DATA_KEY_LIST:

            if not columns_num:
                columns_num = sum(1 for column in va if column.startswith("column_"))

            buy_product_count += sum(
                1
                for i in range(columns_num)
                if "خرید محصول" in va[f"column_{i + 1}"]["reason"]
            )

    # print('buy_product_count', buy_product_count)
    return buy_product_count


def stamp_reason_conter_in_all_user_cards(
    user, gift_table_model, reason: str, card_key_list
):
    columns_num = 0

    card_list = tuple(
        map(
            lambda gift_table: gift_table.award_tick_table,
            gift_table_model.objects.filter(user=user),
        )
    )
    stamp_cont = 0
    for card in card_list:
        for key, va in card.items():
            if key.split("_")[0] not in card_key_list:

                if not columns_num:
                    columns_num = sum(
                        1 for column in va if column.startswith("column_")
                    )

                stamp_cont += sum(
                    1
                    for i in range(columns_num)
                    if reason in va[f"column_{i + 1}"]["reason"]
                )
                # insta_mention_count += sum(1 for i in range(columns_num) if 'استوری ۲۴ ساعته در اینستاکرام' in va[f'column_{i + 1}']['reason'])

    return stamp_cont


def any_column_is_full_or_not(table_data):
    columns_num = 0
    column_is_used = ""
    for key, va in table_data.items():
        if key.split("_")[0] not in DATA_KEY_LIST:

            if not columns_num:
                columns_num = sum(1 for column in va if column.startswith("column_"))

            all_column_stamped_or_not = all(
                [va[f"column_{i + 1}"]["stamp"] for i in range(columns_num)]
            )
            # print(type(va))
            # print(va)
            column_is_used = va["is_used"]
            if all_column_stamped_or_not and not column_is_used:
                return True

    return False


def all_stamp_count(user, card_model, card_key_list):
    columns_num = 0
    stamp_count = 0

    for card in card_model.objects.filter(user=user):
        for key, va in card.award_tick_table.items():
            if key.split("_")[0] in card_key_list:
                continue
            if not columns_num:
                columns_num = sum(1 for column in va if column.startswith("column_"))

            stamp_count += sum(
                1 for i in range(columns_num) if va[f"column_{i + 1}"]["stamp"]
            )
    return stamp_count


def all_is_used_discount(user, card_model, card_key_list):
    all_used_discount = 0

    for card in card_model.objects.filter(user=user):
        for key, va in card.award_tick_table.items():
            if key.split("_")[0] in card_key_list:
                continue
            if va["is_used"]:
                all_used_discount += Decimal(key.split("_")[0])
    return Decimal(all_used_discount)


def festival_ended_or_not(festival_model):
    festival = festival_model.objects.last()
    return festival and (festival.start_date <= date.today() <= festival.end_date)


def festival_ended_and_lottery_was_not_done(festival):
    if not festival:
        return False
    return festival.end_date < date.today() and not festival.lottery_was_done


def each_user_stamps_and_all_stamps_in_active_festival(
    festival_model, user_model, card_key_list
):
    try:
        festival = festival_model.objects.last()
        if not festival:
            return False, False
        s_date = festival.start_date
        e_date = festival.end_date

        users = user_model.objects.prefetch_related("cards").all()
        users_cards = tuple(map(lambda user: (user, user.cards.all()), users))

        all_stamps_in_festival = 0
        users_festival_stamps_count = []
        for user, cards in users_cards:
            stamp_count_in_festival = 0
            columns_num = 0
            for card in cards:
                user_card = card.award_tick_table
                for key, va in user_card.items():
                    if key.split("_")[0] in card_key_list:
                        continue
                    if not columns_num:
                        columns_num = sum(
                            1 for column in va if column.startswith("column_")
                        )

                    stamp_count_in_festival += sum(
                        1
                        for i in range(columns_num)
                        if (
                            va[f"column_{i + 1}"]["stamp"]
                            and (
                                s_date
                                <= datetime.fromisoformat(
                                    va[f"column_{i + 1}"]["date"]
                                ).date()
                                <= e_date
                            )
                        )
                        and all(
                            [
                                s not in va[f"column_{i + 1}"]["reason"]
                                for s in NOT_FESTIVAL_stamps
                            ]
                        )
                    )
            all_stamps_in_festival += stamp_count_in_festival
            users_festival_stamps_count.append((user, stamp_count_in_festival))
    except Exception as e:
        print(e)
    users_festival_stamps_count = tuple(
        filter(
            lambda elem: elem,
            map(
                lambda x: x if x[1] >= festival.min_stamp else None,
                users_festival_stamps_count,
            ),
        )
    )
    return (
        sorted(users_festival_stamps_count, key=lambda elem: elem[1], reverse=True),
        all_stamps_in_festival,
    )


def each_user_stamps_in_festival(festival, user, card_key_list):
    if not festival:
        return False
    s_date = festival.start_date
    e_date = festival.end_date

    cards = user.cards.all()
    stamp_count_in_festival = 0
    columns_num = 0
    for card in cards:
        user_card = card.award_tick_table
        for key, va in user_card.items():
            if key.split("_")[0] in card_key_list:
                continue
            if not columns_num:
                columns_num = sum(1 for column in va if column.startswith("column_"))

            stamp_count_in_festival += sum(
                1
                for i in range(columns_num)
                if va[f"column_{i + 1}"]["stamp"]
                and (
                    s_date
                    <= datetime.fromisoformat(va[f"column_{i + 1}"]["date"]).date()
                    <= e_date
                )
                and all(
                    [
                        s not in va[f"column_{i + 1}"]["reason"]
                        for s in NOT_FESTIVAL_stamps
                    ]
                )
            )

    return stamp_count_in_festival


def user_invites_and_user_customers(user, card_key_list):
    all_invited_users_count = user.referall_users.count()
    # if not all_invited_users_count: return 0, 0

    users_did_firts_purchase = 0
    columns_num = 0
    for card in user.cards.all():
        user_card = card.award_tick_table
        for key, va in user_card.items():
            if key.split("_")[0] in card_key_list:
                continue
            if not columns_num:
                columns_num = sum(1 for column in va if column.startswith("column_"))

            users_did_firts_purchase += sum(
                1
                for i in range(columns_num)
                if "خرید نفر معرفی شده" in va[f"column_{i + 1}"]["reason"]
                or "دستی" in va[f"column_{i + 1}"]["reason"]
            )

    # users_did_not_first_purchase =  all_invited_users_count - users_did_firts_purchase
    return users_did_firts_purchase, all_invited_users_count


def toggle_sort_roder(current_order):
    return not current_order


@login_required(login_url="/")
@user_passes_test(is_staff_user, login_url="/")
def user_list(request):

    if request.method == "GET":
        sort_by = request.GET.get("sort_by", "")
        page_sort = request.GET.get("page", None)
        # print('page', page_sort)

        users = get_user_model().objects.all()

        asc_register_date = (
            request.GET.get("asc_register_date", "false").lower() == "true"
        )
        asc_last_login = request.GET.get("asc_last_login", "false").lower() == "true"
        asc_customers = request.GET.get("asc_customers", "false").lower() == "true"
        birth_date = request.GET.get("birth_date", "false").lower() == "true"

        if page_sort:
            asc_register_date = toggle_sort_roder(asc_register_date)
            asc_last_login = toggle_sort_roder(asc_last_login)
            asc_customers = toggle_sort_roder(asc_customers)
            birth_date = toggle_sort_roder(birth_date)
            # print(birth_date)
        # print('asc_register_date1', asc_register_date)
        # print('asc_last_login1', asc_last_login)
        # print('asc_customers1', asc_customers)

        if sort_by == "birth_date":
            users = users.filter(birth_date__isnull=False).order_by(
                "birth_date_status" if birth_date else "-birth_date_status"
            )

            birth_date = toggle_sort_roder(birth_date)
            print(birth_date)

        if sort_by == "register_date" or not sort_by:
            users = users.order_by(
                "date_joined" if not asc_register_date else "-date_joined"
            )
            asc_register_date = toggle_sort_roder(asc_register_date)
            # print('asc_register_date', asc_register_date)

        if sort_by == "last_login":
            users = (
                users.filter(last_login__isnull=False)
                .exclude(username="developer")
                .order_by(
                    "last_login" if not asc_last_login else "-last_login",
                )
            )
            # users = users.annotate(null_last_login=Case(
            #     When(last_login__isnull=True,
            #          then=Value('1111-12-31')),
            #     default=F('last_login'),
            #     output_field=models.DateTimeField(),)).\
            #         order_by('null_last_login' if not asc_last_login else '-null_last_login', 'date_joined')

            asc_last_login = toggle_sort_roder(asc_last_login)
            # print('asc_last_login', asc_last_login)

        if sort_by == "customers":
            users = users.order_by("customers" if not asc_customers else "-customers")
            asc_customers = toggle_sort_roder(asc_customers)
            # print('asc_customers', asc_customers)

        # Paginate items
        items_per_page = 20
        paginator = Paginator(users, items_per_page)
        default_page = 1
        page = int(request.GET.get("page", paginator.num_pages))

        try:
            items_page = paginator.page(page)
        except PageNotAnInteger:
            items_page = paginator.page(default_page)
        except EmptyPage:
            items_page = paginator.page(paginator.num_pages)

        next_pages_items_count = sum(
            items_per_page for i in range(page, paginator.num_pages)
        )
        last_page_items_num = paginator.count - (
            (paginator.num_pages - 1) * items_per_page
        )

        return render(
            request,
            "moshtari/user_list.html",
            {
                "request_user": request.user,
                "items_page": items_page,
                "user_count": paginator.count
                - (next_pages_items_count + last_page_items_num),
                "sort_by": sort_by,
                "asc_last_login": asc_last_login,
                "asc_register_date": asc_register_date,
                "asc_customers": asc_customers,
                "birth_date": birth_date
            },
        )


def calculate_age(b_date: datetime) -> str:
    if b_date is not None:
        today = timezone.now().date()  # Get today's date
        age = today.year - b_date.year  # Calculate age in years
        # Check if the birthday has occurred this year yet
        if (today.month, today.day) < (b_date.month, b_date.day):
            age -= 1  # Subtract 1 if the birthday hasn't occurred yet this year
        return digits.convert_to_fa(str(age))
    return ""  # Return '-' if there is no birth date


def ajax_search(request):

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        id_card_num_or_name = request.GET.get("id_card_num_or_name")

        if id_card_num_or_name.isdigit():
            users = (
                get_user_model()
                .objects.filter(id_card_num__icontains=id_card_num_or_name)
                .select_related("parent_user")
                .prefetch_related("cards")
                .all()
            )
            # .values('last_login','customers', 'id_card_num','referral_code', 'parent_user', 'is_verified', 'phone_number', 'email', 'first_name', 'last_name', 'date_joined', )

        else:
            users = (
                get_user_model()
                .objects.annotate(
                    full_name=Concat("first_name", Value(" "), "last_name")
                )
                .filter(full_name__icontains=id_card_num_or_name)
                .select_related("parent_user")
                .prefetch_related("cards")
                .all()
            )
            # .values('last_login','customers', 'id_card_num','referral_code', 'parent_user', 'is_verified', 'phone_number', 'email', 'first_name', 'last_name', 'date_joined', )

        # Convert the PhoneNumber objects to their string representation
        # users = list(users)
        users_data = []

        for user in users:
            user_last_card_id = user.cards.last().id
            users_data.append(
                {
                    "id": user.id,
                    "last_login": user.last_login,
                    "customers": user.customers,
                    "id_card_num": user.id_card_num,
                    "referral_code": user.referral_code,
                    "parent_user": user.parent_user,
                    "is_verified": user.is_verified,
                    "phone_number": str(user.phone_number),
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "date_joined": user.date_joined,
                    "last_card_id": user_last_card_id,
                    "birth_date": user.birth_date,
                    "birth_date_status": user.birth_date_status,
                    "age": calculate_age(user.birth_date),
                }
            )
            # user['phone_number'] = str(user['phone_number'])
            # last_card = user['cards'].last() if user['cards'] else None
            # user['last_card'] = serialize('json', [last_card]) if last_card else None

        return JsonResponse(
            users_data,
            safe=False,
        )

    return JsonResponse({"error": "Invalid request method"}, status=400)


@login_required(login_url="/")
def last_user_table(request, id_card_num):
    user_table_count = 0

    fixed_id_card_num = add_leading_zeros(id_card_num)
    user = get_user_model().objects.filter(id_card_num=fixed_id_card_num).first()

    # user_table_count = 0
    if not user:
        return HttpResponse(f"با این {fixed_id_card_num} کدملی کاربری وجود ندارد")

    user_table_count = get_count_user_tables(user)
    data = {}
    big_gift = 0
    user_table = ""
    if request.method == "GET":
        if user.is_authenticated:
            user_table = UserGiftData.objects.filter(user=user).last()
            if user_table:
                data = user_table.award_tick_table
                big_gift = user_table.big_award

                all_user_cards = user.cards.all()
                unused_prize = calculate_user_unuzed_discount(all_user_cards)
                return render(
                    request,
                    "moshtari/last_user_table.html",
                    {
                        "data": data,
                        "big_gift": big_gift,
                        "user": user,
                        "request_user": request.user,
                        "table_created_at": user_table.created_at,
                        "data_key_list": DATA_KEY_LIST,
                        "unused_prize": unused_prize,
                        "user_table_count": user_table_count,
                    },
                )

            return render(
                request,
                "moshtari/table_dose_not_exist.html",
                {
                    "user": user,
                    "request_user": request.user,
                    "user_table_count": user_table_count,
                },
            )

    if request.method == "POST":
        button = request.POST.get("button")
        if button == "new_table":
            latest_user_table_query = UserTableData.objects.order_by("-created_at")
            if latest_user_table_query.exists():
                last_setting_table = latest_user_table_query.first()
                user_table = UserGiftData.objects.create(
                    user=user,
                    award_tick_table=last_setting_table.award_tick_table,
                    big_award=last_setting_table.big_award,
                )
                if user_table:
                    return redirect(f"/last_user_table/{id_card_num}/")

                else:
                    return HttpResponse("مشکل در ایجاد جدول به برنامه نویس اطلاع دهید")

            else:
                return HttpResponse(
                    "هنوز برای سیستم جدولی تنظیم نشده لطفا ابتدا به تنظیمات جدول رفته و جدول ایجاد کنید"
                )

        return HttpResponse("Unauthorized", status=401)


@login_required(login_url="/")
@user_passes_test(is_authenticated_user, login_url="/")
def table_view(request, id_card_num, table_id):
    user = get_user_with_id_card_num(id_card_num, get_user_model())
    request_user = request.user
    if user:
        user_table = UserGiftData.objects.filter(user=user, id=table_id).first()
        if user_table:
            origin_data = user_table.award_tick_table
            data = copy.deepcopy(origin_data)

            big_gift = user_table.big_award

            if user.parent_user:
                parent_user_table = UserGiftData.objects.filter(
                    user=user.parent_user
                ).last()

            # form1 = PrizeForm(id_card_num)
            reasons = stamp_reasons.objects.all()

            if table_is_full_or_not(data):
                data["is_table_full"] = True
                user_table.award_tick_table = data
                user_table.save()

            if request.method == "GET":
                form = StampReasonForm(reasons)
                button = request.GET.get("button")
                # print(data)
                any_column_is_full = any_column_is_full_or_not(data)
                user_table_count = get_count_user_tables(user)

                # Get all user cards
                all_user_cards = user.cards.all()
                unused_prize = 0
                if not request_user.is_staff and not request_user.is_superuser:
                    unused_prize = calculate_user_unuzed_discount(all_user_cards)

                return render(
                    request,
                    "moshtari/stamp_table.html",
                    {
                        "data": data,
                        "big_gift": big_gift,
                        "user": user,
                        "request_user": request_user,
                        "data_key_list": DATA_KEY_LIST,
                        "form": form,
                        "table_created_at": user_table.created_at,
                        "any_column_is_full": any_column_is_full,
                        "user_table_count": user_table_count,
                        "unused_prize": unused_prize,
                        "card_id": table_id,
                    },
                )

            if request.method == "POST":
                date = datetime.now()
                form = StampReasonForm(reasons, request.POST)
                button = request.POST.get("button")

                if button == "delete_stamp" and request_user.is_superuser:
                    table_rows_key = [
                        row_key
                        for row_key, _ in data.items()
                        if row_key.split("_")[0] not in DATA_KEY_LIST
                    ]
                    breaker = False
                    buying_product_count = buy_product_count(data)
                    for row in reversed(table_rows_key):
                        row_key_obj = data[row]
                        row_columns = [
                            key_column
                            for key_column, va in row_key_obj.items()
                            if "column_" in key_column
                        ]
                        for column in row_columns:
                            # print(row, data[row][column]['stamp'])
                            if data[row][column]["stamp"] == True:
                                data[row][column]["stamp"] = False

                                data[row][column]["date"] = ""
                                data[row][column]["admin"] = ""
                                data[row]["is_used"] = False
                                data[row]["is_used_date"] = ""
                                data["use_big_gift"] = False
                                data["is_table_full"] = False

                                # delete parent stamp
                                if (
                                    "خرید محصول" in data[row][column]["reason"]
                                    and user.parent_user
                                    and buying_product_count == 1
                                ):

                                    if user.parent_user.customers > 0:
                                        user.parent_user.customers -= 1
                                        user.parent_user.save()
                                    data["send_message_parent"] = False

                                    parent_data_delete = (
                                        parent_user_table.award_tick_table
                                    )

                                    parent_table_rows_key = [
                                        row_key
                                        for row_key, _ in parent_data_delete.items()
                                        if row_key.split("_")[0] not in DATA_KEY_LIST
                                    ]
                                    breaker_2 = False
                                    for parent_row in parent_table_rows_key:
                                        parent_row_key_obj = parent_data_delete[
                                            parent_row
                                        ]
                                        paretn_row_columns = [
                                            key_column
                                            for key_column, va in parent_row_key_obj.items()
                                            if "column_" in key_column
                                        ]
                                        for parent_column in reversed(
                                            paretn_row_columns
                                        ):
                                            # print('parent_data_delete[parent_row][parent_column]', parent_data_delete[parent_row][parent_column])
                                            if (
                                                f"خرید نفر معرفی شده ({user.first_name} {user.last_name})"
                                                in parent_data_delete[parent_row][
                                                    parent_column
                                                ]["reason"]
                                            ):
                                                parent_data_delete[parent_row][
                                                    parent_column
                                                ]["stamp"] = False
                                                parent_data_delete[parent_row][
                                                    parent_column
                                                ]["reason"] = ""
                                                parent_data_delete[parent_row][
                                                    parent_column
                                                ]["admin"] = ""
                                                parent_data_delete[parent_row][
                                                    parent_column
                                                ]["date"] = ""
                                                parent_data_delete[parent_row][
                                                    "is_used"
                                                ] = False
                                                parent_data_delete[parent_row][
                                                    "is_used_date"
                                                ] = ""
                                                parent_data_delete["is_table_full"] = (
                                                    False
                                                )

                                                parent_user_table.award_tick_table = (
                                                    parent_data_delete
                                                )
                                                parent_user_table.save()

                                                breaker_2 = True
                                                messages.success(
                                                    request,
                                                    _(
                                                        "مهر معرف حذف شد و پیام فرستاده شده بی اعتبار شد"
                                                    ),
                                                )
                                                break

                                        if breaker_2:
                                            break

                                if "دستی" in data[row][column]["reason"]:
                                    if user.customers > 0:
                                        user.customers -= 1
                                        user.save()

                                data[row][column]["reason"] = ""
                                user_table.award_tick_table = data
                                any_column_is_full = any_column_is_full_or_not(data)
                                user_table.save()
                                # messages.info(request,_( 'اخرین مهر حذف شد'))
                                breaker = True
                                # print(table_rows_key[0], row_columns[0], row, column)
                                break
                                # return render(request, 'moshtari/stamp_table.html', {'data': data, 'big_gift': big_gift, 'user': user, 'request_user':request_user , 'data_key_list': DATA_KEY_LIST, 'form': form, 'form1':form1  })
                        if breaker:
                            break
                    else:
                        messages.info(request, _("همه مهر هاحذف شده اند"))

                if button == "stamp":
                    if form.is_valid():
                        selected_option = form.cleaned_data["selected_option"]
                        selected_reason = stamp_reasons.objects.filter(
                            id=int(selected_option)
                        ).first()
                        breaker = False
                        for key, value in data.items():
                            if type(value) == dict:

                                for key_in, value_in in reversed(value.items()):
                                    if "column" in key_in:

                                        if not value_in["stamp"]:
                                            value_in["stamp"] = True
                                            value_in["reason"] = selected_reason.reason
                                            value_in["admin"] = request_user.last_name
                                            value_in["date"] = date.isoformat()

                                            stamp_count = (
                                                stamp_reason_conter_in_all_user_cards(
                                                    user,
                                                    UserGiftData,
                                                    selected_reason.reason,
                                                    DATA_KEY_LIST,
                                                )
                                            )
                                            if (
                                                selected_reason.limit
                                                and stamp_count >= selected_reason.limit
                                            ):
                                                messages.error(
                                                    request,
                                                    _(
                                                        f"کاربر قبلا به دلیل {selected_reason.reason} {digits.convert_to_fa(stamp_count)} عدد مهر دریافت کرده است."
                                                    ),
                                                )
                                                return redirect(
                                                    f"/table_view/{ user.id_card_num}/{table_id}/",
                                                    {
                                                        "data": origin_data,
                                                        "big_gift": big_gift,
                                                        "user": user,
                                                        "request_user": request_user,
                                                        "data_key_list": DATA_KEY_LIST,
                                                        "form": form,
                                                        "table_created_at": user_table.created_at,
                                                        "any_column_is_full": any_column_is_full_or_not(
                                                            origin_data
                                                        ),
                                                    },
                                                )

                                            # if  'استوری ۲۴ ساعته در اینستاکرام' in value_in['reason'] and mention_count >= 2:
                                            #         messages.error(request, _(f'کاربر قبلا به دلیل منشن در اینستاگرام {digits.convert_to_fa(mention_count)} عدد مهر دریافت کرده است'))
                                            #         return redirect(f"/table_view/{ user.id_card_num}/{table_id}/",
                                            #                         {'data': origin_data, 'big_gift': big_gift, 'user': user,
                                            #                         'request_user':request_user , 'data_key_list': DATA_KEY_LIST,
                                            #                         'form': form, 'table_created_at': user_table.created_at,
                                            #                         'any_column_is_full': any_column_is_full_or_not(origin_data)})

                                            if "دستی" in value_in["reason"]:
                                                user.customers += 1
                                                user.save()

                                            if not data["send_message_parent"]:
                                                # send first buy message to parent user once
                                                if user.parent_user and (
                                                    "خرید محصول" in value_in["reason"]
                                                ):
                                                    # print('hahaha' * 50)

                                                    # write send message here to
                                                    user.parent_user.customers += 1
                                                    user.parent_user.save()
                                                    if parent_user_table:
                                                        parent_data = (
                                                            parent_user_table.award_tick_table
                                                        )
                                                        # print(type(parent_data))
                                                        breaker = False
                                                        for (
                                                            key_parent,
                                                            value_parent,
                                                        ) in parent_data.items():
                                                            if type(value) == dict:
                                                                for (
                                                                    key_parent_in,
                                                                    value_parent_in,
                                                                ) in reversed(
                                                                    value_parent.items()
                                                                ):
                                                                    if (
                                                                        "column"
                                                                        in key_parent_in
                                                                    ):
                                                                        if not value_parent_in[
                                                                            "stamp"
                                                                        ]:
                                                                            value_parent_in[
                                                                                "stamp"
                                                                            ] = True
                                                                            value_parent_in[
                                                                                "reason"
                                                                            ] = _(
                                                                                f"خرید نفر معرفی شده ({user.first_name} {user.last_name})"
                                                                            )
                                                                            value_parent_in[
                                                                                "admin"
                                                                            ] = "سیستم اتوماتیک"
                                                                            date = (
                                                                                datetime.now()
                                                                            )
                                                                            value_parent_in[
                                                                                "date"
                                                                            ] = (
                                                                                date.isoformat()
                                                                            )
                                                                            if table_is_full_or_not(
                                                                                parent_data
                                                                            ):
                                                                                parent_data[
                                                                                    "is_table_full"
                                                                                ] = True
                                                                            parent_user_table.award_tick_table = parent_data
                                                                            parent_user_table.save()
                                                                            messages.success(
                                                                                request,
                                                                                _(
                                                                                    "مهر معرف زده شد"
                                                                                ),
                                                                            )
                                                                            breaker = (
                                                                                True
                                                                            )
                                                                            break
                                                            if breaker:
                                                                break
                                                    full_name = f"{user.first_name} {user.last_name}"
                                                    message = f"نفر معرفی شده شما جناب آقای/خانم {full_name} اولین خرید خود را انجام داد و به همین خاطر کارت شما نیز مهر خورد. \n cc.bartardigital.com"
                                                    data_message = {
                                                        "from": "500010609865",
                                                        "to": str(
                                                            user.parent_user.phone_number
                                                        ),
                                                        "text": message,
                                                    }
                                                    send_text_message.delay(
                                                        data_message, full_name
                                                    )
                                                    # response = requests.post('https://console.melipayamak.com/api/send/simple/a8b3b5300f9042b898815c3d83508d8a', json=data_message)
                                                    # if response.status_code == 200:
                                                    messages.success(
                                                        request,
                                                        _(
                                                            f' یک پیام برای معرف ({user.parent_user.first_name + " " + user.parent_user.last_name}) ارسال شد'
                                                        ),
                                                    )
                                                    # else:
                                                    # messages.error('ارسال پیامک با مشکل مواجه شده است.')
                                                    data["send_message_parent"] = True

                                            if table_is_full_or_not(data):
                                                data["is_table_full"] = True

                                            user_table.award_tick_table = data
                                            user_table.save()
                                            breaker = True
                                            break
                            if breaker:
                                break

                        # if data.get('is_table_full', None):
                        #     messages.warning(request, _('جدول  جایی برای مهر زدن ندارد'))
                        any_column_is_full = any_column_is_full_or_not(data)
                        return redirect(
                            f"/table_view/{ user.id_card_num}/{table_id}/",
                            {
                                "data": data,
                                "big_gift": big_gift,
                                "user": user,
                                "request_user": request_user,
                                "data_key_list": DATA_KEY_LIST,
                                "form": form,
                                "table_created_at": user_table.created_at,
                                "any_column_is_full": any_column_is_full,
                                "card_id": table_id,
                            },
                        )

                if button == "used":
                    data_table = user_table.award_tick_table

                    columns_num = 0
                    for key, va in data_table.items():
                        if key.split("_")[0] not in DATA_KEY_LIST:

                            columns_num = sum(
                                1 for column in va if column.startswith("column_")
                            )
                            # print('columns_number', columns_num)
                            all_column_stamped_or_not = all(
                                [
                                    va[f"column_{i + 1}"]["stamp"]
                                    for i in range(columns_num)
                                ]
                            )
                            if all_column_stamped_or_not:

                                if data_table[key]["is_used"] == False:
                                    data_table[key]["is_used"] = True
                                    data_table[key]["is_used_date"] = date.isoformat()
                                    user_table.award_tick_table = data_table
                                    user_table.save()

                                    return redirect(
                                        f"/table_view/{ user.id_card_num}/{table_id}/",
                                        {
                                            "data": data_table,
                                            "big_gift": big_gift,
                                            "user": user,
                                            "request_user": request_user,
                                            "data_key_list": DATA_KEY_LIST,
                                            "form": form,
                                            "table_created_at": user_table.created_at,
                                            "any_column_is_full": any_column_is_full_or_not(
                                                data_table
                                            ),
                                            "card_id": table_id,
                                        },
                                    )

                if button == "undo_used" and request_user.is_superuser:
                    data_table = user_table.award_tick_table
                    columns_num = 0
                    for key, va in reversed(data_table.items()):
                        if key.split("_")[0] not in DATA_KEY_LIST:
                            if data_table[key]["is_used"]:
                                data_table[key]["is_used"] = False
                                # i wanna know deleted time
                                data_table[key]["is_used_date"] = ""
                                user_table.award_tick_table = data_table
                                user_table.save()

                                return redirect(
                                    f"/table_view/{ user.id_card_num}/{table_id}/",
                                    {
                                        "data": data_table,
                                        "big_gift": big_gift,
                                        "user": user,
                                        "request_user": request_user,
                                        "data_key_list": DATA_KEY_LIST,
                                        "form": form,
                                        "table_created_at": user_table.created_at,
                                        "any_column_is_full": any_column_is_full_or_not(
                                            data_table
                                        ),
                                        "card_id": table_id,
                                    },
                                )

                if button == "new_table":
                    if table_is_full_or_not(data):
                        any_column_is_full = any_column_is_full_or_not(data)
                        latest_user_table_query = UserTableData.objects.order_by(
                            "-created_at"
                        )
                        if latest_user_table_query.exists():
                            user_tabel_data = latest_user_table_query.first()

                            # create a specific table data for user
                            user_award_data = UserGiftData(
                                award_tick_table=user_tabel_data.award_tick_table,
                                big_award=user_tabel_data.big_award,
                                user=user,
                            )
                            user_award_data.save()

                            return redirect(
                                f"/table_view/{id_card_num}/{user_award_data.id}/",
                                {
                                    "data": user_award_data.award_tick_table,
                                    "big_gift": user_award_data.big_award,
                                    "user": user,
                                    "request_user": request_user,
                                    "data_key_list": DATA_KEY_LIST,
                                    "form": form,
                                    "table_created_at": user_table.created_at,
                                    "card_id": table_id,
                                },
                            )

                    return redirect(
                        f"/table_view/{ user.id_card_num}/{table_id}/",
                        {
                            "data": data,
                            "big_gift": big_gift,
                            "user": user,
                            "request_user": request_user,
                            "data_key_list": DATA_KEY_LIST,
                            "form": form,
                            "table_created_at": user_table.created_at,
                            "any_column_is_full": any_column_is_full,
                            "card_id": table_id,
                        },
                    )

                # any_column_is_full = any_column_is_full_or_not(data)
                any_column_is_full = any_column_is_full_or_not(data)
                return redirect(
                    f"/table_view/{ user.id_card_num}/{table_id}/",
                    {
                        "data": data,
                        "big_gift": big_gift,
                        "user": user,
                        "request_user": request_user,
                        "data_key_list": DATA_KEY_LIST,
                        "form": form,
                        "table_created_at": user_table.created_at,
                        "any_column_is_full": any_column_is_full,
                        "card_id": table_id,
                    },
                )

        return HttpResponse(_(f"جدول{table_id} وجود ندارد"))
    return HttpResponse(_(f"با این کد ملی {id_card_num} کاربری وجود ندارد"))


@user_passes_test(is_staff_user, login_url="/")
def setting_table(request):
    form = SettingTableForm()
    form1 = StampForm()

    festival_form = FestivalForm()
    if request.method == "GET":
        return render(
            request,
            "moshtari/setting_table.html",
            {
                "form": form,
                "request_user": request.user,
                "form1": form1,
                "festival_form": festival_form,
            },
        )

    if request.method == "POST":
        button = request.POST.get("button")
        # print('button', button)

        if button == "reason":
            form1 = StampForm(request.POST)
            if form1.is_valid():
                reason = form1.cleaned_data["reason"]
                limit = form1.cleaned_data["limit"]
                # print('reason', reason)
                stamp = stamp_reasons.objects.create(reason=reason, limit=limit)
                if stamp:
                    messages.success(request, "دلیل مهر با موفقیت دخیره شد")
                else:
                    messages.error(request, "دلیل مهر دخیره نشد")
                return redirect(
                    "/setting_table/",
                    {
                        "form": form,
                        "request_user": request.user,
                        "form1": form1,
                        "festival_form": festival_form,
                    },
                )
            return render(
                request,
                "moshtari/setting_table.html",
                {
                    "form": form,
                    "request_user": request.user,
                    "form1": form1,
                    "festival_form": festival_form,
                },
            )

        if button == "setting_table":
            form = SettingTableForm(request.POST)

            if form.is_valid():
                table_obj_data = {}

                row_number = form.cleaned_data["row_number"]
                column_number_per_row = form.cleaned_data["column_number_per_row"]
                last_row_value = form.cleaned_data["last_row_value"]
                price_of_each_row = form.cleaned_data["price_of_each_row"]

                columns_obj = {}
                for i in range(1, row_number):
                    # print(i, price_of_each_row)
                    table_obj_data.update({f"{price_of_each_row}_{i}": {}})
                else:
                    table_obj_data.update({f"{last_row_value}_{row_number}": {}})

                for j in range(1, column_number_per_row + 1):
                    columns_obj.update(
                        {
                            f"column_{j}": {
                                "date": "date_time",
                                "stamp": False,
                                "reason": "text",
                                "admin": "last_name",
                            },
                            "is_used": False,
                            "is_used_date": "",
                            "send_message_self_to_is_used": False,
                        }
                    )

                for key, va in table_obj_data.items():
                    table_obj_data[key] = columns_obj

                table_obj_data["is_table_full"] = False
                table_obj_data["send_message_parent"] = False

                created = UserTableData.objects.create(
                    award_tick_table=table_obj_data,
                    big_award=((price_of_each_row * (row_number - 1)) + last_row_value),
                )
                if created:
                    messages.success(
                        request,
                        _(
                            "جدول شما ساخته شد و از این به بعد از این جدول استفاده میشود"
                        ),
                    )
                    return redirect(
                        "/setting_table/",
                        {
                            "form": form,
                            "request_user": request.user,
                            "form1": form1,
                            "festival_form": festival_form,
                        },
                    )

                else:
                    messages.error(request, _("جدول سخته نشد"))
                    return redirect(
                        "/setting_table/",
                        {
                            "form": form,
                            "request_user": request.user,
                            "form1": form1,
                            "festival_form": festival_form,
                        },
                    )

            return render(
                request,
                "moshtari/setting_table.html",
                {
                    "form": form,
                    "request_user": request.user,
                    "form1": form1,
                    "festival_form": festival_form,
                },
            )

        if button == "festival":
            festival_post_form = FestivalForm(request.POST)

            if festival_post_form.is_valid():

                if festival_ended_or_not(Festival):

                    messages.error(
                        request,
                        _(
                            "یک جشنواره فعال وجود دارد, امکان ایجاد چند جشنواره به طور همزمان وجود ندارد"
                        ),
                    )
                    return render(
                        request,
                        "moshtari/setting_table.html",
                        {
                            "form": form,
                            "request_user": request.user,
                            "form1": form1,
                            "festival_form": festival_post_form,
                        },
                    )
                festival_post_form.save()
                messages.success(
                    request,
                    "جشنواره ذخیره شد و به صورت اتوماتیک در تاریخ شروع شروع میشود.",
                )

                return render(
                    request,
                    "moshtari/setting_table.html",
                    {
                        "form": form,
                        "request_user": request.user,
                        "form1": form1,
                        "festival_form": festival_post_form,
                    },
                )
            return render(
                request,
                "moshtari/setting_table.html",
                {
                    "form": form,
                    "request_user": request.user,
                    "form1": form1,
                    "festival_form": festival_post_form,
                },
            )

        if button == "calc_users_chance_num_list":
            workbook = Workbook()
            sheet = workbook.active
            sheet["A1"] = "شماره تلفن"
            sheet["B1"] = "نام و نام خانوادگی"
            sheet["C1"] = "تعداد شانس"
            sheet["D1"] = "از"
            sheet["E1"] = "تا"

            festival = Festival.objects.all().last()
            if not festival:
                return HttpResponse("جشنواره ای وجود ندارد")

            if festival.all_taken_stamps:
                messages.error(request, "قبلا عدد شانس هر یوزر محاسبه شده است")
                return render(
                    request,
                    "moshtari/setting_table.html",
                    {
                        "form": form,
                        "request_user": request.user,
                        "form1": form1,
                        "festival_form": festival_form,
                    },
                )

            each_user_stamps, unused = (
                each_user_stamps_and_all_stamps_in_active_festival(
                    Festival, get_user_model(), DATA_KEY_LIST
                )
            )
            random.shuffle(each_user_stamps)
            stamp_sequency = 0
            each_user_chance_list = []
            stamps_of_number_one = 0
            for i, (user, stamp_count) in enumerate(each_user_stamps):
                # if i+1 == 1:
                #     try:
                #         stamps_of_number_one = stamp_count
                #         # this users can't give min_stamps and they are not in lottery
                #         festival.members.add(user, through_defaults={
                #             'festival_chance_number_list': None,
                #             'taken_stamps':stamp_count,
                #             'rank': 1,
                #             'win': True,
                #             "message_content": f'کاربر گرامی،شمادر{festival.name} بدون قرعه کشی به عنوان نفر اول برنده شدید.تبریک می گوییم!'
                #         })

                #     except Exception as e:
                #         print(e)

                #     continue

                if not stamp_count >= festival.min_stamp:
                    try:
                        # this users can't give min_stamps and they are not in lottery
                        festival.members.add(
                            user,
                            through_defaults={
                                "festival_chance_number_list": None,
                                "taken_stamps": stamp_count,
                                # 'rank': i + 1,
                                "win": False,
                                "message_content": f"برای شرکت در {festival.name} شما بایستی حداقل {digits.convert_to_fa(festival.min_stamp)} مهر داشته باشید.",
                            },
                        )

                    except Exception as e:
                        print(e)

                    continue

                until_this = stamp_sequency + stamp_count
                each_user_chance_list = [i for i in range(stamp_sequency, until_this)]

                message = f"کاربر گرامی {user.first_name} {user.last_name} ردیف های شانس شما در {festival.name} از عدد {digits.convert_to_fa(stamp_sequency)} تا {digits.convert_to_fa(until_this - 1)} می باشد"

                # Crate excel file
                sheet[f"A{i + 2}"] = str(user.phone_number).replace("+98", "0")
                sheet[f"B{i + 2}"] = f"{user.first_name} {user.last_name}"
                sheet[f"C{i + 2}"] = stamp_count
                sheet[f"D{i + 2}"] = stamp_sequency
                sheet[f"E{i + 2}"] = until_this - 1

                stamp_sequency += stamp_count

                # print('i', i + 1)
                # print('user', user)
                # print('stamp_count', stamp_count)
                # print(each_user_chance_list)
                # print('stamp_sequency', stamp_sequency)
                # print(message)
                # print('*' * 60)

                try:
                    # data_message = {'from': '500010609865', 'to': str(user.phone_number) , 'text': message}
                    # response = requests.post('https://console.melipayamak.com/api/send/simple/a8b3b5300f9042b898815c3d83508d8a', json=data_message)
                    # status = 200
                    festival.members.add(
                        user,
                        through_defaults={
                            "festival_chance_number_list": each_user_chance_list,
                            "taken_stamps": stamp_count,
                            # 'rank': i + 1,
                            # 'message_status': response.status_code,
                            # 'message_status': status
                            "message_content": message,
                        },
                    )

                except Exception as e:
                    print(
                        f"error {e} in calc_users_chance_num_list button with user {user.first_name} {user.last_name}"
                    )

            file_path = f"{settings.MEDIA_ROOT}/excel_files/{festival.start_date}until{festival.end_date}.xlsx"
            workbook.save(file_path)

            festival.excel_file = file_path
            festival.all_taken_stamps = stamp_sequency + stamps_of_number_one
            festival.step_number = int((stamp_sequency) // (festival.number_of_winners))
            festival.number_one_stamps = stamps_of_number_one
            festival.save()
            messages.success(
                request,
                "عدد شانس هر کاربر محاسبه شد و در پنل کاربریشان نشان داده میشود",
            )
            return render(
                request,
                "moshtari/setting_table.html",
                {
                    "form": form,
                    "request_user": request.user,
                    "form1": form1,
                    "festival_form": festival_form,
                },
            )


@user_passes_test(is_staff_user, login_url="/")
def last_table(request):
    if request.method == "GET":
        latest_user_table_query = UserTableData.objects.order_by("-created_at")
        if latest_user_table_query.exists():
            user_tabel_data = latest_user_table_query.first()

            return render(
                request,
                "moshtari/last_table.html",
                {
                    "data": user_tabel_data.award_tick_table,
                    "big_gift": user_tabel_data.big_award,
                    "data_key_list": DATA_KEY_LIST,
                    "request_user": request.user,
                },
            )

        return HttpResponse(_("هنوز جدولی وجود ندارد"))


@login_required(login_url="/")
def all_user_tables(request, id_card_num):
    if request.method == "GET":

        user = (
            get_user_model()
            .objects.filter(id_card_num=add_leading_zeros(id_card_num))
            .first()
        )
        all_user_tables = 0
        if user:
            user_table_count = get_count_user_tables(user)
            # print('user_table_count', user_table_count)
            all_user_tables = UserGiftData.objects.filter(user=user).all()
            table_len = len(all_user_tables)

        else:
            return HttpResponse("این کدملی وجود ندارد")

        return render(
            request,
            "moshtari/all_user_tables.html",
            {
                "user": user,
                "request_user": request.user,
                "all_user_tables": all_user_tables,
                "data_key_list": DATA_KEY_LIST,
                "table_len": table_len,
                "user_table_count": user_table_count,
            },
        )


@login_required(login_url="/")
def user_invites(request, id_card_num):
    if request.method == "GET":
        user = (
            get_user_model()
            .objects.filter(id_card_num=add_leading_zeros(id_card_num))
            .prefetch_related("parent_user")
            .first()
        )
        invited_users = tuple(
            map(lambda user: (user, user.cards.first()), user.referall_users.all())
        )

        return render(
            request,
            "moshtari/user_invites.html",
            {
                "user": user,
                "user_invites": invited_users,
                "request_user": request.user,
            },
        )


@login_required(login_url="/")
def porfile(request, referral_code):
    
    request_user = request.user
    user = (
        get_user_model()
        .objects.filter(referral_code=unquote(referral_code))
        .prefetch_related("referall_users")
        .first()
    )
    if request.method == "GET":

        # print('user', user)
        # print(referral_code)
        if not user:
            return HttpResponse(f"There is no user with this code {referral_code}")
        message = ""
        invited_users_did_firts_purchase, invited_users_did_not_first_purchase = (
            user_invites_and_user_customers(user, DATA_KEY_LIST)
        )

        festival = Festival.objects.last()
        if not festival:
            return render(
                request,
                "moshtari/profile.html",
                {
                    "request_user": request_user,
                    "user": user,
                    "user_table_count": get_count_user_tables(user),
                    "invited_users_did_firts_purchase": invited_users_did_firts_purchase,
                    "invited_users_did_not_first_purchase": invited_users_did_not_first_purchase,
                    "all_stamp_count": all_stamp_count(
                        user, UserGiftData, DATA_KEY_LIST
                    ),
                    "all_used_discount": all_is_used_discount(
                        user, UserGiftData, DATA_KEY_LIST
                    ),
                    "refferal_code": referral_code,
                    "stamps_in_festival": each_user_stamps_in_festival(
                        festival, user, DATA_KEY_LIST
                    ),
                    "form": BirthDateForm,
                },
            )
        festival_is_not_active_and_was_not_done = (
            festival
            and festival.end_date < date.today()
            and not festival.lottery_was_done
        )
        calc_festival_chance_digits = True if festival.all_taken_stamps else False
        if festival_is_not_active_and_was_not_done and calc_festival_chance_digits:
            message = (
                FestivalMembers.objects.filter(user=user, festival=festival)
                .values("message_content")
                .first()
            )
            if message:
                message = message.get("message_content")
            if not message:
                message = f"برای شرکت در {festival.name} شما بایستی حداقل {digits.convert_to_fa(festival.min_stamp)} مهر داشته باشید."

        return render(
            request,
            "moshtari/profile.html",
            {
                "request_user": request_user,
                "user": user,
                "user_table_count": get_count_user_tables(user),
                "invited_users_did_firts_purchase": invited_users_did_firts_purchase,
                "invited_users_did_not_first_purchase": invited_users_did_not_first_purchase,
                "all_stamp_count": all_stamp_count(user, UserGiftData, DATA_KEY_LIST),
                "all_used_discount": all_is_used_discount(
                    user, UserGiftData, DATA_KEY_LIST
                ),
                "refferal_code": referral_code,
                "stamps_in_festival": each_user_stamps_in_festival(
                    festival, user, DATA_KEY_LIST
                ),
                "festival_message_content": message,
                "festival": festival,
                "form": BirthDateForm,
            },
        )

    if request.method == "POST":
        
        button = request.POST.get("button")
        if button == 'birth_date_verification':
            user.birth_date_status = True
            user.save()
            return redirect('profile', referral_code)
        
        if button == 'del_birth_date':
            user.birth_date_status = False
            user.birth_date = None
            user.save()
            return redirect('profile', referral_code)
        
        
        form = BirthDateForm(request.POST)

        if form.is_valid():
            birth_date = form.cleaned_data.get('birth_date')
            
            
            print('birth_date', birth_date)
            print('birth_date', type(birth_date))
            user.birth_date = birth_date
            if request.user.is_staff:
                user.birth_date_status = True
                user.save()
            user.save()

            return redirect("profile", referral_code)

        invited_users_did_firts_purchase, invited_users_did_not_first_purchase = (
            user_invites_and_user_customers(user, DATA_KEY_LIST)
        )

        festival = Festival.objects.last()
        if not festival:
            return render(
                request,
                "moshtari/profile.html",
                {
                    "request_user": request_user,
                    "user": user,
                    "user_table_count": get_count_user_tables(user),
                    "invited_users_did_firts_purchase": invited_users_did_firts_purchase,
                    "invited_users_did_not_first_purchase": invited_users_did_not_first_purchase,
                    "all_stamp_count": all_stamp_count(
                        user, UserGiftData, DATA_KEY_LIST
                    ),
                    "all_used_discount": all_is_used_discount(
                        user, UserGiftData, DATA_KEY_LIST
                    ),
                    "refferal_code": referral_code,
                    "stamps_in_festival": each_user_stamps_in_festival(
                        festival, user, DATA_KEY_LIST
                    ),
                    "form": BirthDateForm,
                },
            )
        festival_is_not_active_and_was_not_done = (
            festival
            and festival.end_date < date.today()
            and not festival.lottery_was_done
        )
        calc_festival_chance_digits = True if festival.all_taken_stamps else False
        if festival_is_not_active_and_was_not_done and calc_festival_chance_digits:
            message = (
                FestivalMembers.objects.filter(user=user, festival=festival)
                .values("message_content")
                .first()
            )
            if message:
                message = message.get("message_content")
            if not message:
                message = f"برای شرکت در {festival.name} شما بایستی حداقل {digits.convert_to_fa(festival.min_stamp)} مهر داشته باشید."

        return render(
            request,
            "moshtari/profile.html",
            {
                "request_user": request_user,
                "user": user,
                "user_table_count": get_count_user_tables(user),
                "invited_users_did_firts_purchase": invited_users_did_firts_purchase,
                "invited_users_did_not_first_purchase": invited_users_did_not_first_purchase,
                "all_stamp_count": all_stamp_count(user, UserGiftData, DATA_KEY_LIST),
                "all_used_discount": all_is_used_discount(
                    user, UserGiftData, DATA_KEY_LIST
                ),
                "refferal_code": referral_code,
                "stamps_in_festival": each_user_stamps_in_festival(
                    festival, user, DATA_KEY_LIST
                ),
                "festival_message_content": message,
                "festival": festival,
                "form": form,
            },
        )


@login_required(login_url="/")
def festival_users(request):

    if not Festival.objects.last():
        return render(request, "404.html")

    each_user_stamps, all_stamps = each_user_stamps_and_all_stamps_in_active_festival(
        Festival, get_user_model(), DATA_KEY_LIST
    )
    return render(
        request,
        "moshtari/festival_users.html",
        {
            "request_user": request.user,
            "each_user_stamps_in_active_festival": each_user_stamps,
            "all_stamps": all_stamps,
        },
    )


@login_required(login_url="/")
def festival_winners(request: HttpRequest):
    if request.method == "GET":
        winner_list_num = unquote(request.GET.get("winner_list"))
        winner_list_num = winner_list_num.replace("[", "").replace("]", "").split(", ")

        # print(winner_list_num)

        festival_id = request.GET.get("festival_id", "")
        festival: Festival = Festival.objects.filter(id=festival_id)

        if not festival:
            return HttpResponse(f"Festival with {festival_id} not found", status=400)

        festival = festival.first()
        # winner_list_user = [first_winner_user]
        winner_list_user = []
        winner_list_user += list(
            map(
                lambda chance_num: FestivalMembers.objects.filter(
                    festival=festival, festival_chance_number_list__contains=chance_num
                ).first(),
                winner_list_num,
            )
        )

        for i, festival_member_obj in enumerate(winner_list_user):
            festival_member_obj.win = True
            festival_member_obj.rank = i + 1
            festival_member_obj.prize = festival.winners_prizes.get(f"{i + 1}")
            festival_member_obj.save()

        # print(winner_list_user)
        festival.lottery_was_done = True
        festival.save()

        return render(
            request,
            "moshtari/festival_winners.html",
            {"festival_winners": winner_list_user, "request_user": request.user},
        )


@user_passes_test(is_staff_user, login_url="/")
@login_required(login_url="/")
def do_lottery(request):
    form = FestivalFirstWinner()
    festival = Festival.objects.last()
    if not festival:
        return HttpResponse("جشنواره ای وجود ندارد")
    festival_id = festival.id

    each_user_stamp, _ = each_user_stamps_and_all_stamps_in_active_festival(
        Festival, get_user_model(), DATA_KEY_LIST
    )
    all_participants = len(each_user_stamp)
    # participiant_stamps = sum(x[1] for x in filter(lambda x: x,  map(lambda elem: elem if elem[1] >=  festival.min_stamp else None, each_user_stamp[1:])))
    participiant_stamps = sum(
        x[1]
        for x in filter(
            lambda x: x,
            map(
                lambda elem: elem if elem[1] >= festival.min_stamp else None,
                each_user_stamp,
            ),
        )
    )
    if request.method == "GET":
        return render(
            request,
            "moshtari/do_lottery.html",
            {
                "request_user": request.user,
                "form": form,
                "participiant_stamps": participiant_stamps,
                "participiant_stamps_1": participiant_stamps - 1,
                "all_participants": all_participants,
            },
        )

    if request.method == "POST":
        winner_list_num = []
        form = FestivalFirstWinner(
            request.POST, participiant_stamps_1=participiant_stamps - 1
        )

        if form.is_valid():

            first_winner_num = form.cleaned_data.get("first_winner_number")
            winner_list_num.append(first_winner_num)
            step_number = festival.step_number
            # all_participiant_stamps = festival.all_taken_stamps - festival.number_one_stamps
            all_participiant_stamps = festival.all_taken_stamps - 1

            # we subtract 2 from festival winners for first one of list and second for lottery winner
            all_winner_num = festival.number_of_winners - 1

            winner_num = first_winner_num
            for i in range(all_winner_num):
                next_step = winner_num + step_number
                winner_num = (
                    next_step
                    if next_step < all_participiant_stamps
                    else next_step - all_participiant_stamps
                )
                winner_list_num.append(winner_num)
            festival.first_winner_number = first_winner_num
            festival.winner_link = f"https://cc.bartardigital.com/festival_winners/?winner_list={winner_list_num}&festival_id={festival_id}"
            festival.save()
            # messages.success(request, 'این جشنواره به پایان رسید و لیست برندگان مشخص شد')
            return redirect(
                f"/festival_winners/?winner_list={winner_list_num}&festival_id={festival_id}"
            )

        return render(
            request,
            "moshtari/do_lottery.html",
            {
                "form": form,
                "request_user": request.user,
                "participiant_stamps": participiant_stamps,
                "participiant_stamps_1": participiant_stamps - 1,
                "all_participants": all_participants,
            },
        )


def send_message_to_programmer(request):
    if request.method == "GET":
        pay_when = request.GET.get("when")
        try:
            full_name = request.user.first_name + " " + request.user.last_name
            message = f"{pay_when} By {full_name}"
            data = {"from": "500010609865", "to": "09904336151", "text": message}
            # response = requests.post('https://console.melipayamak.com/api/send/simple/a8b3b5300f9042b898815c3d83508d8a', json=data)
            send_text_message.delay(data, full_name)
            # if response.status_code == 200:
            request.session["message_sent"] = True
            # print(request.COOKIES)
            # print(response)

            return JsonResponse({"status": 200, "when": pay_when})
        except Exception as e:
            return JsonResponse({"status": e})


def stamp_counter_in_one_card(card_data: Dict, reason: str, card_key_list: list) -> int:
    columns_num = 0
    stamp_count = 0

    for key, va in card_data.items():
        if key.split("_")[0] not in card_key_list:

            if not columns_num:
                columns_num = sum(1 for column in va if column.startswith("column_"))

            stamp_count += sum(
                1
                for i in range(columns_num)
                if reason in va[f"column_{i + 1}"]["reason"]
            )

    return stamp_count


def make_stamp(card: Dict, stamp_reason: str, admin_name: str) -> Dict:
    updated_card = copy.deepcopy(card)
    breaker = False
    for key, value in updated_card.items():
        if type(value) == dict:

            for key_in, value_in in reversed(value.items()):
                if "column" in key_in:

                    if not value_in["stamp"]:
                        value_in["stamp"] = True
                        value_in["reason"] = stamp_reason
                        value_in["admin"] = f"{admin_name} (سیستمی)"
                        value_in["date"] = datetime.now().isoformat()

                        if table_is_full_or_not(updated_card):
                            updated_card["is_table_full"] = True

                        breaker = True
                        break

        if breaker:
            break

    return updated_card, breaker


def create_new_card_for_user(user) -> Optional[UserGiftData]:
    """
    If rais error when creating new card return None
        else return UserGiftData ojbect

    """
    try:
        last_created_card = UserTableData.objects.last()

        new_card = UserGiftData.objects.create(
            user=user,
            award_tick_table=last_created_card.award_tick_table,
            big_award=last_created_card.big_award,
        )

        return new_card
    except Exception as e:
        print(e)
        return None


def update_or_add_user(
    user_type: str,
    response_data: Dict,
    card_data: Dict,
    stamp_reason: str,
    user,
    key: str,
):
    updated = False

    for exised_user in response_data[user_type]:
        # stamps_count = stamp_counter_in_one_card(card_data, stamp_reason, DATA_KEY_LIST)
        if (
            exised_user.get("national_code", "") == user.id_card_num
            and exised_user.get("db", "") == key
        ):
            exised_user["all_automatic_stamps"] += 1
            response_data["total_stamps"] += 1
            updated = True
            break

    if not updated:
        # stamps_count = stamp_counter_in_one_card(card_data, stamp_reason, DATA_KEY_LIST)

        response_data[user_type].append(
            {
                "national_code": user.id_card_num,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "mobile": str(user.phone_number),
                "all_automatic_stamps": 1,
                "db": key,
            }
        )
        response_data["total_stamps"] += 1


def save_make_stamp(
    card,
    reason: str,
    national_code: str,
    make_stamp,
    db_stamped_user,
    new_card: bool,
    new_register: bool,
    admin_user: str,
    person_info: Dict,
):

    db_stamped_user_entry = next(
        (
            entry
            for entry in db_stamped_user
            if national_code == entry.get("national_code", None)
        ),
        None,
    )
    updated_card, is_table_full = make_stamp(card.award_tick_table, reason, admin_user)
    card.award_tick_table = updated_card
    card.save()
    if not db_stamped_user_entry:
        db_stamped_user.append(
            {**person_info, "new_register": new_register, "new_card": new_card}
        )

    return is_table_full


@transaction.atomic
def automatic_stamp(request: HttpRequest) -> JsonResponse:
    if request.method not in ["GET", "POST"]:
        return JsonResponse(
            {"error": True, "message": "Unsupported method"}, status=405
        )

    row_version_obj = OrderDetailRowVersion.objects.first()
    if request.method == "GET":
        last_row_versions: Dict = {}

        response_data = {
            "personal_key": [],
            "company_key": [],
            # 'stamped_users': [],
            # 'exised_users': [],
            # 'total_stamps': 0
        }

        row_verison_company = 0
        row_verison_person = 0

        header_body = copy.deepcopy(settings.ACCOUNTANT_BODY)

        url = settings.ACCOUNTANT_URL
        login_url = settings.ACCOUNTANT_TOKEN_URL
        personal_lgoin_data = settings.PERSONAL_ACCOUNTANT_LOGIN
        company_lgoin_data = settings.COMPANY_ACCOUNTANT_LOGIN

        personal_key = settings.PERSONAL_SECRET_KEY
        company_key = settings.COMAPANY_SECRET_KEY
        personal_compony_keys = {
            "personal_key": personal_key,
            "company_key": company_key,
        }
        order_dateils_exist = {}

        login_header = {
            "Content-Type": "application/json-patch+json",
            "Content-Length": "<calculated when request is sent>",
        }

        incomplete_users: List[Dict] = []

        if row_version_obj:
            row_verison_person = row_version_obj.row_version_person
            row_verison_company = row_version_obj.row_version_company

        for key, value in personal_compony_keys.items():
            headers = {
                "Content-Type": "application/json-patch+json",
            }

            if key == "personal_key":
                header_body["fromOrderDetailVersion"] = row_verison_person
                auth_token_value_res = retry_request(
                    "https://mahakacc.mahaksoft.com/API/v3/Sync/Login",
                    headers=login_header,
                    method="post",
                    data=json.dumps(personal_lgoin_data),
                )

                auth_token_value_obj = (
                    auth_token_value_res.json() if auth_token_value_res else {}
                )
                # print(auth_token_value_obj)
                if auth_token_value_obj.get("Result"):
                    headers["Authorization"] = "Bearer " + auth_token_value_obj.get(
                        "Data", {}
                    ).get("UserToken", "")

                else:
                    return JsonResponse(
                        {
                            "message": "مشکل در لاگین کردن به دیتابیس شخصی (به احتمال زیاد مشکل از مهک هست بعد از چند دقیقه دوباره تلاش کنید)",
                            "error": True,
                        },
                        status=200,
                    )

            if key == "company_key":
                header_body["fromOrderDetailVersion"] = row_verison_company
                auth_token_value_obj = retry_request(
                    "https://mahakacc.mahaksoft.com/API/v3/Sync/Login",
                    headers=login_header,
                    method="post",
                    data=json.dumps(company_lgoin_data),
                ).json()

                if auth_token_value_obj.get("Result", ""):
                    headers["Authorization"] = "Bearer " + auth_token_value_obj.get(
                        "Data", {}
                    ).get("UserToken", "")

                else:
                    return JsonResponse(
                        {
                            "message": "مشکل در لاگین کردن به دیتابیس شرکت (به احتمال زیاد مشکل از مهک هست بعد از چند دقیقه دوباره تلاش کنید)",
                            "error": True,
                        },
                        status=200,
                    )

            header_body_json = json.dumps(header_body)

            # print(headers)

            response = retry_request(
                url=url, method="post", headers=headers, data=header_body_json
            )
            response_dict = response.json()
            # print('resss', response.status_code)
            # print('resss', response_dict.get("message", ))

            if (
                response.status_code == 401
                and response_dict.get("message", "") == "Unauthorized"
            ):
                return JsonResponse(
                    {"message": "مشکلی در لاگین", "error": True}, status=200
                )

            if not response_dict.get("Result"):
                return JsonResponse(
                    {"message": "عدم گرفتن درست اطلاعات", "error": True}, status=200
                )

            order_details = response_dict.get("Data").get("Objects").get("OrderDetails")
            orders = response_dict.get("Data", {}).get("Objects", {}).get("Orders", [])
            people = response_dict.get("Data", {}).get("Objects", {}).get("People", [])
            product_details = (
                response_dict.get("Data", {})
                .get("Objects", {})
                .get("ProductDetails", [])
            )
            products = (
                response_dict.get("Data", {}).get("Objects", {}).get("Products", [])
            )

            # print("len(order)", len(order_details))

            if not order_details:
                order_dateils_exist[key] = "سفارش جدیدی وجود ندارد"
                continue

            for order_detail in order_details:

                order_price = order_detail.get("Price", 0)
                order_id = order_detail.get("OrderId")
                income_id = order_detail.get("IncomeId", 0)
                order_detail_count = int(order_detail.get("Count1", 0))
                product_detail_id = order_detail.get("ProductDetailId", 0)
                order_detail_created_date = order_detail.get("CreateDate", "")
                order_detail_row_version = order_detail.get("RowVersion", "")

                minimum_price = 500_000 if key == "personal_key" else 5_000_000

                # order = list(filter(lambda o: o.get('OrderId') == order_id, orders))[0]
                # person = list(filter(lambda p: p.get('PersonId') == order.get('PersonId'), people))[0]
                # ‌ I get order that related to this order_detail
                order = next((o for o in orders if o.get("OrderId") == order_id), None)
                product_id, product_price = next(
                    (
                        (
                            product_detail.get("ProductId", 0),
                            product_detail.get("Price1", 0),
                        )
                        for product_detail in product_details
                        if product_detail.get("ProductDetailId", "")
                        == product_detail_id
                    ),
                    (0, 0),  # Default tuple if no match is found
                )

                # print(product_id, product_price, 'fsdafsdfsfsdsda')

                # product_name = next ((p.get('Name', '') for p in products if p.get('ProductId') == product_id and product_price >= minimum_price), None)
                product_name = next(
                    (
                        p.get("Name", "")
                        for p in products
                        if p.get("ProductId") == product_id
                    ),
                    None,
                )

                if not order:
                    continue

                # I get person that related to given order (Not order_detail)
                person = next(
                    (p for p in people if p.get("PersonId") == order.get("PersonId")),
                    None,
                )

                if not person:
                    continue

                person_national_id = person.get("NationalCode", "")
                person_phone_number = person.get("Mobile", "")
                person_first_name: str = (
                    person["FirstName"].replace("ك", "ک").replace("ي", "ی")
                    if person and person.get("FirstName") is not None
                    else "نام وجود ندارد"
                )

                person_last_name = (
                    person["LastName"].replace("ك", "ک").replace("ي", "ی")
                    if person and person.get("FirstName") is not None
                    else "نام خانوادگی وجود ندارد"
                )
                person_code = person.get("PersonCode", 0)

                minimum_price = 500_000 if key == "personal_key" else 5_000_000
                order_price = (
                    order_price + ((order_price * 10) / 100)
                    if key != "personal_key"
                    else order_price
                )

                same_phone_user = (
                    get_user_model()
                    .objects.filter(phone_number=person_phone_number)
                    .first()
                )

                # If user don't have national code or mobile continiue
                if (
                    not person_national_id
                    or not person_phone_number
                    or (
                        same_phone_user
                        and person_national_id != same_phone_user.id_card_num
                    )
                ):
                    incomplete_user = next(
                        (
                            user
                            for user in incomplete_users
                            if (
                                user.get("person_code") == person_code
                                and user.get("first_name") == person_first_name
                                and user.get("last_name") == person_last_name
                                and user.get("mobile") == person_phone_number
                                and user.get("national_code") == person_national_id
                                and user.get("db") == key
                            )
                        ),
                        None,
                    )
                    if incomplete_user:
                        continue
                    incomplete_users.append(
                        {
                            "person_code": person_code,
                            "first_name": person_first_name,
                            "last_name": person_last_name,
                            "national_code": person_national_id,
                            "mobile": person_phone_number,
                            "db": key,
                            "repeated_phone_number": (
                                f"{same_phone_user.first_name} {same_phone_user.last_name}"
                                if same_phone_user
                                else ""
                            ),
                        }
                    )
                    continue

                phone_number_pattern = r"^\d{11}$"
                if not re.match(phone_number_pattern, person_phone_number.strip()):
                    incomplete_user = next(
                        (
                            user
                            for user in incomplete_users
                            if user.get("national_code") == person_national_id
                        ),
                        None,
                    )
                    if incomplete_user:
                        continue
                    else:
                        print(person_phone_number)
                        incomplete_users.append(
                            {
                                "first_name": person_first_name,
                                "last_name": person_last_name,
                                "national_code": person_national_id,
                                "mobile": person_phone_number,
                                "db": key,
                                "repeated_phone_number": "شماره اشتباه",
                            }
                        )
                        continue

                person_entry = next(
                    (
                        entry
                        for entry in response_data[key]
                        if person_national_id == entry.get("national_code", "")
                    ),
                    None,
                )
                agsat_id = 9933 if key == "personal_key" else 9430

                if person_entry:
                    person_entry["stamps_count"] += (
                        int(order_detail_count)
                        if order_price >= minimum_price and income_id != agsat_id
                        else 0
                    )
                    person_entry["orders_info"].append(
                        {
                            "created_date": order_detail_created_date,
                            "row_version": order_detail_row_version,
                        }
                    )
                    person_entry["products"].append(product_name)
                else:
                    response_data[key].append(
                        {
                            "first_name": person_first_name,
                            "last_name": person_last_name,
                            "person_code": person_code,
                            "phone_number": person_phone_number,
                            "stamps_count": (
                                int(order_detail_count)
                                if order_price >= minimum_price
                                and income_id != agsat_id
                                else 0
                            ),
                            "take_photo_stamp": 0,
                            "national_code": person_national_id,
                            "orders_info": [
                                {
                                    "created_date": order_detail_created_date,
                                    "row_version": order_detail_row_version,
                                }
                            ],
                            "products": [product_name],
                        }
                    )

                # Save row_version
            last_row_version = order_details[-1].get("RowVersion")
            last_row_versions[key] = last_row_version

        # print('response_data', response_data)

        return JsonResponse(
            {
                "error": False,
                "data": {
                    "response_data": response_data,
                    "no_order": order_dateils_exist,
                    "incomplete_users": incomplete_users,
                    "last_row_versions": last_row_versions,
                },
            },
            status=200,
        )

    if request.method == "POST":
        error_message_rais = ""
        raising_error = False
        data = json.loads(request.body)
        User = get_user_model()
        admin_user = data.get("admin_user", "")
        db_stamped_user = []
        last_detail_versions = data.get("last_detail_versions", "")
        # print('last_row_versions', last_detail_versions)
        try:
            with transaction.atomic():  # Ensures all operations are atomi
                for accounant, persons in data.items():
                    if accounant not in ["personal_key", "company_key"]:
                        continue

                    if persons == -1:
                        continue
                    for person_info in persons:
                        try:
                            first_name = person_info.get("first_name", "N/A")
                            last_name = person_info.get("last_name", "N/A")
                            national_code = person_info.get("national_code", "N/A")
                            person_code = person_info.get("person_code", "N/A")
                            stamps_count = int(person_info.get("stamps_count", 0))
                            take_photo_stamp = person_info.get("take_photo_stamp", 0)
                            phone_number = person_info.get("phone_number", "")
                            # print(national_code, first_name)
                            user = (
                                User.objects.prefetch_related("cards")
                                .filter(id_card_num=national_code)
                                .first()
                            )

                            if user:

                                make_new_card = False

                                if take_photo_stamp:
                                    last_card_obj = user.cards.last()
                                    last_card_data = last_card_obj.award_tick_table
                                    # If user card is full
                                    if last_card_data.get("is_table_full", ""):
                                        make_new_card = True
                                        new_card = create_new_card_for_user(user)
                                        save_make_stamp(
                                            card=new_card,
                                            reason="عکس از محصول",
                                            national_code=national_code,
                                            make_stamp=make_stamp,
                                            db_stamped_user=db_stamped_user,
                                            new_card=make_new_card,
                                            new_register=False,
                                            admin_user=admin_user,
                                            person_info=person_info,
                                        )
                                    else:
                                        # If user card not full
                                        save_make_stamp(
                                            card=last_card_obj,
                                            reason="عکس از محصول",
                                            national_code=national_code,
                                            make_stamp=make_stamp,
                                            db_stamped_user=db_stamped_user,
                                            new_card=make_new_card,
                                            new_register=False,
                                            admin_user=admin_user,
                                            person_info=person_info,
                                        )

                                for _ in range(int(stamps_count)):
                                    last_card_obj = user.cards.last()
                                    last_card_data = last_card_obj.award_tick_table
                                    # If user card is full
                                    if last_card_data.get("is_table_full", ""):
                                        make_new_card = True
                                        new_card = create_new_card_for_user(user)
                                        save_make_stamp(
                                            card=new_card,
                                            reason="خرید محصول",
                                            national_code=national_code,
                                            make_stamp=make_stamp,
                                            db_stamped_user=db_stamped_user,
                                            new_card=make_new_card,
                                            new_register=False,
                                            admin_user=admin_user,
                                            person_info=person_info,
                                        )
                                    else:
                                        # If user card not full
                                        save_make_stamp(
                                            card=last_card_obj,
                                            reason="خرید محصول",
                                            national_code=national_code,
                                            make_stamp=make_stamp,
                                            db_stamped_user=db_stamped_user,
                                            new_card=make_new_card,
                                            new_register=False,
                                            admin_user=admin_user,
                                            person_info=person_info,
                                        )

                            else:  # If user doesn't exist

                                new_user = User.objects.create_user(
                                    username=phone_number,
                                    id_card_num=national_code,
                                    password=national_code,
                                    first_name=first_name,
                                    last_name=last_name,
                                    phone_number=phone_number,
                                    is_verified=True,
                                )
                                new_card_first = create_new_card_for_user(new_user)
                                new_card_first_card = new_card_first.award_tick_table

                                if take_photo_stamp:
                                    # If user card is full
                                    if new_card_first_card.get("is_table_full", ""):
                                        new_card = create_new_card_for_user(new_user)
                                        save_make_stamp(
                                            card=new_card,
                                            reason="عکس از محصول",
                                            national_code=national_code,
                                            make_stamp=make_stamp,
                                            db_stamped_user=db_stamped_user,
                                            new_card=True,
                                            new_register=True,
                                            admin_user=admin_user,
                                            person_info=person_info,
                                        )
                                    else:
                                        # If user card not full
                                        save_make_stamp(
                                            card=new_card_first,
                                            reason="عکس از محصول",
                                            national_code=national_code,
                                            make_stamp=make_stamp,
                                            db_stamped_user=db_stamped_user,
                                            new_card=True,
                                            new_register=True,
                                            admin_user=admin_user,
                                            person_info=person_info,
                                        )

                                for _ in range(int(stamps_count)):
                                    # If user card is full
                                    if new_card_first_card.get("is_table_full", ""):
                                        new_card = create_new_card_for_user(new_user)
                                        save_make_stamp(
                                            card=new_card,
                                            reason="خرید محصول",
                                            national_code=national_code,
                                            make_stamp=make_stamp,
                                            db_stamped_user=db_stamped_user,
                                            new_card=True,
                                            new_register=True,
                                            admin_user=admin_user,
                                            person_info=person_info,
                                        )
                                    else:
                                        # If user card not full
                                        save_make_stamp(
                                            card=new_card_first,
                                            reason="خرید محصول",
                                            national_code=national_code,
                                            make_stamp=make_stamp,
                                            db_stamped_user=db_stamped_user,
                                            new_card=True,
                                            new_register=True,
                                            admin_user=admin_user,
                                            person_info=person_info,
                                        )

                                if not take_photo_stamp and not int(stamps_count):
                                    db_stamped_user.append(
                                        {
                                            **person_info,
                                            "new_register": True,
                                            "new_card": True,
                                        }
                                    )

                                # Send registery message
                                full_name = f"{first_name} {last_name}"
                                message_text = f"""
                                        {full_name} عزیز؛
    😍🤩
                            
    کارت وفاداری برتر دیجیتال برای شما صادر شد.
    برای اطلاع از نحوه دریافت تخفیف در خریدهای بعدی خود، حتما ویدئوی زیر را ببینید:
                                                https://bartardigital.com/loyalty-card-guide/
                                                
    با تشکر."""
                                message_data = {
                                    "from": "500010609865",
                                    "to": str(phone_number),
                                    "text": message_text,
                                }
                                send_text_message.delay(message_data, full_name)

                        except Exception as e:
                            # Log the error and raise an exception to trigger rollback
                            m = f"Error processing person_info: {person_info}, error: {traceback.format_exc()}"
                            raising_error = True
                            error_message_rais = m
                            raise IntegrityError(f"m")

                    # print(last_detail_versions)
                    if row_version_obj:
                        for key, value in last_detail_versions.items():
                            print("value", value)
                            if key == "personal_key":
                                setattr(row_version_obj, "row_version_person", value)
                            else:
                                setattr(row_version_obj, "row_version_company", value)
                        row_version_obj.save()
                    else:
                        OrderDetailRowVersion.objects.create(
                            row_version_person=int(
                                last_detail_versions.get("personal_key", 0)
                            ),
                            row_version_company=int(
                                last_detail_versions.get("company_key", 0)
                            ),
                        )

        except ValidationError as e:
            return JsonResponse({"error": True, "message": str(e)}, status=400)
        except IntegrityError:
            print(error_message_rais)
            return JsonResponse(
                {"error": True, "message": error_message_rais}, status=500
            )
        except Exception as e:
            # Log the error and return a generic message
            print("Unexpected error:", str(e))
            return JsonResponse(
                {"error": True, "message": "An unexpected error occurred."}, status=500
            )

        return JsonResponse({"success": "true", "data": db_stamped_user}, status=200)


@user_passes_test(is_staff_user, login_url="/")
@login_required(login_url="/")
def sms_logs(request):
    if request.method != "GET":
        return HttpResponse(f"Not allowd ", status=403)

    sms_logs = SMSLog.objects.all().order_by("-created_at")[:500]

    return render(
        request,
        "moshtari/sms_logs.html",
        {"sms_logs": list(sms_logs), "request_user": request.user},
    )
