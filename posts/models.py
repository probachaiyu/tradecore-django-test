from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='likes',
                             on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

class PostManager(models.Manager):
    def with_likes_count(self):
        return self.annotate(total_likes=F('likes'))

class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    likes = GenericRelation(Like, default=0)

    objects = PostManager()

    def __str__(self):
        return '{} - {}'.format(self.title, self.author)

    def comment_count(self):
        ct = ContentType.objects.get_for_model(Post)
        obj_pk = self.id
        return Like.objects.filter(content_type=ct, object_pk=obj_pk).count()

    @property
    def total_likes(self):
        return self.likes.count()