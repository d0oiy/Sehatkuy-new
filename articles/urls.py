from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    # Public views
    path('', views.article_list, name='list'),
    path('<slug:slug>/', views.article_detail, name='detail'),
    
    # Admin views
    path('admin/', views.article_admin_list, name='admin_list'),
    path('admin/create/', views.article_create, name='admin_create'),
    path('admin/<int:article_id>/edit/', views.article_edit, name='admin_edit'),
    path('admin/<int:article_id>/delete/', views.article_delete, name='admin_delete'),
]

