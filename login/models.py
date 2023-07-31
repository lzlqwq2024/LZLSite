from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    avatar = ProcessedImageField(upload_to='login/avatar', default="login/avatar/default_man.png", processors=[ResizeToFill(100,100)])
    c_time = models.DateTimeField(auto_now_add=True)
    has_confirmed = models.BooleanField(default=False)
    no_comment = models.BooleanField(default=False)
    loved_blog = models.TextField(null=True, blank=True)
    small_description = models.CharField(max_length=256, default="这个人很懒，什么都没有写~")
    big_detail = models.TextField(default="<p>这个人很懒，什么都没有写~</p>")

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return "/login/index/{}/".format(self.name)
    
    class Meta:
        ordering = ['-c_time']
        verbose_name = "用户"
        verbose_name_plural = "用户"

class ConfirmString(models.Model):
    code = models.CharField(max_length=256)
    tag = models.CharField(max_length=256, default="")
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name + ": " + self.code
    
    class Meta:
        ordering = ["-c_time"]
        verbose_name = "确认码"
        verbose_name_plural = "确认码"

class ResetString(models.Model):
    code = models.CharField(max_length=256)
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name + "：" + self.code

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "密码重置码"
        verbose_name_plural = "密码重置码"
