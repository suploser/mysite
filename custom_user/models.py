from django.db import models
from django.conf import settings
import os, shutil
# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=60)
    email = models.EmailField()
    password = models.CharField(max_length=60)
    is_supuser = models.BooleanField(default=False)
    has_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class ConfirmString(models.Model):
    token = models.CharField(max_length=250)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reg_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username+','+self.token

    class Meta:
        ordering=['-reg_time']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=20, default='')

    def __str__(self):
        return self.nickname

AVATAR_ROOT = 'avatar'
AVATAR_DEFAULT = os.path.join('/media',AVATAR_ROOT, 'default_64.png')
class UserAvatar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=AVATAR_ROOT)

def get_avatar_url(self):
    try:
        avatar = UserAvatar.objects.get(user=self)
        return avatar.avatar.url
    except Exception as e:
        # print(str(e))
        return AVATAR_DEFAULT

def set_avatar_url(self, src_path):
    import re
    try:
        avatar = UserAvatar.objects.get(user=self)
        old_path = os.path.join(settings.BASE_DIR, re.sub(r'^/', '', avatar.avatar.url))
        old_filename = os.path.splitext(os.path.split(old_path)[-1])[0]
        start_num = int(old_filename.split('_')[-1])+1
    except:
        avatar = UserAvatar(user=self)
        old_path = ''
        start_num = 0
    img_format = os.path.splitext(os.path.split(src_path)[-1])[-1]
    # 新的文件名,有可能上一次保存成功，该路径还存在
    new_filename = '%s_64_%s%s'%(self.id, start_num, img_format)
    new_path = os.path.join(settings.BASE_DIR, 'media', AVATAR_ROOT, new_filename)
    # 图片复制（或者覆盖原path）
    shutil.copy(src_path, new_path)
    avatar.avatar = os.path.join(AVATAR_ROOT, new_filename)
    avatar.save()
    if os.path.isfile(old_path):
        os.remove(old_path)
    
# 动态绑定方法
User.set_avatar_url = set_avatar_url
User.get_avatar_url = get_avatar_url

class CheckCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    check_code = models.CharField(max_length=10)
    created_time = models.DateTimeField(auto_now=True)