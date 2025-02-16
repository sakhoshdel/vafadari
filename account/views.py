from datetime import timedelta
from urllib.parse import unquote

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse

# from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from persian_tools import digits
from phonenumber_field.phonenumber import PhoneNumber
from unidecode import unidecode

from moshtari.models import UserGiftData, UserTableData

# import random
from moshtari.tasks import send_text_message

from .forms import ChangePasswordForm, ChangePhoneForm, LoginForm, UserRegistrationForm
from .models import User, VerificationCode

TIME_EXPIRETION = 120


def custom_404(request, exception):
    return render(
        request,
        "404.html",
        {"exception": exception, "request_user": request.user},
        status=404,
    )


def register(request):
    param = ""
    parent_user = ""
    referral_code = request.GET.get("ref")
    if referral_code:
        referral_code = unquote(referral_code)
    if request.method == "POST":
        # get ref code
        # print(request.GET.get('ref'))
        id_card_num = request.POST.get("id_card_num")
        # print('id_card_num', id_card_num)

        post_data = request.POST.copy()
        phone_number = request.POST.get("phone_number")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        en_id_card_numb = digits.convert_to_en(id_card_num)
        post_data["password1"] = en_id_card_numb
        post_data["password2"] = en_id_card_numb
        post_data["username"] = unidecode("{}".format(phone_number))
        post_data["first_name"] = _(first_name)
        post_data["last_name"] = _(last_name)
        # print('#' * 100)
        # print(post_data.get('send_otp'))
        # print(post_data)
        # print('4' * 100)
        send_code_flag = post_data.get("send_otp")
        form = UserRegistrationForm(post_data)

        if form.is_valid():
            # print('* ' * 60)
            user: User = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            # add parent_user to user
            parent_user = User.objects.filter(referral_code=referral_code).first()
            # print(parent_user.first_name)
            if parent_user:
                user.parent_user = parent_user

            birth_date = form.cleaned_data.get("birth_date")
            # Verify birthdate if registered by staff user
            if birth_date and request.user.is_staff:
                user.birth_date_status = True
                user.save()

            form.save()
            # get latest UserTableData
            latest_user_table_query = UserTableData.objects.order_by("-created_at")
            if latest_user_table_query.exists():
                user_tabel_data = latest_user_table_query.first()

                # create a specific table data for user
                user_award_data = UserGiftData(
                    award_tick_table=user_tabel_data.award_tick_table,
                    big_award=user_tabel_data.big_award,
                    user=user,
                )
                user_award_data.save()

                full_name = first_name + " " + last_name
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

                if send_code_flag and request.user.is_staff:
                    return redirect(f"/verify/?phn={phone_number}")
                if not request.user.is_staff:
                    return redirect(f"/verify/?phn={phone_number}")

                user.is_verified = True
                user.save()

            return redirect(f"/table_view/{user.id_card_num}/{user_award_data.id}/")

    else:
        if referral_code:
            parent_user = User.objects.filter(
                referral_code=unquote(referral_code)
            ).first()

        form = UserRegistrationForm()
        param = request.GET.get("ref")
        # print(param)
    return render(
        request,
        "account/register.html",
        {
            "request_user": request.user,
            "form": form,
            "param": param,
            "parent_user": parent_user,
        },
    )


def verify(request):
    phone_number = ""
    if request.method == "GET":
        user = ""
        if phone_number is not None:
            phone_number = request.GET.get("phn")
            change_phone = request.GET.get("change_phone")

            phone_number_unpluse = phone_number
        # print(phone_number)

        if phone_number:
            phone_number = phone_number.replace(" 98", "0")
            user = User.objects.filter(phone_number=phone_number).first()

            last_user_table_id = 0
            last_user_table = UserGiftData.objects.filter(user=user).last()
            if last_user_table:
                last_user_table_id = last_user_table.id

            # print(user.id_card_num)
            # data = {'to': phone_number}

            return render(
                request,
                "account/verify.html",
                context={
                    "user": user,
                    "request_user": request.user,
                    "phone_number": phone_number,
                    "phone_number_unpluse": phone_number_unpluse,
                    "last_user_table_id": last_user_table_id,
                    "TIME_EXPIRETION": TIME_EXPIRETION,
                },
            )

        if change_phone:
            referral_code = unquote(request.GET.get("referral_code"))

            user = User.objects.filter(referral_code=referral_code).first()
            return render(
                request,
                "account/verify.html",
                context={
                    "user": user,
                    "request_user": request.user,
                    "change_phone": change_phone,
                    "referral_code": referral_code,
                    "TIME_EXPIRETION": TIME_EXPIRETION,
                },
            )

        return render(
            request,
            "account/verify.html",
            context={
                "phone_number": phone_number,
                "request_user": request.user,
                "phone_number_unpluse": phone_number_unpluse,
                "TIME_EXPIRETION": TIME_EXPIRETION,
            },
        )


