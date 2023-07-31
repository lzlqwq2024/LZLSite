from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.utils.html import conditional_escape
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from . import models
from login.models import User
import hashlib

# Create your views here.

def get_root_comments(comments):
    roots = []
    for comment in comments:
        if not comment.parent_comment:
            roots.append(comment)
    return roots

def search_comments(root, result=[]):
    result.append(root)
    if root.child_comment:
        child_list = root.child_comment.split(" ")
        child_list = [models.Comment.objects.get(id=i) for i in child_list]
        for child in child_list:
            search_comments(child, result)
    return result

def get_comments(comments):
    roots = get_root_comments(comments)
    comment_list = []
    for root in roots:
        comment_list = comment_list + search_comments(root, [])
    return comment_list

def get_child_comments(comments):
    for comment in comments:
        comment.child_comment = ""
        comment.save()
    for comment in comments:
        if comment.parent_comment:
            parent = comment.parent_comment
            if parent.child_comment:
                parent.child_comment = parent.child_comment + " " + str(comment.id)
                parent.save()
            else:
                parent.child_comment = str(comment.id)
                parent.save()

def blog(request, blog_id):
    login = conditional_escape(request.session.get('is_login', ''))
    if login:
        try:
            name = conditional_escape(request.session.get('user_name'))
            user = User.objects.get(name=name)
            loved_blog = user.loved_blog.split(" ")
        except:
            name = None
            user = None
            loved_blog = None
    else:
        name = None
        user = None
        loved_blog = None
    
    try:
        blog = models.Blog.objects.get(id=int(blog_id))
        blog.seen += 1
        blog.save()

        if loved_blog:
            if str(blog_id) in loved_blog:
                loved = True
            else:
                loved = False
        else:
            loved = False

        try:
            category = blog.category
        except:
            category = None

        try:
            tag_list = blog.tag.all()
        except:
            tag_list = None
    except:
        blog = None
        category = None
        tag_list = None
        loved = False

    if user and blog:
        if request.method == "POST":
            love = conditional_escape(request.POST.get("love", "2"))
            if int(love) == 0:
                if str(blog_id) in loved_blog:
                    pos = loved_blog.index(str(blog_id))
                    loved_blog.pop(pos)

                    loved_blog_str = ""
                    for i in range(0, len(loved_blog)):
                        if (i == 0):
                            loved_blog_str = str(loved_blog[0])
                        else:
                            loved_blog_str = loved_blog_str + " " + str(loved_blog[i])
                    
                    user.loved_blog = loved_blog_str
                    blog.love = blog.love-1
                    blog.seen = blog.seen-1
                    loved = False
                    user.save()
                    blog.save()
            elif int(love) == 1:
                if str(blog_id) not in loved_blog:
                    if (user.loved_blog):
                        user.loved_blog = user.loved_blog + " " + str(blog_id)
                    else:
                        user.loved_blog = str(blog_id)
                    blog.love = blog.love+1
                    blog.seen = blog.seen-1
                    loved = True

                    user.save()
                    blog.save()

    message = ""
    if request.method == "POST":
        if user and blog:
            try:
                content = request.POST.get("add_comment", "")
                if user.no_comment:
                    message = "您正处于禁言状态，无法创建评论！"
                elif content:
                    models.Comment.objects.create(user=user, blog=blog, text=content)
                    blog.comment_num = blog.comment_num+1
                    blog.save()
                else:
                    message = "评论内容不能为空！"
            except:
                message = "未知错误，无法创建评论！"

    comments = models.Comment.objects.filter(blog=blog)
    get_child_comments(comments)
    comments = models.Comment.objects.filter(blog=blog)
    comment_list = get_comments(comments)

    if blog:
        comment_sum = int(blog.comment_num)
    else:
        comment_sum = None
    
    return render(request, 'blog/blog.html', {'blog': blog, 'category': category, 'tag_list': tag_list, 'loved': loved, 'login': login, 'username':name, 'user':user, 'comment_list': comment_list, 'comment_sum': comment_sum, 'message': message})

