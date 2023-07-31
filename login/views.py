from django.conf import settings
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import conditional_escape
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token
from django.http import JsonResponse
from django.utils import timezone
from . import models
import hashlib, datetime, random, pytz

# Create your views here.

def hashcode(s, salt="LZLBlog"):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()

def login(request):
    if request.session.get("is_login", ""):
        return redirect(reverse('index'))
    
    visitnum = int(conditional_escape(request.session.get('visit_num', 0)))
    if visitnum <= 3:
        request.session['visit_num'] = visitnum+1
    else:
        turn_visit_num = conditional_escape(request.POST.get('turn_visit_num',0))
        if turn_visit_num:
            request.session['visit_num'] = 1

    try:
        remember_signature = request.get_signed_cookie(key=hashcode('LZLBlog'), salt=hashcode('LZLBlog'), max_age=7*24*3600)
        if remember_signature == hashcode(hashcode('LZLBlog')):
            href = conditional_escape(request.COOKIES.get('redirect_href',None))
            if href:
                return redirect(href)
            else:
                username = conditional_escape(request.get_signed_cookie(key=hashcode('username'), salt=hashcode(hashcode('username')), max_age=7*24*3600))
                return redirect(reverse('index'))
    except:
        pass

    if request.method == "POST":     
        username = conditional_escape(request.POST.get("username",''))
        password = conditional_escape(request.POST.get("password",''))
        message = '请检查填写的内容格式是否正确！'
        if username.strip() and password:
            try:
                user = models.User.objects.get(name=username)
            except:
                try:
                    user = models.User.objects.get(email=username)
                except:
                    message = '用户名或密码不正确！'
                    return render(request, 'login/login.html', {'message':message})
            if user.password == hashcode(password):
                if not(user.has_confirmed):
                    message = '用户未经过邮件确认！'
                    return render(request, 'login/login.html', {'message':message})
                request.session['is_login'] = 1
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name

                response = redirect(reverse('index'))
                remember = request.POST.get('remember', '')
                href = conditional_escape(request.COOKIES.get('redirect_href','')) 
                if remember:
                    response.set_signed_cookie(key=hashcode('LZLBlog'), value=hashcode(hashcode('LZLBlog')), salt=hashcode('LZLBlog'), max_age=7*24*3600)
                    response.set_signed_cookie(key=hashcode('username'), value=hashcode(user.name), salt=hashcode(hashcode('username')), max_age=7*24*3600)
                if href:
                    return redirect(href)
                else:
                    return response
            else:
                message = '用户名或密码不正确！'
                return render(request, 'login/login.html', {'message':message})            
    else:
        message = ''
    
    return render(request, 'login/login.html', {'message':message})

def password_verification(password):
    message = ''
    if len(password) < 8:
        message = '密码位数必须至少有 8 位！'
        return message
    for chars in password:
        if '\u4e00' <= chars and chars <= '\u9fff':
            message = '密码中不可以包含中文字符！'
            return message
    en = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    capital_en = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    number = ['1','2','3','4','5','6','7','8','9']
    flag = 0
    for letter in en:
        if letter in password:
            flag = flag + 1
            break
    for letter in capital_en:
        if letter in password:
            flag = flag + 1
            break
    for num in number:
        if num in password:
            flag = flag+1
            break
    if flag < 2:
        message = '密码必须至少包含小写字母、大写字母和数字中的两种！'
        return message
    return message

def email_verification(email):
    message = ''
    emaillist = list(email)
    if emaillist.count('@') != 1:
        message = '请检查邮箱格式是否正确！'
        return message
    if emaillist.index('@') == 0 or emaillist.index('@') == len(emaillist)-1:
        message = '请检查邮箱格式是否正确！'
        return message
    return message

def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hashcode(user.name, now)
    tag = hashcode(user.name, "tag")
    get_str = ''
    for x in range(6):
        num = random.randint(0,len(code)-1)
        get_str = get_str + code[num]
    models.ConfirmString.objects.create(code=get_str, user=user, tag=tag)
    return (get_str,tag)

