from django.urls import path
from . import views

urlpatterns = [
    path('blog/<int:blog_id>/', views.blog, name="blog"),
    path('category/<int:category_id>/<int:request_page>/', views.category, name="category"),
    path('list/<int:request_page>/', views.list, name="list"),
    path('blog/<int:blog_id>/reply/<int:comment_id>/', views.comment_reply, name="comment"),
    path('write/', views.write, name="write"),
    path('update/<int:blog_id>/', views.update, name="update"),
    path('manage/<int:request_page>/', views.manage, name="manage"),
    path('update_category_and_tag/', views.update_category_and_tag, name="update_ct"),
    path('upload_image/', views.upload_image)
]