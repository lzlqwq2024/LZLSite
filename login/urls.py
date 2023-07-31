from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('logout/', views.logout, name="logout"),
    path('reset/', views.reset, name="reset"),
    path('confirm/', views.user_confirm, name="confirm"),
    path('resetpassword/', views.resetpassword, name="resetpassword"),
    path('index/<slug:name>/', views.index, name="user_index"),
    path('upload_image/', views.upload_image),
]