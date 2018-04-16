from django import forms
from custom_user.models import User
import utils

class loginForm(forms.Form):
    username = forms.CharField(label='用户名',
        widget=forms.TextInput(
            attrs={'id':'login-username', 'class':'form-control'}),
        error_messages={'required':'用户名不能为空'}
        )
    password = forms.CharField(
        label='密码', 
        widget=forms.PasswordInput(
            attrs={'id':'login-password','class':'form-control'}),
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
            attrs={'id':'reg-username', 'class':'form-control'}),
        # error_messages={'required':'用户名不能为空'}
        )
    email = forms.EmailField(label='邮箱',
        widget=forms.EmailInput(attrs={'id':'email', 'class':'form-control'}))
    password = forms.CharField(label='密码',
        max_length=20, min_length=8,
        widget=forms.PasswordInput(attrs={'class':'form-control reg-password'}))
    password_again = forms.CharField(label='再一次输入密码',
        max_length=20, min_length=8,
        widget=forms.PasswordInput(attrs={'class':'form-control reg-password'}))

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
