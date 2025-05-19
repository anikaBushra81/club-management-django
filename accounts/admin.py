from django.contrib import admin
from .models import *
# Register your models here.

class UserProfileAdminView(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'phone', 'blood_group', 'student_id', 'batch', 'official_id', 'designation', 'profile_picture', 'password_reset_token_created']

admin.site.register(UserProfile, UserProfileAdminView)


class UserRoleAdminView(admin.ModelAdmin):
    list_display = ['user_role', 'user', 'uid', 'user_type']
admin.site.register(UsersRole, UserRoleAdminView)