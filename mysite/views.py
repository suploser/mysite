from datetime import timedelta
from django.shortcuts import render_to_response,render,redirect
from django.urls import reverse
# User有可能有冲突
from blog.models import Blog, User

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


def logout(request):
    referer = request.META.get('HTTP_REFERER',reverse('home'))
    session_key = request.session.session_key
    print(session_key)
    if request.session.exists(session_key):
        request.session.delete(session_key)
    return redirect(referer)