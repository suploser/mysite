import string, random, os, uuid
from datetime import timedelta
from datetime import datetime
from django.utils import timezone
# render返回一个HTTPResponse，set_cookie
from django.shortcuts import render,redirect
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse
from .models import User, ConfirmString , CheckCode
from blog.models import Blog
from .forms import loginForm, RegForm, ForgetPwdForm, ChangePwdForm, ChangeEmailForm
import utils
# Create your views here.
# 登录信息写入session

def write_to_session(request, user):
    request.session.set_expiry(0)
    # 动态绑定方法
    request.session['username'] = user.username
    # request.session['nickname'] = user.userprofile.nickname
    request.session['avatar_url'] = user.get_avatar_url()
    request.session['password'] = user.password
    request.session['is_supuser'] = user.is_supuser
    request.session['email'] = user.email
    request.session['last_login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    request.session['user'] = 'user'

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
        #写入session表的用户信息，考虑封装成一个方法？
        write_to_session(request, user);
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
            write_to_session(request, user);
            return redirect(referer)
    if not request.session.get('username'):
        return render(request, 'login.html', {'login_form':login_form,'referer':referer})
    else:
        return render(request, 'message.html', {'message':'您已登录，不可重复登录或者注销后再次登录'})

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
    # token几乎不会重复,所以偷个懒
    confirm = ConfirmString.objects.filter(token=token).first()
    if not confirm:
        message = '无效的链接'
        referer = reverse('regist')+"?from="+referer
        return render(request, 'confirm.html',{'message':message, 'referer':referer})
    now = timezone.now()
    reg_time = confirm.reg_time
    if  now > reg_time + timedelta(days=settings.CONFIRM_DAYS):
        # 删除失效用户
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

# 把验证码保存到数据库
def get_check_code(request):
    email = request.GET.get('email')
    token = ''.join(random.sample(string.digits+string.ascii_letters, 6))
    data = {}
    try:
        if not User.objects.filter(email=email):
            raise Exception('该邮箱未被注册')
        user = User.objects.get(email=email)
        if CheckCode.objects.filter(user=user):
            code =CheckCode.objects.get(user=user)
            if timezone.now() < timedelta(seconds=60)+ code.created_time:
                raise Exception('已经获取过验证码，请稍后再试')
        else:
            code = CheckCode(user=user)
        # 生成6位验证码
        code.check_code = token
        code.save()
        utils.send_email_code(email, token)
        data['status'] = 'Success'
        data['message'] = '验证码已发送至邮件，注意查收'

    except Exception as e:
        data['status'] = 'Fail'
        data['message'] = str(e)

    finally:
        return JsonResponse(data)

def reset_pwd(request):
    data={}
    if request.method == 'POST':
        forget_pwd_form = ForgetPwdForm(request.POST)
        if forget_pwd_form.is_valid():
            email = forget_pwd_form.cleaned_data['email']
            password = forget_pwd_form.cleaned_data['pwd_1']
            # 修改密码，为custom_user添加一个set_pwd方法（便于加密）？？
            user = User.objects.get(email=email)
            user.password = utils.hash_token(password)
            user.save()
            # 删除验证码
            code = CheckCode.objects.get(user=user)
            code.delete()
            # 重置密码后自动登录
            write_to_session(request, user);
            data['status'] = 'Success'
            data['message'] = '密码修改成功'
            return JsonResponse(data)
        data['status'] = 'Fail'
        data['email_error'] = get_error('email', forget_pwd_form)
        data['pwd_1_error'] = get_error('pwd_1', forget_pwd_form)
        data['pwd_2_error'] = get_error('pwd_2', forget_pwd_form)
        data['check_code_error'] = get_error('check_code', forget_pwd_form)
        return JsonResponse(data)
    return render(request, 'reset_pwd.html')

# 判断是否登录的装饰器
def is_login(is_json=False):
    def _is_login(func):
        def wrapper(request):
            data = {}
            try:
                if not request.session.get('username'):
                    print('*********')
                    raise Exception('您还未登录')
                return func(request) 
            except Exception as e:
                if is_json:
                    data['status'] = 'Fail'
                    data['message'] = str(e)
                    return JsonResponse(data)
                else:
                    # 返回消息页面
                    data['message'] = '您还未登录'
                    return render(request, 'message.html', context=data)
        return wrapper
    return _is_login

@is_login()
def change_pwd(request):
    if request.method == 'POST':
        data = {}
        c_form = ChangePwdForm(request.POST, session=request.session)
        if c_form.is_valid():
            # 找到user对象
            username = request.session.get('username')
            user = User.objects.get(username=username)
            new_pwd = c_form.cleaned_data.get('new_pwd')
            user.password = new_pwd
            user.save()
            # 修改session内容
            request.session['password'] = user.password
            data['status'] = 'Success'
            data['message'] = '密码修改成功'
            return JsonResponse(data)
        data['status'] = 'Fail'
        data['old_pwd_error'] = get_error('old_pwd', c_form )
        data['new_pwd_error'] = get_error('new_pwd', c_form )
        data['new_pwd_again_error'] = get_error('new_pwd_again', c_form)
        data['non_field_error'] = ','.join(c_form.non_field_errors())
        return JsonResponse(data)
    # get方式获取
    return render(request, 'change_pwd.html')

# 获取验证码
# 通过session保存check_code
def get_check_code_1(request):
    email = request.GET.get('email')
    check_code = ''.join(random.sample(string.digits+string.ascii_letters, 4))
    data = {}
    try:
        if User.objects.filter(email=email):
            raise Exception('邮箱已经被使用')
        if request.session.get('check_code'):
            check_code_time = datetime.strptime(request.session.get('check_code_time'),  '%Y-%m-%d %H:%M:%S')
            if check_code_time+timedelta(seconds=30) > datetime.now():
                raise Exception('已获取验证码,请稍后再试')
        request.session['check_code'] = check_code
        request.session['check_code_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        utils.send_email_code(email, check_code)
        data['status'] = 'Success'
        data['message'] = '验证码已发送至邮箱,请注意查收'
    except Exception as e:
        data['status'] = 'Fail'
        data['message'] = str(e)
    finally:
        return JsonResponse(data)

@is_login()
def change_email(request):
    data = {}
    if request.method == 'POST':
        change_email_from = ChangeEmailForm(request.POST, session=request.session)
        if change_email_from.is_valid():
            username = request.session.get('username')
            new_email = change_email_from.cleaned_data.get('new_email')
            user = User.objects.get(username=username)
            user.email = new_email
            user.save()
            # 移除
            request.session.pop('check_code')
            request.session.pop('check_code_time')
            request.session['email'] = user.email
            # del request.session['chcek_code'] 
            data['status'] = 'Success'
            data['message'] = '修改邮箱成功'
            return JsonResponse(data)
        data['status'] = 'Fail'
        data['new_email_error'] = get_error('new_email', change_email_from)
        data['check_code_error'] = get_error('check_code', change_email_from)
        return JsonResponse(data)
    return render(request, 'change_email.html')

@is_login()
def user_avatar(request):
    username = request.session.get('username')
    user = User.objects.get(username=username)
    return render(request, 'user_avatar.html',{'user':user})

@is_login()
def avatar_upload(request):
    if request.method == 'POST':
        data = {}
        if request.FILES.get('avatar_file'):
            avatar_file = request.FILES['avatar_file']
            temp_floder = os.path.join(settings.BASE_DIR, 'media', 'temp')
            if not os.path.isdir(temp_floder):
                os.makedirs(temp_floder)
            temp_filename = uuid.uuid1().hex + os.path.splitext(avatar_file.name)[-1]
            temp_path = os.path.join(temp_floder, temp_filename)
            with open(temp_path, 'wb') as f:
                for chunk in avatar_file.chunks():
                    f.write(chunk)
        else:
            # 未选择图片
            data['status'] = 'Fail'
            data['message'] = '您还未选择图片'
            return JsonResponse(data)
        left = int(float(request.POST['avatar_x']))
        top = int(float(request.POST['avatar_y']))
        right = left + int(float(request.POST['avatar_width']))
        bottom = top + int(float(request.POST['avatar_height']))
        from PIL import Image
        avatar = Image.open(temp_path)
        # 裁剪
        crop_avatar = avatar.convert('RGBA').crop((left, top, right, bottom)).\
        resize((64,64), Image.ANTIALIAS)
        crop_avatar.save(temp_path)
        # 背景白色
        # out = Image.new('RGBA', crop_avatar.size, (255,255,255))
        # out.paste(crop_avatar, (0,0,64,64))
        # out.save(temp_path)
        user = User.objects.get(username=request.session.get('username'))
        user.set_avatar_url(temp_path)
        # ....
        os.remove(temp_path)
        data['status'] = 'Success'
        data['message'] = user.get_avatar_url()
        request.session['avatar_url'] = user.get_avatar_url()
        return JsonResponse(data)
