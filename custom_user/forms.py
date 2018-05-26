from django import forms
from .models import User, ConfirmString, CheckCode
import utils

class loginForm(forms.Form):
    username = forms.CharField(label='用户名',
        widget=forms.TextInput(
            attrs={'id':'login-username', 'class':'form-control','placeholder':"请输入用户名"}),
        error_messages={'required':'用户名不能为空'}
        )
    password = forms.CharField(
        label='密码', 
        widget=forms.PasswordInput(
            attrs={'id':'login-password','class':'form-control','placeholder':"请输入密码"}),
        error_messages={'required':'密码不能为空'}
        )

    def clean(self):
        username = self.cleaned_data.get('username','')
        password = self.cleaned_data.get('password','')
        password = utils.hash_token(password)
        user = User.objects.filter(username=username, password=password).first()
        if not user:
            raise forms.ValidationError('用户名或密码错误')
        elif not user.has_confirmed:
            raise forms.ValidationError('用户尚未验证,请前往邮箱验证')
        else:
            self.cleaned_data['user'] = user
        return self.cleaned_data

class RegForm(forms.Form):
    username = forms.CharField(
        label='用户名', 
        min_length=6, max_length=20,
        widget=forms.TextInput(
            attrs={'id':'reg-username', 'class':'form-control','placeholder':"请输入用户名"}),
        # error_messages={'required':'用户名不能为空'}
        )
    email = forms.EmailField(label='邮箱',
        widget=forms.EmailInput(attrs={'id':'email', 'class':'form-control','placeholder':"请输入邮箱"}))
    password = forms.CharField(label='密码',
        max_length=20, min_length=8,
        widget=forms.PasswordInput(attrs={'class':'form-control reg-password','placeholder':"请输入密码"}))
    password_again = forms.CharField(label='再一次输入密码',
        max_length=20, min_length=8,
        widget=forms.PasswordInput(attrs={'class':'form-control reg-password','placeholder':"请再输入一次密码"}))

    def clean_username(self):
        username = self.cleaned_data['username']
        user = User.objects.filter(username=username)
        if user:
            raise forms.ValidationError('用户名已注册')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email):
            raise forms.ValidationError('邮箱已使用')
        return email

    def clean_password_again(self):
        password = self.cleaned_data.get('password','')
        password_again = self.cleaned_data['password_again']
        if password_again != password:
            raise forms.ValidationError('两次密码输入不一致')
        return password_again


class ForgetPwdForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'请输入注册时所用邮箱'})
    )
    pwd_1 = forms.CharField(
        label='新的密码',
        min_length=8,
        max_length=20,
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输入8-20位的新密码'})
        ) 
    pwd_2 = forms.CharField(
        label='再输入一次',
        min_length=8,
        max_length=20,
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'再一次输入密码'})
        ) 
    check_code = forms.CharField(
        label='验证码',
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'请输入验证码'})
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email):
            raise form.ValidationError('该邮箱未被注册')
        return email

    def clean_pwd_2(self):
        # 验证两次输入的密码是否相同
        pwd_2 = self.cleaned_data.get('pwd_2','')
        pwd_1 = self.cleaned_data.get('pwd_1')
        if pwd_1 != pwd_2:
            raise forms.ValidationError('两次输入的密码不一致')
        return pwd_2

    def clean_check_code(self):
        check_code = self.cleaned_data.get('check_code')
        email = self.cleaned_data.get('email')
        # 该验证方式更加严谨
        # 验证码是否正确
        user = User.objects.get(email=email)   
        if not CheckCode.objects.filter(user=user):
            raise forms.ValidationError('未获取验证码')    
        code = CheckCode.objects.get(user=user)
        if code.check_code != check_code:
            raise forms.ValidationError('验证码不正确')
        # 验证码是否失效
        from datetime import timedelta
        from django.utils import timezone
        if timezone.now() - code.created_time > timedelta(seconds=600):
            # 删除过期验证码
            code.delete()
            raise forms.ValidationError('验证码失效，请重新获取')
       
        return check_code


