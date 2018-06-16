from django.shortcuts import render
from django.conf import settings
from blog.models import Blog
import redis
redis_client = redis.StrictRedis(host='192.168.1.110')

def home(request):
    # 总浏览量
    if not request.COOKIES.get('home'):
        redis_client.incr('view_counts')
    view_counts = redis_client.get('view_counts').decode('utf-8')
    today_hot_blog_list, yesterday_hot_blog_list, hot_blog_list = \
    Blog.use_cache()
    read_num_list, date_list = Blog.get_seven_days_read_nums()
    context = {}
    context['read_num_list'] = read_num_list
    context['today_hot_blog_list'] = today_hot_blog_list
    context['yesterday_hot_blog_list'] = yesterday_hot_blog_list
    context['hot_blog_list'] = hot_blog_list
    context['date_list'] = date_list
    context['view_counts'] = view_counts
    response = render(request, 'home.html', context=context)
    response.set_cookie('home', 'true')
    return response