def send_email(email, code):
    from django.core.mail import EmailMultiAlternatives
    subject = "来自 www.LZLBlog.com 的注册确认邮件"
    text_content = '''感谢注册 www.LZLBlog.com, 欢迎阅读作者的博客并发表评论与改进意见，
                    如果您看到这条信息，说明您的邮箱服务器不支持 HTML 链接功能，请检查或升级系统以解决问题！'''
    html_content = '''
                    <p>感谢注册<a href="http://{}/index/index/" target=_blank> www.LZLBlog.com </a>，
                    欢迎阅读作者的博客并发表评论与改进意见！</p>
                    <p>您的验证码是：</p><h1> {} </h1>
                    <p>此验证码有效期为 {} 天！</p>
                    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def register(request):
    if request.method == 'POST':
        username = conditional_escape(request.POST.get('username',''))
        password = conditional_escape(request.POST.get('password',''))
        password_repeat = conditional_escape(request.POST.get('password_again',''))
        email = conditional_escape(request.POST.get('email',''))
        message = "请检查填写的内容格式是否正确！"
        if username.strip() and password and password_repeat and email:
            if password != password_repeat:
                message = "两次输入的密码不同！"
                return render(request, 'login/register.html', {'message':message})
            else:
                user_list = models.User.objects.filter(name=username)
                if user_list:
                    message = "该用户名已经存在！"
                    return render(request, 'login/register.html', {'message':message})
                email_list = models.User.objects.filter(email=email)
                if email_list:
                    message = "该邮箱已经被注册了！"
                    return render(request, 'login/register.html', {'message':message})
                if password_verification(password):
                    message = password_verification(password)
                    return render(request, 'login/register.html', {'message':message})
                if email_verification(email):
                    message = email_verification(email)
                    return render(request, 'login/register.html', {'message':message})                   
                
                new_user = models.User()
                new_user.name = username
                new_user.password = hashcode(password_repeat)
                new_user.email = email
                new_user.save()

                code,tag = make_confirm_string(new_user)
                send_email(email, code)
                request.session['tag'] = tag

                return redirect(reverse('comfirm'))
        else:
            return render(request, 'login/register.html', {'message':message})
    return render(request, 'login/register.html')

def user_confirm(request):
    message = ''
    if request.method == "POST":
        tag = conditional_escape(request.session.get('tag', ''))
        email_password = conditional_escape(request.POST.get('email_password',''))
        try:
            confirm = models.ConfirmString.objects.get(tag=tag)
        except:
            return render(request, 'login/confirm.html', {'message':message})
        
        c_time = confirm.c_time
        now = datetime.datetime.now()
        now = now.replace(tzinfo=pytz.timezone('UTC'))
        if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
            confirm.user.delete()
            del request.session['tag']
            message = '您的邮件已经过期！请重新注册!'
            return render(request, 'login/confirm.html', {'message':message})
        if email_password == confirm.code:
            confirm.user.has_confirmed = True
            confirm.user.save()
            confirm.delete()
            del request.session['tag']
            return redirect(reverse('login'))
        else:
            message = '邮箱验证码不正确！'
            return render(request, 'login/confirm.html', {'message':message})
    return render(request, 'login/confirm.html', {'message':message})

def logout(request):
    if not request.session.get('is_login', ''):
        return redirect(reverse('login'))
    
    try:
        response = redirect(reverse('login'))
        response.delete_cookie(key=hashcode('LZLBlog'))
        request.session.flush()
        redirect_href = conditional_escape(request.COOKIES.get('redirect_href',''))
        if redirect_href:
            return redirect(redirect_href)
        else:
            return response
    except:
        request.session.flush()
        redirect_href = conditional_escape(request.COOKIES.get('redirect_href',''))
        if redirect_href:
            return redirect(redirect_href)
        else:
            return redirect(reverse('login'))
        
def make_reset_password_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hashcode(user.name, now)
    repeat_reset_list = models.ResetString.objects.filter(user=user)
    if repeat_reset_list:
        for repeat_reset in repeat_reset_list:
            repeat_reset.delete()

    models.ResetString.objects.create(code=code, user=user)
    return code

def send_reset_password_email(email, code):
    from django.core.mail import EmailMultiAlternatives
    subject = "来自 www.LZLBlog.com 的修改密码邮件"
    text_content = '''感谢来到 www.LZLBlog.com, 欢迎阅读作者的博客并发表评论与改进意见，
                    如果您看到这条信息，说明您的邮箱服务器不支持 HTML 链接功能，请检查或升级系统以解决问题！'''
    html_content = '''
                    <p>感谢来到<a href="http://{}/index/index/" target=_blank> www.LZLBlog.com </a>，
                    欢迎阅读作者的博客并发表评论与改进意见！</p>
                    <h2>点击此链接以重置密码：<a href="http://{}/login/resetpassword/?code={}">重置密码链接</a></h2>
                    <p>此链接有效期为 {} 天！</p>
                    '''.format("127.0.0.1:8000", "127.0.0.1:8000", code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def reset(request):
    message = ''
    if request.method == 'POST':
        email = conditional_escape(request.POST.get('email', ''))
        message = '请检查填写的内容格式是否正确！'
        if email:
            if email_verification(email):
                message = email_verification(email)
                return render(request, 'login/reset.html', {'message':message})
            try:
                user = models.User.objects.get(email=email)
            except:
                message = '请检查填写的邮箱是否正确！'
                return render(request, 'login/reset.html', {'message':message})
            
            code = make_reset_password_confirm_string(user)
            send_reset_password_email(email, code)

            message = '邮件已发送，请查收邮件并通过邮件中的链接修改密码！'
            return render(request, 'login/reset.html', {'message':message})

        return render(request, 'login/reset.html', {'message':message})
    return render(request, 'login/reset.html', {'message':message})

def resetpassword(request):
    code = conditional_escape(request.GET.get('code', ''))
    message = ''
    if request.method == 'POST':
        message = '请检查填写的内容是否符合格式！'
        try:
            confirm = models.ResetString.objects.get(code=code)
        except:
            message = '无效的修改密码链接！'
            return render(request, 'login/resetpassword.html', {'message':message, 'code':''})

        c_time = confirm.c_time
        user = confirm.user
        password = conditional_escape(request.POST.get('password', ''))
        password_repeat = conditional_escape(request.POST.get('password_repeat', ''))
        now = datetime.datetime.now()
        now = now.replace(tzinfo=pytz.timezone('UTC'))
        if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
            message = '邮件已过期，请重新重置密码！'
            confirm.delete()
            return render(request, 'login/resetpassword.html', {'message':message, 'code':code})
        
        if password and password_repeat:
            if password != password_repeat:
                message = '两次输入的密码不同！'
                return render(request, 'login/resetpassword.html', {'message':message, 'code':code})
            if password_verification(password):
                message = password_verification(password)
                return render(request, 'login/resetpassword.html', {'message':message, 'code':code})

            user.password = hashcode(password_repeat)
            user.save()
            confirm.delete()

            response = redirect(reverse('login'))
            try:
                response.delete_cookie(key=hashcode('LZLBlog'))
                request.session.flush()
            except:
                request.session.flush()
            return response

        return render(request, 'login/resetpassword.html', {'message':message, 'code':code}) 
    return render(request, 'login/resetpassword.html', {'message':message, 'code':code}) 

def index(request, name):
    try:
        user = models.User.objects.get(name=name)
        username = user.name
    except:
        user = None
        username = None
    if not(user):
        limits = 1
        render(request, 'login/index.html', {'user':user, 'limits':limits, 'username':username, 'login':request.session.get('is_login', '')})
    elif not(request.session.get('is_login', '')) or request.session.get('user_name','') != user.name:
        limits = 1
        return render(request, 'login/index.html', {'user':user, 'limits':limits, 'username':username, 'login':request.session.get('is_login', '')})
    else:
        limits = 0

    if request.method == "POST":
        big_detail = request.POST.get("big_detail", "")
        if big_detail:
            user.big_detail = big_detail
            user.save()
        
        small_description = conditional_escape(request.POST.get('small_description', ''))
        if small_description:
            user.small_description = small_description
            user.save()

        try:
            avatar = request.FILES['avatar']
        except:
            avatar = None
        if avatar:
            user.avatar = avatar
            user.save()

    return render(request, 'login/index.html', {'user':user, "limits":limits, 'username':username, 'login':request.session.get('is_login', '')})

@csrf_exempt
def upload_image(request):
    import os

    if request.method == "POST":
        file_obj = request.FILES['file']
        file_name_suffix = file_obj.name.split(".")[-1]
        if file_name_suffix not in ["jpg", "png", "gif", "jpeg"]:
            return JsonResponse({"message": "错误的文件格式"})

        upload_time = timezone.now()
        path = os.path.join(
            settings.MEDIA_ROOT,
            'tinymce',
            str(upload_time.year),
            str(upload_time.month),
            str(upload_time.day)
        )

        if not os.path.exists(path):
            os.makedirs(path)

        file_path = os.path.join(path, file_obj.name)

        file_url = f'{settings.MEDIA_URL}tinymce/{upload_time.year}/{upload_time.month}/{upload_time.day}/{file_obj.name}'
        if os.path.exists(file_path):
            return JsonResponse({'message': '文件已存在', 'location': file_url})

        with open(file_path, 'wb+') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

        return JsonResponse({'message': '上传图片成功', 'location': file_url})
    return JsonResponse({'detail': '错误的请求'})

@requires_csrf_token
def page_not_found(request, exception):
    return render(request, 'login/404.html')