# use ajax to send verify code to user phone number
def send_code(request):
    phone_number = ""
    if request.method == "GET":

        # phone_number = request.GET.get('phn').replace(' ', '+')
        phone_number = request.GET.get("phn")
        referral_code = unquote(request.GET.get("referral_code"))
        change_phone = request.GET.get("change_phone")
        # print(phone_number)
        user = User.objects.filter(phone_number=phone_number).first()
        user_change_phone = User.objects.filter(
            referral_code=unquote(referral_code)
        ).first()
        # print('user_change_phone', user_change_phone)
        if user:
            # print("cache.get(f'verification_code_{phone_number}')", cache.get(f'verification_code_{phone_number}'))
            stored_code = VerificationCode.objects.filter(
                phone_number=phone_number
            ).last()
            s_code = True
            if stored_code:
                s_code = stored_code.is_expired()

            if s_code:
                data = {"to": phone_number}
                response = requests.post(
                    "https://console.melipayamak.com/api/send/otp/a8b3b5300f9042b898815c3d83508d8a",
                    json=data,
                )
                rs = response.json()
                # rs = {'code': ''.join([str(random.randint(0, 9)) for _ in range(6)]), 'status': 'ارسال موفق بود'}
                # print(rs)
                if rs.get("status") == "ارسال موفق بود":
                    code = rs.get("code")
                    # print('8' * 50)
                    # print('code: ' , code)
                    # expiration_time = timezone.now() + datetime.timedelta(seconds=TIME_EXPIRETION)

                    # cache.set(f'verification_code_{phone_number}', code, TIME_EXPIRETION)
                    verification_code = VerificationCode.objects.create(
                        phone_number=phone_number,
                        code=code,
                        expiration_time=timezone.now()
                        + timedelta(seconds=TIME_EXPIRETION),
                    )
                    if verification_code:
                        return JsonResponse(
                            {"message": "Verification code sent successfully"}
                        )
                    else:
                        return JsonResponse(
                            {"message": "Verification code dont be save successfully"}
                        )
                else:
                    # Handle the case where the OTP request was not successful
                    return JsonResponse({"error": "Failed to send verification code"})
            else:

                return JsonResponse(
                    {"error": f"Code sent try after {TIME_EXPIRETION} seconds"}
                )

        elif user_change_phone:
            stored_code = VerificationCode.objects.filter(
                phone_number=change_phone
            ).last()
            s_code = True
            if stored_code:
                s_code = stored_code.is_expired()

            if s_code:
                data = {"to": change_phone}
                response = requests.post(
                    "https://console.melipayamak.com/api/send/otp/a8b3b5300f9042b898815c3d83508d8a",
                    json=data,
                )
                rs = response.json()
                # rs = {'code': ''.join([str(random.randint(0, 9)) for _ in range(6)]), 'status': 'ارسال موفق بود'}
                # print(rs)
                if rs.get("status") == "ارسال موفق بود":
                    code = rs.get("code")
                    # print('8' * 50)
                    # print('code: ' , code)
                    # expiration_time = timezone.now() + datetime.timedelta(seconds=TIME_EXPIRETION)

                    # cache.set(f'verification_code_{phone_number}', code, TIME_EXPIRETION)
                    verification_code = VerificationCode.objects.create(
                        phone_number=change_phone,
                        code=code,
                        expiration_time=timezone.now()
                        + timedelta(seconds=TIME_EXPIRETION),
                    )
                    if verification_code:
                        return JsonResponse(
                            {"message": "Verification code sent successfully"}
                        )
                    else:
                        return JsonResponse(
                            {"message": "Verification code dont be save successfully"}
                        )
                else:
                    # Handle the case where the OTP request was not successful
                    return JsonResponse({"error": "Failed to send verification code"})
            else:

                return JsonResponse(
                    {"error": f"Code sent try after {TIME_EXPIRETION} seconds"}
                )

        else:
            return JsonResponse({"error": "This number does not register"})

    else:
        return JsonResponse({"error": "Invalid request method"})


