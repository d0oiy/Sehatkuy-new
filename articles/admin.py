from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'views_count', 'created_at')
    list_filter = ('is_published', 'created_at', 'author')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Informasi Artikel', {
            'fields': ('title', 'slug', 'excerpt', 'image')
        }),
        ('Konten', {
            'fields': ('content',)
        }),
        ('Pengaturan', {
            'fields': ('author', 'is_published', 'views_count')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
