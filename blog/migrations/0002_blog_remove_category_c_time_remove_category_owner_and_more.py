# Generated by Django 4.2 on 2023-07-12 06:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_user_no_comment'),
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='标题')),
                ('desc', models.CharField(blank=True, max_length=1024, verbose_name='摘要')),
                ('content', models.TextField(verbose_name='正文')),
                ('status', models.PositiveIntegerField(choices=[(1, '正常'), (0, '删除'), (2, '草稿')], default=1, verbose_name='状态')),
                ('c_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '文章',
                'verbose_name_plural': '文章',
                'ordering': ['-id'],
            },
        ),
        migrations.RemoveField(
            model_name='category',
            name='c_time',
        ),
        migrations.RemoveField(
            model_name='category',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='c_time',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='owner',
        ),
        migrations.DeleteModel(
            name='Article',
        ),
        migrations.AddField(
            model_name='blog',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.category', verbose_name='分类'),
        ),
        migrations.AddField(
            model_name='blog',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.user', verbose_name='作者'),
        ),
        migrations.AddField(
            model_name='blog',
            name='tag',
            field=models.ManyToManyField(to='blog.tag', verbose_name='标签'),
        ),
    ]