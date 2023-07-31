from django.urls import path
from . import views

urlpatterns = [
    path('list/<int:request_page>/', views.list, name="works"),
]