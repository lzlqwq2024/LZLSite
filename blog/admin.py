from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.Category)
admin.site.register(models.Tag)
admin.site.register(models.Comment)

@admin.register(models.Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'desc', 'content', 'status', 'category', 'show_tag', 'owner']
    
    def show_tag(self, obj):
        return [tag.name for tag in obj.tag.all()]
    
    filter_horizontal = ('tag',)

