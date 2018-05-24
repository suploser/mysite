from django.contrib import admin
from .models import User, ConfirmString, UserProfile
# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'nickname', 'password', 'email','has_confirmed', 'is_supuser')
    # 获取外键的字段值
    # def username(self, obj):
    #     return '123'
    def nickname(self, obj):
        return obj.userprofile.nickname

@admin.register(ConfirmString)
class ConfirmStringAdmin(admin.ModelAdmin):
    list_display = ('user', 'reg_time', 'token')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname')


