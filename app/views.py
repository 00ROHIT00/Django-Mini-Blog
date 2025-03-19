from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import User, BlogPost, Comment
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.db import models

# Create your views here.

def home(request):
    # Get latest 3 blog posts
    latest_posts = BlogPost.objects.all()[:3]
    
    # Get active bloggers (users who have posted in the last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    active_bloggers = User.objects.filter(
        blog_posts__created_at__gte=thirty_days_ago
    ).annotate(
        last_post_date=models.Max('blog_posts__created_at')
    ).distinct().order_by('-last_post_date')[:5]
    
    return render(request, 'index.html', {
        'latest_posts': latest_posts,
        'active_bloggers': active_bloggers
    })

def about(request):
    return render(request, 'about.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']
        full_name = request.POST['full_name']
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register')
        
        # Split full name into first and last name
        name_parts = full_name.split(maxsplit=1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password1
        )
        login(request, user)
        messages.success(request, 'Registration successful!')
        return redirect('home')
    
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Set session variable to show welcome toast
            request.session['show_welcome_toast'] = True
            messages.success(request, 'Login successful!')
            
            # Check if there's a next URL to redirect to
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('home')

@require_POST
def clear_welcome_toast(request):
    if 'show_welcome_toast' in request.session:
        del request.session['show_welcome_toast']
    return JsonResponse({'status': 'success'})

def blog_list(request):
    posts = BlogPost.objects.all()
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    return render(request, 'blog_list.html', {'posts': posts})

def blog_detail(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    comments = post.comments.all()  # Comments are already ordered by created_at due to model Meta
    return render(request, 'blog_detail.html', {
        'post': post,
        'comments': comments
    })

@login_required
def create_comment(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(
                content=content,
                author=request.user,
                post=post
            )
            messages.success(request, 'Comment added successfully!')
            return redirect('blog_detail', post_id=post_id)
        else:
            messages.error(request, 'Comment cannot be empty.')
    
    return render(request, 'create_comment.html', {'post': post})

@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id
    
    # Check if user is the comment author or the blog post author
    if request.user == comment.author or request.user == comment.post.author:
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
    else:
        messages.error(request, 'You do not have permission to delete this comment.')
    
    return redirect('blog_detail', post_id=post_id)

def author_detail(request, author_id):
    author = get_object_or_404(User, id=author_id)
    posts = BlogPost.objects.filter(author=author)
    return render(request, 'author_detail.html', {'author': author, 'posts': posts})

def blogger_detail(request, author_id):
    author = get_object_or_404(User, id=author_id)
    posts = BlogPost.objects.filter(author=author).order_by('-created_at')
    return render(request, 'blogger_detail.html', {
        'author': author,
        'posts': posts
    })

def blogger_list(request):
    # Get all users who have published at least one blog post
    bloggers = User.objects.filter(blog_posts__isnull=False).distinct().order_by('username')
    return render(request, 'blogger_list.html', {'bloggers': bloggers})

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        
        if not title or not content:
            messages.error(request, 'Both title and content are required.')
            return redirect('create_post')
        
        post = BlogPost.objects.create(
            title=title,
            content=content,
            author=request.user
        )
        messages.success(request, 'Blog post created successfully!')
        return redirect('blog_detail', post_id=post.id)
    
    return render(request, 'create_post.html')