def comment_reply(request, blog_id, comment_id):
    login = conditional_escape(request.session.get('is_login', None))
    if not login:
        return redirect(reverse('blog', args=(int(blog_id), )))
    
    blog = get_object_or_404(models.Blog, id=int(blog_id))
    comment = get_object_or_404(models.Comment, id=int(comment_id))
    name = conditional_escape(request.session.get('user_name'))
    user = User.objects.get(name=name)

    message = ""
    if request.method == "POST":
        reply_comment = request.POST.get("reply_comment", "")
        try:
            user = User.objects.get(name=conditional_escape(request.session.get("user_name", "")))
            if user.no_comment:
                message = "您已经被禁言，无法创建评论！"
            if reply_comment:
                models.Comment.objects.create(user=user, blog=blog, text=reply_comment, parent_comment=comment)
                blog.comment_num = blog.comment_num+1
                blog.save()
                return redirect(reverse('blog', args=(int(blog_id), )))
            else:
                message = "评论内容不能为空！"
        except:
            message = "请先登录后再创建评论！"

    context = {'blog': blog, 'comment': comment, 'message': message, 'login': login, 'username': name, 'user': user}
    return render(request, 'blog/reply_comment.html', context)

def category(request, category_id, request_page):
    login = conditional_escape(request.session.get('is_login', ''))

    if login:
        try:
            name = conditional_escape(request.session.get('user_name'))
            user = User.objects.get(name=name)
        except:
            name = None
            user = None
    else:
        name = None
        user = None

    try:
        category = models.Category.objects.get(id=category_id)
    except:
        category = None

    all_blog = models.Blog.objects.filter(status=1, category=category)
    paginator = Paginator(all_blog, 9)

    page = paginator.get_page(request_page)
    page_sum = paginator.num_pages

    if page_sum <= 7:
        page_list = [i for i in range(1, page_sum+1)]
    elif request_page in [i for i in range(1,5)]:
        page_list = [i for i in range(1, 8)]
    elif request_page in [i for i in range(page_sum-3,page_sum+1)]:
        page_list = [i for i in range(page_sum-6,page_sum+1)]
    else:
        page_list = [i for i in range(request_page-3, request_page+4)]

    return render(request, 'blog/category.html', {'active_category':category, 'all_category': models.Category.objects.all(), 'blogs':page, 'page_sum':page_sum, 'page_num':request_page, 'page_list':page_list, 'login':login, 'user':user, 'username':name})

def list(request, request_page=1):
    login = conditional_escape(request.session.get('is_login', ''))

    if login:
        try:
            name = conditional_escape(request.session.get('user_name'))
            user = User.objects.get(name=name)
            if name == 'lzl20220405':
                show_manage_page = 1
            else:
                show_manage_page = 0
        except:
            name = None
            user = None
            show_manage_page = 0
    else:
        name = None
        user = None
        show_manage_page = 0

    all_blog = models.Blog.objects.filter(status=1)
    paginator = Paginator(all_blog, 9)
    
    page = paginator.get_page(request_page)
    page_sum = paginator.num_pages

    if page_sum <= 7:
        page_list = [i for i in range(1, page_sum+1)]
    elif request_page in [i for i in range(1,5)]:
        page_list = [i for i in range(1, 8)]
    elif request_page in [i for i in range(page_sum-3,page_sum+1)]:
        page_list = [i for i in range(page_sum-6,page_sum+1)]
    else:
        page_list = [i for i in range(request_page-3, request_page+4)]
    
    return render(request, 'blog/list.html', {'show_manage_page': show_manage_page, 'all_category': models.Category.objects.all(), 'blogs':page, 'page_sum':page_sum, 'page_num':request_page, 'page_list':page_list, 'login':login, 'user':user, 'username':name})

def hashcode(s, salt="LZLBlog"):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()

