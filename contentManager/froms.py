from django import forms
from .models import PostBlog, Attachment

class PostBlogForm(forms.ModelForm):
    class Meta:
        model = PostBlog
        fields = ['title', 'content']

class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file']
 