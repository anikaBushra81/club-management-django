from accounts.models import UserProfile, UsersRole


def generateRoleSession(req):
    urs = UsersRole.objects.filter(user=req.user).first()
    if (urs is None) and (not req.user.is_superuser):
        role = 'Null'
    elif req.user.is_superuser:
        role = 'Admin'
    else:
        count=0
        role = ""
        urs = UsersRole.objects.filter(user=req.user)
        for ur in urs:            
            if count>0:
                role = role+", "+ur.display_user_role
            else:
                role = role+ur.display_user_role
                count+=1
    return role

def user_data(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            profile_picture = "/static/images/pfp.jpg"
            utype=''
            uid = ''
        else:
            profile = UserProfile.objects.filter(user = request.user).first()
            profile_picture = profile.profile_picture.url
            utype = profile.user_type
            if utype == 'student':
                uid = profile.student_id
            else:
                uid = profile.official_id
        role = generateRoleSession(request)
    
    else:
        profile_picture = None
        role = None
        utype = ''
        uid = ''
    return {
        'profile_picture': profile_picture,
        'role': role,
        'user_type':utype,
        'uid':uid,
    }