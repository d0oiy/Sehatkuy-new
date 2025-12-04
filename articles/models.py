from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="Judul")
    slug = models.SlugField(unique=True, max_length=200)
    content = models.TextField(verbose_name="Konten")
    image = models.ImageField(upload_to='articles/', blank=True, null=True, verbose_name="Gambar")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name="Penulis"
    )
    excerpt = models.TextField(max_length=300, blank=True, help_text="Ringkasan artikel (opsional)")
    is_published = models.BooleanField(default=True, verbose_name="Diterbitkan")
    views_count = models.IntegerField(default=0, verbose_name="Jumlah Dilihat")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Artikel"
        verbose_name_plural = "Artikel"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('articles:detail', kwargs={'slug': self.slug})

    def increment_views(self):
        """Tambah jumlah views"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
