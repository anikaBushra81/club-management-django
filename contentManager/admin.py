from django.contrib import admin
from .models import *

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1  # Show one empty attachment field by default

class PostAdmin(admin.ModelAdmin):
    inlines = [AttachmentInline]
    list_display = ('id', 'user', 'title', 'content', 'created_at', 'attachment_paths')

    def attachment_paths(self, obj):
        attachments = Attachment.objects.filter(post=obj)
        return ', '.join([attachment.file.name for attachment in attachments])
    attachment_paths.short_description = 'Attachment Paths'
     
admin.site.register(PostBlog, PostAdmin)


class SliderAdmin(admin.ModelAdmin):
    list_display = ('smallText', 'img', 'title',)
admin.site.register(Sliders, SliderAdmin) 