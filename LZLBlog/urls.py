"""LZLBlog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import GenericSitemap
from .sitemaps import IndexSitemap, LoginSitemap, ListSitemap
from django.conf import settings
from login import views
from blog.models import Blog
from login.models import User

blog_info_dict = {
    'queryset': Blog.objects.filter(status=1),
    'date_field': 'c_time',
}

user_info_dict = {
    'queryset': User.objects.all(),
    'date_field': 'c_time',
}

sitemaps = {
    'blog': GenericSitemap(blog_info_dict, priority=0.7),
    'index': IndexSitemap,
    'list': ListSitemap,
    'user_index': GenericSitemap(user_info_dict, priority=0.5),
    'login': LoginSitemap
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include('login.urls')),
    path('index/', include('index.urls')),
    path('blogs/', include('blog.urls')),
    path('works/', include('work.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = views.page_not_found
