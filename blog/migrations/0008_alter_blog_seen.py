# Generated by Django 4.2 on 2023-07-15 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_blog_seen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='seen',
            field=models.IntegerField(default=0, verbose_name='展现量'),
        ),
    ]
