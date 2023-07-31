from django.db import models
from login.models import User
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

# Create your models here.

class Work(models.Model):

    title = models.CharField(max_length=255, verbose_name='标题')
    desc = models.CharField(max_length=1024, null=True, blank=True, verbose_name='摘要')
    cover = ProcessedImageField(upload_to='work/cover', default="blog/cover/default_cover.png", processors=[ResizeToFill(350,300)])
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    url = models.URLField(max_length=200, default="https://github.com/", verbose_name="链接")
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '作品'
        verbose_name_plural = '作品'
        ordering = ['-id']