def write(request):
    login = conditional_escape(request.session.get('is_login', ''))
    message = ""

    if login:
        try:
            name = conditional_escape(request.session.get('user_name'))
            user = User.objects.get(name=name) 
            if name == 'lzl20220405': 
                limit = 0
            else:
                limit = 1
        except:
            name = None
            user = None
            limit = 1
    else:
        name = None
        user = None
        limit = 1

    if request.method == "POST":
        message = "出现未知错误，无法创建博客！"
        title = conditional_escape(request.POST.get("blog_title", ""))
        desc = conditional_escape(request.POST.get("blog_desc", ""))
        category = conditional_escape(request.POST.get("blog_category", ""))
        tag = conditional_escape(request.POST.get("blog_tag", ""))
        status = conditional_escape(request.POST.get("blog_status", ""))
        content = request.POST.get("blog_content", "")

        try:
            cover = request.FILES['blog_cover']
        except:
            cover = None

        if not (title and desc and status and content):
            message = "请检查填写的格式是否正确！"
            return render(request, 'blog/write.html', {'message': message, 'login': login, 'username': name, 'user': user, 'limit':limit, 'all_category': models.Category.objects.all(), 'all_tag':models.Tag.objects.all()})
        
        try:
            tag_name_list = tag.split(" ")
            tag_models = []
        except:
            message = "请检查填写的数据是否正确！"
            return render(request, 'blog/write.html', {'message': message, 'login': login, 'username': name, 'user': user, 'limit':limit, 'all_category': models.Category.objects.all(), 'all_tag':models.Tag.objects.all()})

        if category:
            try:
                category_model = models.Category.objects.get(name=category)
            except:
                category_model = models.Category.objects.create(name=category)
        else:
            category_model = None

        for tag_name in tag_name_list:
            if tag_name:
                try:
                    tag_models.append(models.Tag.objects.get(name=tag_name))
                except:
                    tag_models.append(models.Tag.objects.create(name=tag_name))

        new_blog = models.Blog.objects.create(title=title, desc=desc, content=content, status=int(status), category=category_model, owner=models.User.objects.get(name="lzl20220405"))
        
        if cover:
            new_blog.cover = cover

        for tag_model in tag_models:
            if tag_model:
                new_blog.tag.add(tag_model)

        new_blog.save()
        return redirect(reverse('manage', args=(1, )))
    
    return render(request, 'blog/write.html', {'message': message, 'login': login, 'username': name, 'user': user, 'limit':limit, 'all_category': models.Category.objects.all(), 'all_tag':models.Tag.objects.all()})

def update(request, blog_id):
    login = conditional_escape(request.session.get('is_login', ''))
    message = ""

    if login:
        try:
            name = conditional_escape(request.session.get('user_name'))
            user = User.objects.get(name=name) 
            if name == 'lzl20220405': 
                limit = 0
            else:
                limit = 1
        except:
            name = None
            user = None
            limit = 1
    else:
        name = None
        user = None
        limit = 1

    try:
        blog = models.Blog.objects.get(id=blog_id)
    except:
        blog = None

    if not blog:
        return render(request, 'blog/update.html', {'message': message, 'blog':blog, 'login': login, 'username': name, 'user': user, 'limit':limit, 'all_category': models.Category.objects.all(), 'all_tag':models.Tag.objects.all()})

    if request.method == "POST":
        message = "出现未知错误，无法修改博客！"
        title = conditional_escape(request.POST.get("blog_title", ""))
        desc = conditional_escape(request.POST.get("blog_desc", ""))
        category = conditional_escape(request.POST.get("blog_category", ""))
        tag = conditional_escape(request.POST.get("blog_tag", ""))
        status = conditional_escape(request.POST.get("blog_status", ""))
        content = request.POST.get("blog_content", "")

        try:
            cover = request.FILES['blog_cover']
        except:
            cover = None

        if not (title and desc and status and content):
            message = "请检查填写的格式是否正确！"
            return render(request, 'blog/update.html', {'message': message, 'blog': blog, 'all_blog_tag': blog.tag.all(), 'login': login, 'username': name, 'user': user, 'limit':limit, 'all_category': models.Category.objects.all(), 'all_tag':models.Tag.objects.all()})
        
        try:
            tag_name_list = tag.split(" ")
            tag_models = []
        except:
            message = "请检查填写的数据是否正确！"
            return render(request, 'blog/update.html', {'message': message, 'blog': blog, 'all_blog_tag': blog.tag.all(), 'login': login, 'username': name, 'user': user, 'limit':limit, 'all_category': models.Category.objects.all(), 'all_tag':models.Tag.objects.all()})

        if int(status) == 0:
            blog.delete()
            return redirect(reverse('manage', args=(1, )))
        
        if category:
            try:
                category_model = models.Category.objects.get(name=category)
            except:
                category_model = models.Category.objects.create(name=category)

        for tag_name in tag_name_list:
            if tag_name:
                try:
                    tag_models.append(models.Tag.objects.get(name=tag_name))
                except:
                    tag_models.append(models.Tag.objects.create(name=tag_name))

        blog.title = title
        blog.desc = desc
        blog.content = content
        blog.status = int(status)
        
        if category:
            blog.category = category_model
        else:
            blog.category = None
        
        if cover:
            blog.cover = cover

        blog.tag.clear()
        for tag_model in tag_models:
            blog.tag.add(tag_model)

        blog.save()
        message = '修改博客成功！'

    return render(request, 'blog/update.html', {'message': message, 'blog':blog, 'login': login, 'all_blog_tag': blog.tag.all(), 'username': name, 'user': user, 'limit':limit, 'all_category': models.Category.objects.all(), 'all_tag':models.Tag.objects.all()})

