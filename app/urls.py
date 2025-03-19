from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('clear-welcome-toast/', views.clear_welcome_toast, name='clear_welcome_toast'),
    path('blog/blogs/', views.blog_list, name='blog_list'),
    path('blog/post/<int:post_id>/', views.blog_detail, name='blog_detail'),
    path('blog/blogger/<int:author_id>/', views.blogger_detail, name='blogger_detail'),
] 