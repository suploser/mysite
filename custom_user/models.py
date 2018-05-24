from django.db import models

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