def manage(request, request_page=1):
    login = conditional_escape(request.session.get('is_login', ''))

    if login:
        try:
            name = conditional_escape(request.session.get('user_name'))
            user = User.objects.get(name=name) 
            if name == 'lzl20220405': 
                limit = 0
            else:
                limit = 1
        except:
            name = None
            user = None
            limit = 1
    else:
        name = None
        user = None
        limit = 1

    all_blog = models.Blog.objects.all()
    paginator = Paginator(all_blog, 9)
    
    page = paginator.get_page(request_page)
    page_sum = paginator.num_pages

    if page_sum <= 7:
        page_list = [i for i in range(1, page_sum+1)]
    elif request_page in [i for i in range(1,5)]:
        page_list = [i for i in range(1, 8)]
    elif request_page in [i for i in range(page_sum-3,page_sum+1)]:
        page_list = [i for i in range(page_sum-6,page_sum+1)]
    else:
        page_list = [i for i in range(request_page-3, request_page+4)]
    
    return render(request, 'blog/manage.html', {'limit': limit, 'blogs':page, 'page_sum':page_sum, 'page_num':request_page, 'page_list':page_list, 'login':login, 'user':user, 'username':name})

def update_category_and_tag(request):
    login = conditional_escape(request.session.get('is_login', ''))
    message = ""

    if login:
        try:
            name = conditional_escape(request.session.get('user_name'))
            user = User.objects.get(name=name) 
            if name == 'lzl20220405': 
                limit = 0
            else:
                limit = 1
        except:
            name = None
            user = None
            limit = 1
    else:
        name = None
        user = None
        limit = 1

    if request.method == "POST":
        category_name = conditional_escape(request.POST.get("category_name", ""))
        tag_name = conditional_escape(request.POST.get("tag_name", ""))
        category_color = conditional_escape(request.POST.get("category_color", ""))
        tag_color = conditional_escape(request.POST.get("tag_color"))

        if not((category_name or tag_name) and (category_color or tag_color)):
            message = "请检查填写的格式是否正确！"
            return render(request, 'blog/update_category_and_tag.html', {'message': message, 'limit': limit, 'all_category':models.Category.objects.all(), 'all_tag':models.Tag.objects.all(), 'login':login, 'user':user, 'username':name})

        try:
            if category_name:
                category = models.Category.objects.get(name=category_name)
            else:
                category = None

            if tag_name:
                tag = models.Tag.objects.get(name=tag_name)
            else:
                tag = None
        except:
            message = "请检查填写的数据是否正确！"
            return render(request, 'blog/update_category_and_tag.html', {'message': message, 'limit': limit, 'all_category':models.Category.objects.all(), 'all_tag':models.Tag.objects.all(), 'login':login, 'user':user, 'username':name})
        
        if category:
            category.color = category_color
            category.save()

        if tag:
            tag.color = tag_color
            tag.save()

        message = "修改分类与标签成功！"

    return render(request, 'blog/update_category_and_tag.html', {'message': message, 'limit': limit, 'all_category':models.Category.objects.all(), 'all_tag':models.Tag.objects.all(), 'login':login, 'user':user, 'username':name})

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