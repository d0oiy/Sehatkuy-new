from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Article
from .forms import ArticleForm


def is_admin(user):
    """Check if user is admin"""
    return user.is_superuser or getattr(user, 'role', None) == 'admin'


@user_passes_test(is_admin)
@login_required
def article_create(request):
    """Admin: Buat artikel baru"""
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, f'Artikel "{article.title}" berhasil dibuat!')
            return redirect('articles:admin_list')
    else:
        form = ArticleForm()
    
    return render(request, 'articles/admin/article_form.html', {
        'form': form,
        'title': 'Buat Artikel Baru'
    })


@user_passes_test(is_admin)
@login_required
def article_edit(request, article_id):
    """Admin: Edit artikel"""
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, f'Artikel "{article.title}" berhasil diperbarui!')
            return redirect('articles:admin_list')
    else:
        form = ArticleForm(instance=article)
    
    return render(request, 'articles/admin/article_form.html', {
        'form': form,
        'article': article,
        'title': f'Edit: {article.title}'
    })


@user_passes_test(is_admin)
@login_required
def article_delete(request, article_id):
    """Admin: Hapus artikel"""
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        title = article.title
        article.delete()
        messages.success(request, f'Artikel "{title}" berhasil dihapus!')
        return redirect('articles:admin_list')
    
    return render(request, 'articles/admin/article_confirm_delete.html', {
        'article': article
    })


@user_passes_test(is_admin)
@login_required
def article_admin_list(request):
    """Admin: Daftar semua artikel"""
    articles = Article.objects.all().order_by('-created_at')
    
    # Filter
    search = request.GET.get('search', '')
    if search:
        articles = articles.filter(Q(title__icontains=search) | Q(content__icontains=search))
    
    published_filter = request.GET.get('published', '')
    if published_filter == 'yes':
        articles = articles.filter(is_published=True)
    elif published_filter == 'no':
        articles = articles.filter(is_published=False)
    
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'articles/admin/article_list.html', {
        'articles': page_obj,
        'search': search,
        'published_filter': published_filter,
    })


def article_list(request):
    """Daftar artikel untuk publik"""
    articles = Article.objects.filter(is_published=True).order_by('-created_at')
    
    # Search
    search = request.GET.get('search', '')
    if search:
        articles = articles.filter(Q(title__icontains=search) | Q(content__icontains=search) | Q(excerpt__icontains=search))
    
    paginator = Paginator(articles, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'articles/article_list.html', {
        'articles': page_obj,
        'search': search,
    })


def article_detail(request, slug):
    """Detail artikel"""
    article = get_object_or_404(Article, slug=slug, is_published=True)
    
    # Increment views
    article.increment_views()
    
    # Artikel terkait (3 artikel terbaru selain artikel ini)
    related_articles = Article.objects.filter(
        is_published=True
    ).exclude(id=article.id).order_by('-created_at')[:3]
    
    return render(request, 'articles/article_detail.html', {
        'article': article,
        'related_articles': related_articles,
    })
