from datetime import timedelta
from django.shortcuts import render,redirect
from django.urls import reverse
from custom_user.models import User
from blog.models import Blog
from .forms import loginForm, RegForm

def home(request):
    today_hot_blog_list, yesterday_hot_blog_list, hot_blog_list = \
    Blog.use_cache()
    read_num_list, date_list = Blog.get_seven_days_read_nums()
    context = {}
    context['read_num_list'] = read_num_list
    context['today_hot_blog_list'] = today_hot_blog_list
    context['yesterday_hot_blog_list'] = yesterday_hot_blog_list
    context['hot_blog_list'] = hot_blog_list
    context['date_list'] = date_list
    return render(request, 'home.html', context=context)


def login(request):
    '''
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = User.objects.filter(username=username, password=password)
    referer = request.META.get('HTTP_REFERER',reverse('home'))
    if user:
        request.session.set_expiry(0)
        request.session['username'] = username
        request.session['password'] = password
        request.session['user'] = 'user'
        return redirect(referer)
    else:
        return render(request, 'error.html', {'message':'用户名或密码错误'})
        '''
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
            user = User(username=username, email=email, password=password)
            user.save()
                #写入session表的    用户信息
            request.session.set_expiry(0)
            request.session['username'] = username
            request.session['password'] = password
            request.session['user'] = 'user'
            referer = request.GET.get('from', reverse('home'))
            return redirect(referer)
    return render(request, 'regist.html', {'regist_form':regist_form})

def logout(request):
    referer = request.META.get('HTTP_REFERER',reverse('home'))
    session_key = request.session.session_key
    print(session_key)
    if request.session.exists(session_key):
        request.session.delete(session_key)
    return redirect(referer)