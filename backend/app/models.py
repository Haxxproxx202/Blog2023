from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

CustomUser = settings.AUTH_USER_MODEL

# Manager poza klasą Post
# class PublishedManager(models.Manager):
#     def get_queryset(self):
#         return super(PublishedManager, self).get_queryset().filter(status='published')


class Post(models.Model):
    class PublishedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(status='published')

    STATUS_CHOICES = (
        ('draft', "Draft"),
        ('published', 'Published'),
    )
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique_for_date='publish')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blog_posts')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ('-publish', )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('app:post_detail',
                       args=[self.publish.year,
                             self.publish.strftime('%m'),
                             self.publish.strftime('%d'),
                             self.slug])


