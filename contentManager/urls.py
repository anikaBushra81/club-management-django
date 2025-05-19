from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from contentManager import views


urlpatterns = [
    path('feedsMain/', views.show_post, name='feedsMain'),
    path('feeds/', views.post_list, name='feeds'),
    path('upload/', views.add_post, name='upload'),
]
