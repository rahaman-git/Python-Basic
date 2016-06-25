from django.contrib import admin

# Register your models here.
from .models import Comment


class CommentModelAdmin(admin.ModelAdmin):
    list_display = ["content", "id"]

admin.site.register(Comment, CommentModelAdmin)
