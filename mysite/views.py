from datetime import timedelta
from django.shortcuts import render_to_response
from blog.models import Blog

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
    return render_to_response('home.html', context=context)
    