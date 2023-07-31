from django.shortcuts import render
from django.utils.html import conditional_escape
from login.models import User
from django.views.decorators.csrf import requires_csrf_token

# Create your views here.

def send_suggestion_email(username, subject, message):
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings

    subject = "来自 {} 的改进建议：{}".format(username, subject)
    text_content = message
    html_content = '''
                    <p>{}</p>
                    '''.format(message)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, ['lzl20220405@163.com'])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def index(request):
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

    if request.method == "POST":
        suggestion_username = conditional_escape(request.POST.get('suggestion_username', ''))
        suggestion_subject = conditional_escape(request.POST.get('suggestion_subject', ''))
        suggestion_message = conditional_escape(request.POST.get('suggestion_message', ''))

        if suggestion_username and suggestion_subject and suggestion_message:
            send_suggestion_email(suggestion_username, suggestion_subject, suggestion_message)
    
    return render(request, 'index/index.html', {'login': login, 'username':name, 'user': user})

def about(request):
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

    if request.method == "POST":
        suggestion_username = conditional_escape(request.POST.get('suggestion_username', ''))
        suggestion_subject = conditional_escape(request.POST.get('suggestion_subject', ''))
        suggestion_message = conditional_escape(request.POST.get('suggestion_message', ''))

        if suggestion_username and suggestion_subject and suggestion_message:
            send_suggestion_email(suggestion_username, suggestion_subject, suggestion_message)

    return render(request, 'index/about.html', {'login': login, 'username': name, 'user': user})

@requires_csrf_token
def page_not_found(request, exception):
    return render(request, 'login/404.html')
