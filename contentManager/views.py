from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from .froms import *
from .models import *
from accounts.models import UsersRole

 
# Create your views here.
def show_post(request):
    posts = PostBlog.objects.all().order_by('-created_at')
    data = {
        "posts":posts,
    }
    return render(request, 'blogPost.html', context=data)

def post_list(request):
    posts = PostBlog.objects.all().order_by('-created_at')
    return render(request, 'feedsList.html', {'posts': posts})


# decorator's helping function
def role_req(user):
    # allowing only users who are listed in selected_role && admin
    allow = True
    urs = UsersRole.objects.filter(user=user).first()
    if (urs is None) and (not user.is_superuser):
        allow = False
    return allow
@login_required(login_url='/login/')
@user_passes_test(role_req, login_url='/denied-access/')
def add_post(request):
    if request.method == 'POST':
        post_form = PostBlogForm(request.POST)
        files = request.FILES.getlist('attachments')
        
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.user = request.user
            post.save()
            
            for file in files:
                Attachment.objects.create(post=post, file=file)
            
            return redirect('/')
    else:
        post_form = PostBlogForm()
        
    return render(request, 'contentPost.html', {'post_form': post_form})
