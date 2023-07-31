from django.db import models
from login.models import User
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='名称')
    color = models.CharField(max_length=50, default="#2655cc", verbose_name='颜色')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'

class Tag(models.Model):
    name = models.CharField(max_length=10, verbose_name='名称')
    color = models.CharField(max_length=50, default="#2655cc", verbose_name='颜色')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'

class Blog(models.Model):
    STATUS_NORMAL = 1
    STATUS_DRAFT = 2
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DRAFT, '草稿'),
    )

    title = models.CharField(max_length=255, verbose_name='标题')
    desc = models.CharField(max_length=1024, null=True, blank=True, verbose_name='摘要')
    cover = ProcessedImageField(upload_to='blog/cover', default="blog/cover/default_cover.png", processors=[ResizeToFill(350,300)])
    content = models.TextField(verbose_name='正文')
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name='状态')
    seen = models.IntegerField(default=0, verbose_name='阅读量')
    love = models.IntegerField(default=0, verbose_name='点赞数')
    comment_num = models.IntegerField(default=0, verbose_name='评论数')
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.SET_NULL, null=True, blank=True)
    tag = models.ManyToManyField(Tag, verbose_name='标签', blank=True)
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return "/blogs/blog/{}/".format(self.id)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-id']

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='用户')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True, blank=True, verbose_name='博客')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='父评论')
    child_comment = models.TextField(null=True, blank=True, verbose_name='子评论')
    text = models.TextField(verbose_name='内容')
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return "By %s On %s：%s" %(self.user, str(self.c_time), self.text)

    class Meta:
        ordering = ["c_time"]
        verbose_name = "评论"
        verbose_name_plural = "评论"