# use ajax to get verify code from client and confirm it
def verify_code(request):
    phone_num = ""
    change_phone = ""
    if request.method == "GET":
        verification_code = request.GET.get("code")
        referral_code = unquote(request.GET.get("referral_code"))
        change_phone = request.GET.get("change_phone")
        # print('change_phone', change_phone)

        phone_num = request.GET.get("phone_number")
        if phone_num:
            # First, try to verify against the stored code in the cache
            # stored_code = cache.get(f'verification_code_{phone_num}')
            stored_code = VerificationCode.objects.filter(phone_number=phone_num).last()
            # print(stored_code)
            if stored_code:
                ver_code = stored_code.code
            if stored_code and verification_code == ver_code:
                if not stored_code.is_expired():
                    user = User.objects.filter(phone_number=phone_num).first()
                    if user:
                        user.is_verified = True
                        user.save()
                        # print(request.user.is_superuser )
                        if not request.user.is_staff:
                            login(request, user)

                        if user.parent_user:
                            message = f"کاربر معرفی شده شما آقای/خانم {user.first_name} {user.last_name} ثبت نام خود را در باشگاه وفاداری برتر دیجیتال تکمیل نمود. \n لطفا دوست خود را تا اولین خرید ترغیب نمایید. \n cc.bartardigital.com "
                            data = {
                                "from": "500010609865",
                                "to": str(user.parent_user.phone_number),
                                "text": message,
                            }
                            response = requests.post(
                                "https://console.melipayamak.com/api/send/simple/a8b3b5300f9042b898815c3d83508d8a",
                                json=data,
                            )
                            # print(response.status_code)
                            # print(response)

                        return JsonResponse(
                            {
                                "success": True,
                            }
                        )
                    else:
                        # print('success', False , 'No user with this phone number', verification_code, stored_code),
                        return JsonResponse(
                            {
                                "success": False,
                                "message": "No user with this phone number",
                            }
                        )
        elif change_phone:
            stored_code = VerificationCode.objects.filter(
                phone_number=change_phone
            ).last()
            # print(stored_code)
            if stored_code:
                ver_code = stored_code.code
            if stored_code and verification_code == ver_code:
                if not stored_code.is_expired():
                    user = User.objects.filter(referral_code=referral_code).first()
                    if user:
                        if User.objects.filter(phone_number=change_phone).exists():
                            return JsonResponse(
                                {
                                    "success": False,
                                    "message": _(
                                        "با این شماره قبلا ثبت نام شده نمیتوانید به این شماره تغییر بدید."
                                    ),
                                }
                            )
                        user.is_verified = True
                        user.phone_number = change_phone
                        user.save()
                        # print(request.user.is_superuser )
                        return JsonResponse(
                            {
                                "success": True,
                            }
                        )
                    else:
                        # print('success', False , 'No user with this phone number', verification_code, stored_code),
                        return JsonResponse(
                            {
                                "success": False,
                                "message": "No user with this phone number",
                            }
                        )

        else:
            # Verification failed
            # print('success', False, 'Incorrect verification code' , verification_code, stored_code)
            return JsonResponse(
                {"success": False, "message": "Incorrect verification code"}
            )

    # Handle other HTTP methods
    # print('success', False,'Invalid request method', verification_code, stored_code)
    return JsonResponse({"success": False, "message": "Invalid request method"})


def sign_in(request):
    if request.method == "GET":
        form = LoginForm()

        if request.user.is_staff:
            return redirect("/user_list/")

        if request.user.is_authenticated and not request.user.is_staff:
            return redirect(f"/last_user_table/{request.user.id_card_num}")
        return render(
            request, "account/login.html", {"request_user": request.user, "form": form}
        )

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = digits.convert_to_en(form.cleaned_data["username"])
            password = digits.convert_to_en(form.cleaned_data["password"])
            # print(username, password)
            user = authenticate(request, username=username, password=password)
            if user:
                if not user.is_verified and not user.is_superuser and not user.is_staff:
                    messages.error(request, _("شماره شما تایید نشده است"))
                    link = f"/verify?phn={user.phone_number}"
                    return render(
                        request,
                        "account/login.html",
                        {
                            "request_user": request.user,
                            "form": form,
                            "verify_link": link,
                        },
                    )
                elif user.is_superuser or user.is_staff:
                    login(request, user)
                    return redirect("/user_list/")
                else:
                    login(request, user)
                    return redirect(f"/last_user_table/{user.id_card_num}/")

        messages.error(request, _(f"رمز یا کدملی شما اشتباه است"))
        return render(
            request, "account/login.html", {"request_user": request.user, "form": form}
        )


