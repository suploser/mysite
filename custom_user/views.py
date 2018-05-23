from datetime import timedelta
from datetime import datetime
from django.utils import timezone
from django.shortcuts import render,redirect
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse
from .models import User, ConfirmString
from blog.models import Blog
from .forms import loginForm, RegForm
import utils
# Create your views here.
def user_info(request):
    context = {}
    return render(request, 'user_info.html', context)

def get_error(field, form):
    return ','.join(form.errors.get(field,''))

def overall_login(request):
    data = {}
    login_form = loginForm(request.POST)
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        #写入session表的用户信息
        request.session.set_expiry(0)
        request.session['username'] = user.username
        request.session['password'] = user.password
        request.session['is_supuser'] = user.is_supuser
        request.session['email'] = user.email
        request.session['last_login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        request.session['user'] = 'user'
        data['status'] = 'Success'
        data['referer'] = request.META.get('HTTP_REFERER', reverse('home'))
        return JsonResponse(data)
    data['status'] = 'Error'
    data['username_error'] = get_error('username', login_form)
    data['password_error'] = get_error('password', login_form)
    data['non_field_error'] = ','.join(login_form.non_field_errors())
    return JsonResponse(data)

def overall_regist(request):
    data = {}
    reg_form = RegForm(request.POST)
    if reg_form.is_valid():
        username = reg_form.cleaned_data['username']
        email = reg_form.cleaned_data['email']
        password = reg_form.cleaned_data['password']
        password = utils.hash_token(password)
        user = User(username=username, password=password, email=email)
        user.save()
        referer = request.META.get('HTTP_REFERER', reverse('home'))
        #发送邮件
        token = utils.make_confirm_string(username)
        utils.send_confirm_email(email, token, referer)
        ConfirmString.objects.create(user=user, token=token)
        data['status'] = 'Success'
        data['referer'] = referer
        return JsonResponse(data)
    data['status'] = 'Error'
    data['username_error'] = get_error('username', reg_form)
    data['email_error'] = get_error('email',reg_form)
    data['password_error'] = get_error('password', reg_form)
    data['password_again_error'] = get_error('password_again', reg_form)
    return JsonResponse(data)
    
def login(request): 
    login_form = loginForm()
    referer = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        # print(request.POST.get('csrfmiddlewaretoken', ''))
        login_form = loginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            #写入session表的用户信息
            request.session.set_expiry(0)
            request.session['username'] = user.username
            request.session['password'] = user.password
            request.session['is_supuser'] = user.is_supuser
            request.session['email'] = user.email
            request.session['last_login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            request.session['user'] = 'user'
            
            return redirect(referer)
    return render(request, 'login.html', {'login_form':login_form,'referer':referer})

def regist(request):
    regist_form = RegForm()
    if request.method == 'POST':
        regist_form = RegForm(request.POST)
        if regist_form.is_valid():

            username = regist_form.cleaned_data['username']
            email = regist_form.cleaned_data['email']
            password = regist_form.cleaned_data['password']
            #密码加密
            password = utils.hash_token(password)
            user = User(username=username, email=email, password=password)
            user.save()
            referer = request.GET.get('from', reverse('home'))
            token = utils.make_confirm_string(user.username)
            utils.send_confirm_email(email, token, referer)
            ConfirmString.objects.create(user=user, token=token)
            message = '注册成功, 请前往邮箱确认'
            referer = 'http://127.0.0.1:8000'+referer
            return render(request, 'confirm.html', {'message':message, 'referer':referer})
    return render(request, 'regist.html', {'regist_form':regist_form})

def confirm(request):
    token = request.GET.get('token')
    referer = request.GET.get('from')
    confirm = ConfirmString.objects.filter(token=token).first()
    if not confirm:
        message = '无效的链接'
        referer = reverse('regist')+"?from="+referer
        return render(request, 'confirm.html',{'message':message, 'referer':referer})
    now = timezone.now()
    reg_time = confirm.reg_time
    if  now > reg_time + timedelta(days=settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '链接已过期,请重新注册!'
        referer = reverse('regist')+"?from="+referer
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '注册成功,请到登录页登录,即将跳转至登录页!'
        referer = reverse('login')+"?from="+referer
    return render(request, 'confirm.html',{'message':message, 'referer':referer})


def logout(request):
    referer = request.META.get('HTTP_REFERER',reverse('home'))
    session_key = request.session.session_key
    # print(session_key)
    if request.session.exists(session_key):
        request.session.delete(session_key)
    return redirect(referer)