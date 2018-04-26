from django.shortcuts import render_to_response, render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.conf import settings
from .models import Blog, BlogType
from comment.models import Comment

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
    blog_types = BlogType.objects.all()   
    # blog_types = BlogType.objects.annotate(Count('blog'))
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
    return render(request,'blogs_list.html', context=context)

def blogs_by_type(request, blog_type_id):
    blog_type = get_object_or_404(BlogType, pk=blog_type_id)
    # blogs = Blog.objects.filter(blog_type=blog_type_id)
    blogs = blog_type.blog_set.all()
    context = deal_common(request, blogs)
    context['blog_type'] = blog_type
    return render(request,'blogs_by_type.html', context=context)

def blogs_by_date(request, year, month):
    blogs = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = deal_common(request, blogs)
    context['blog_list_title'] = '%s 年 %s 月'% (year, month)
    return render(request,'blogs_by_date.html', context=context)

def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    blog_content_type = ContentType.objects.get_for_model(blog)
    cookies_key = blog.read_statistics_once_read(request)
    #上一篇，下一篇文章
    previous_blog = Blog.objects.filter(created_time__gt=blog.created_time).last()
    next_blog = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context={}
    context['blog'] = blog
    context['previous_blog'] = previous_blog
    context['next_blog'] = next_blog
    response = render(request,'blog_detail.html', context=context)
    response.set_cookie(cookies_key, 'true')
    return response

#判断用户是否为管理员的装饰器
def check_admin(func):
    def wrapper(request):
        if request.session.get('username'):
            if request.session.get('is_supuser'):
                return func(request)
        message = '您不是管理员,无法发表博客'
        return render(request, 'message.html', {'message':message})
    return wrapper

@check_admin
def blog_add(request):
    if request.method == 'POST':
        data = {}
        title = request.POST.get('blog_title')
        blog_type = request.POST.getlist('tag')
        content = request.POST.get('content')
        from custom_user.models import User
        author = User.objects.filter(is_supuser=True).first()
        blog_type_list = []
        for tag in blog_type:
            blog_type_id = int(tag)
            blog_type_list.append(blog_type_id)

        try:
            if len(title) <=0 or len(title)>=50:
                raise Exception('请输入一个不超过50个字符的标题')
            if len(blog_type_list) == 0:
                raise Exception('请选择至少一个分类')
            if len(content) == 0:
                raise Exception('请输入博客内容')
            blog = Blog()
            blog.title = title
            blog.content = content
            blog.author = author
            blog.save()
            #ManyToManyField保存方式
            for blog_type in BlogType.objects.filter(id__in=blog_type_list):
                blog.blog_type.add(blog_type)

            data['status'] = 'Success'
            from django.urls import reverse
            data['message'] = reverse('blog_detail', args=[blog.id,])
        except Exception as e:
            data['status'] = 'Fail'
            data['message'] = e
        from django.http import JsonResponse
        return JsonResponse(data)

    return render(request, 'blog_add.html')