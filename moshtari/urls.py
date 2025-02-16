from django.urls import path
from . import views




urlpatterns = [
    # path('', views.home, name='home'),
    path('last_user_table/<int:id_card_num>/', views.last_user_table, name='last_user_table'),
    path('user_list/', views.user_list, name="user_list"),
    path('ajax_search', views.ajax_search, name='ajax_search'),
    path('table_view/<str:id_card_num>/<int:table_id>/', views.table_view, name='table_view'),
    path('setting_table/', views.setting_table, name='setting_table'),
    path('last_table/', views.last_table, name='last_table'),
    path('all_user_tables/<int:id_card_num>/', views.all_user_tables, name='all_user_tables'),
    path('user_invites/<int:id_card_num>/', views.user_invites, name='user_invites'),
    path('profile/<str:referral_code>/', views.porfile, name='profile'),
    path('festival_users/', views.festival_users, name='festival_users'),
    path('festival_winners/', views.festival_winners, name='festival_winners'),
    path('do_lottery/', views.do_lottery, name='do_lottery'),
    path('auto_stamp/', views.automatic_stamp, name='auto_stamp'),
    path('sms_logs/', views.sms_logs, name='sms_logs'),
    path('send_message_to_programmer/', views.send_message_to_programmer, name='send_message_to_programmer'),


]

