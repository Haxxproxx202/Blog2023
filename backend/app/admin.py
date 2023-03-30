from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostModel(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'created', 'status')