def logout_view(request):
    logout(request)
    return redirect("/")


@login_required(login_url="/")
def change_pass(request, referral_code):
    request_user = request.user
    user = User.objects.filter(referral_code=unquote(referral_code)).first()
    if not user:
        return HttpResponse("یوزری وجود ندارد")
    if request.method == "GET":
        return render(
            request,
            "account/change_password.html",
            {"request_user": request_user, "form": ChangePasswordForm(), "user": user},
        )
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_pass = digits.convert_to_en(form.cleaned_data.get("old_pass"))
            new_pass = digits.convert_to_en(form.cleaned_data.get("new_pass"))
            if not user.check_password(old_pass):
                messages.warning(request, _("رمز قبلی  صحیح نیست."))
                return render(
                    request,
                    "account/change_password.html",
                    {"request_user": request_user, "form": form, "user": user},
                )

            user.set_password(new_pass)
            user.save()
            messages.success(request, _("رمز با موفقیت تغییر یافت"))
            if request_user.is_staff:
                login(request, request_user)

        return redirect("/")


@login_required(login_url="/")
def reset_password(request):
    referral_code = ""
    if request.method == "GET":
        referral_code = unquote(request.GET.get("referral_code"))
        # print('referral_code fetch', referral_code)
        user = User.objects.filter(referral_code=referral_code).first()
        if not user:
            return JsonResponse(
                {
                    "user_not_found": f"user not found with this referral code {referral_code}"
                }
            )
        user.set_password(user.id_card_num)
        user.save()

        message = f"کاربر گرامی رمز شما به درخواست خودتان به حالت اولیه (کدملی) بازگشت \n برتر دیجیتال \n cc.bartardigital.com"
        data_message = {
            "from": "500010609865",
            "to": str(user.phone_number),
            "text": message,
        }
        response = requests.post(
            "https://console.melipayamak.com/api/send/simple/a8b3b5300f9042b898815c3d83508d8a",
            json=data_message,
        )
        rs = response.json()
        sms_status = response.status_code
        # rs = {'code': ''.join([str(random.randint(0, 9)) for _ in range(6)]), 'status': 'ارسال موفق بود'}
        # print(rs)
        sms_status = 200
        if sms_status == 200:
            return JsonResponse(
                {
                    "sms_status": sms_status,
                    "sms_response_msg": rs.get("status"),
                    "full_name": f"{user.first_name} {user.last_name}",
                }
            )
        return JsonResponse(
            {
                "sms_status": sms_status,
                "sms_response_msg": rs.get("status"),
                "full_name": f"{user.first_name} {user.last_name}",
            }
        )


@login_required(login_url="/")
def change_phone(request, referral_code):
    request_user = request.user
    user = User.objects.filter(referral_code=unquote(referral_code)).first()

    if not user:
        return HttpResponse("یوزری وجود ندارد")
    if request.method == "GET":
        return render(
            request,
            "account/change_phone.html",
            {"request_user": request_user, "user": user, "form": ChangePhoneForm()},
        )

    if request.method == "POST":
        form = ChangePhoneForm(request.POST)

        if form.is_valid():
            password = digits.convert_to_en(form.cleaned_data.get("password"))
            new_phone = PhoneNumber.from_string(
                region="IR", phone_number=str(form.cleaned_data.get("new_phone"))
            ).as_national.replace(" ", "")

            if not user.check_password(password):
                messages.warning(request, _("رمز شما صحیح نمی باشد"))
                return render(
                    request,
                    "account/change_phone.html",
                    {"request_user": request_user, "user": user, "form": form},
                )

            return redirect(
                f"/verify/?change_phone={new_phone}&referral_code={unquote(referral_code)}"
            )

        return render(
            request,
            "account/change_phone.html",
            {"request_user": request_user, "user": user, "form": form},
        )
