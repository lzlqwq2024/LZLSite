from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils.html import conditional_escape
from login.models import User
from . import models

# Create your views here.

def list(request, request_page=1):
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

    all_work = models.Work.objects.all()
    paginator = Paginator(all_work, 9)
    
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

    return render(request, 'work/list.html', {'login': login, 'user':user, 'username':name, 'page_sum':page_sum, 'page_num':request_page, 'page_list':page_list, 'works': page})
