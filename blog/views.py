from django.shortcuts import render_to_response, render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.urls import reverse
from django.conf import settings
from .models import Blog, BlogType
from comment.models import Comment
from django.http import JsonResponse

def deal_common(request, blogs):
    page_num = int(request.GET.get('page', 1))
    paginator = Paginator(blogs, settings.EACH_PAGE_BLOG_NUMS)
    page_of_blogs = paginator.get_page(page_num)
    #分页逻辑
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
    # 对blog_date_dict按key排序？？
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

#添加博客时判断用户是否为管理员的装饰器
def __check_admin(func):
    def wrapper(request):
        if request.session.get('is_supuser'):
            return func(request)
        message = '您不是管理员,无法发表博客'
        return render(request, 'message.html', {'message':message})
    return wrapper

def check_post_data(request):
    post_data = {}
    title = request.POST.get('blog_title')
    blog_type = request.POST.getlist('tag')
    content = request.POST.get('content')
    from custom_user.models import User
    author = User.objects.filter(is_supuser=True).first()
    blog_type_list = []
    for tag in blog_type:
        blog_type_id = int(tag)
        blog_type_list.append(blog_type_id)
    if len(title) <=0 or len(title)>=50:
        raise Exception('请输入一个不超过50个字符的标题')
    if len(blog_type_list) == 0:
        raise Exception('请选择至少一个分类')
    if len(content) == 0:
        raise Exception('请输入博客内容')
    post_data['title'] = title
    post_data['blog_type_list'] = blog_type_list
    post_data['content'] = content
    post_data['author'] = author
    return post_data

@__check_admin
def blog_add(request):
    if request.method == 'POST':
        data={}
        try:
            post_data = check_post_data(request)
            blog = Blog()
            blog.title = post_data['title']
            blog.content = post_data['content']
            blog.author = post_data['author']
            blog.save()
            #ManyToManyField保存方式,不用save方法
            for blog_type in BlogType.objects.filter(id__in=post_data['blog_type_list']):
                blog.blog_type.add(blog_type)

            data['status'] = 'Success'
            #发表后跳转至该博客页
            data['message'] = reverse('blog_detail', args=[blog.id,])
        except Exception as e:
            data['status'] = 'Fail'
            data['message'] = str(e)
        return JsonResponse(data)
    return render(request, 'blog_add.html')
# 修改博客时的装饰器
def check_admin(return_json=True):
    def __check_admin(func):
        def wrapper(request, blog_id):
            message = ''
            data = {}
            try:
                if not request.session.get('is_supuser'):
                    message = '非管理员不可编辑博文'
                    raise Exception(message)
                if not Blog.objects.filter(id=blog_id):
                    message = '博文不存在'
                    raise Exception(message)
                return func(request, blog_id)
            except Exception as e:
                if return_json:
                    data['status'] = 'Fail'
                    data['message'] = str(e)
                    return JsonResponse(data)
                return render(request, 'message.html', {'message':message})
        return wrapper
    return __check_admin

@check_admin(False)    
def edit(request, blog_id):
    blog = Blog.objects.get(id=blog_id)
    tags = []
    for tag in BlogType.objects.all():
        tag.checked = True if tag in blog.blog_type.all() else False
        tags.append(tag)
    return render(request, 'blog_edit.html', {'blog':blog, 'tags':tags})

# ajax获取博文内容
@check_admin(True)
def ajax_get_content(request, blog_id):
    blog = Blog.objects.get(id=blog_id)
    data = {}
    data['status'] = 'Success'
    data['message'] = blog.content
    return JsonResponse(data)

@check_admin(True)
def edit_ajax_add(request, blog_id):
    data = {}
    try:
        post_data = check_post_data(request)
        blog = Blog.objects.get(id=blog_id)
        blog.title = post_data['title']
        blog.author = post_data['author']
        blog.content = post_data['content']
        blog.save()
        blog.blog_type.clear()
        for blog_type in BlogType.objects.filter(id__in=post_data['blog_type_list']):
            blog.blog_type.add(blog_type)
        data['status'] = 'Success'
        data['message'] = reverse('blog_detail', args=[blog.id,])
    except Exception as e:
        data['status'] = 'Fail'
        data['message'] = str(e)
    return JsonResponse(data)