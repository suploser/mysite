from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator
from .models import Blog, BlogType
from django.db.models import Count
from django.conf import settings

def deal_common(request, blogs):
    page_num = int(request.GET.get('page', 1))
    paginator = Paginator(blogs, settings.EACH_PAGE_BLOG_NUMS)
    page_of_blogs = paginator.get_page(page_num)
    #分页
    page_range = list(range(max(page_num-2, 1), page_num))+\
    list(range(page_num, min(page_num+2, paginator.num_pages)+1))
    if page_range[0]-1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages-page_range[-1] >=2:
        page_range.append('...')
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)
    # blog_types = BlogType.objects.all()   
    blog_types = BlogType.objects.annotate(Count('blog'))
    blog_date_list = Blog.objects.dates('created_time', 'month', 'DESC')
    blog_date_dict = {}
    for blog_date in blog_date_list:
        blog_nums = Blog.objects.filter(created_time__year=blog_date.year
            ,created_time__month=blog_date.month).count()
        blog_date_dict[blog_date] = blog_nums
    context = {}
    context['page_range'] = page_range
    context['blogs'] = page_of_blogs
    context['blog_types'] = blog_types
    context['blog_date_dict'] = blog_date_dict
    return context

def blogs_list(request):
    blogs_list = Blog.objects.all()
    context = deal_common(request, blogs_list)
    return render_to_response('blogs_list.html', context=context)

def blogs_by_type(request, blog_type_id):
    blog_type = get_object_or_404(BlogType, pk=blog_type_id)
    # blogs = Blog.objects.filter(blog_type=blog_type_id)
    blogs = Blog.objects.filter(blog_type=blog_type)
    context = deal_common(request, blogs)
    context['blog_type'] = blog_type
    return render_to_response('blogs_by_type.html', context=context)

def blogs_by_date(request, year, month):
    blogs = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = deal_common(request, blogs)
    context['blog_list_title'] = '%s 年 %s 月'% (year, month)
    return render_to_response('blogs_by_date.html', context=context)

def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    cookies_key = blog.read_statistics_once_read(request)
    #上一篇，下一篇文章
    previous_blog = Blog.objects.filter(created_time__gt=blog.created_time).last()
    next_blog = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context={}
    context['blog'] = blog
    context['previous_blog'] = previous_blog
    context['next_blog'] = next_blog
    response = render_to_response('blog_detail.html', context=context)
    response.set_cookie(cookies_key, 'true')
    return response