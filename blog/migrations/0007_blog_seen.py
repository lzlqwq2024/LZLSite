# Generated by Django 4.2 on 2023-07-15 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_alter_blog_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='seen',
            field=models.PositiveIntegerField(default=0, verbose_name='展现量'),
        ),
    ]
