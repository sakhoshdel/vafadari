from django.contrib import admin
from django.contrib.admin import AdminSite
from django.http.request import HttpRequest
from django.utils.translation import gettext as _
from jalali_date.admin import ModelAdminJalaliMixin

from moshtari.models import *
admin.site.site_header = "مدیریت دیتابیس مشتری وفادار"
admin.site.site_title = " مدیریت دیتابیس "
admin.site.index_title = "به مدیریت دیتابیس خوش آمدید"


# class FestivalAdmin(admin.ModelAdmin):
#     # fields = ['excel_file']
    
#     # def has_change_permission(self, request, obj=None) -> bool:
#     #     if obj is not None and obj.lottery_was_done:
#     #         return False
#     #     return super().has_change_permission(request, obj=obj)
    
#     # def has_delete_permission(self, request, obj= None) -> bool:
#     #     if obj is not None and obj.lottery_was_done:
#     #         return False
#     #     return super().has_change_permission(request, obj=obj)
#     pass


admin.site.register(UserGiftData)
admin.site.register(OrderDetailRowVersion)
admin.site.register(UserTableData)
admin.site.register(stamp_reasons)
# admin.site.register(Festival, FestivalAdmin)
admin.site.register(FestivalMembers)
admin.site.register(SMSLog)

@admin.register(Festival)
class FestivalAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    # list_display = '__all__'
    pass

