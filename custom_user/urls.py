from django.urls import path
from . import views


urlpatterns = [
    path('user_info/', views.user_info, name='user_info'),
    path('overall_login/', views.overall_login, name="overall_login"),
    path('overall_regist/', views.overall_regist, name="overall_regist"),
    path('login/',views.login, name='login'),
    path('regist/', views.regist, name='regist'),
    path('confirm/', views.confirm, name='confirm'),
    path('logout/', views.logout, name='logout'),
    path('get_check_code/', views.get_check_code, name='get_check_code'),
    path('reset_pwd/', views.reset_pwd, name='reset_pwd'),
    path('change_pwd/', views.change_pwd, name='change_pwd')
]