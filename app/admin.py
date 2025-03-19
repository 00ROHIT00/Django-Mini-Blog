from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, BlogPost

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'created_at')
    search_fields = ('username', 'email')
    ordering = ('-created_at',)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'author')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
