from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile



class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('official', 'Official'), 
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=15)
    blood_group = models.CharField(max_length=5)
    student_id = models.CharField(max_length=20, null=True, blank=True)
    batch = models.CharField(max_length=10, null=True, blank=True)
    official_id = models.CharField(max_length=20, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    password_reset_token_created = models.DateTimeField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True, default='profile_pictures/def.jpg')

    def save(self, *args, **kwargs):
        if self.profile_picture:
            img = Image.open(self.profile_picture)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img = img.resize((400, 400))
            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=85)

            # Create a new Django-friendly file
            img_file = InMemoryUploadedFile(
                img_io,
                field_name=None,
                name=f"{self.profile_picture.name.split('.')[0]}.jpg",
                content_type='image/jpeg',
                size=img_io.tell(),
                charset=None
            )
            
            self.profile_picture = img_file

        # Call the real save method
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.user.username



class UsersRole(models.Model):
    USER_ROLE_CHOICES = [
        ('vice_president', _('Vice President')),
        ('treasurer', _('Treasurer')),
        ('general_secretary', _('General Secretary')),
    ]
    
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('official', 'Official'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_role = models.CharField(max_length=25, choices=USER_ROLE_CHOICES, unique=True)
    uid = models.CharField(max_length=20, blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.uid:
            # Fetch user_id from UserProfile
            upf = UserProfile.objects.get(user = self.user)
            if upf.official_id:
                self.uid = upf.official_id
                self.user_type = 'official'
            else:
                self.uid = upf.student_id
                self.user_type = 'student'
        super().save(*args, **kwargs)
         
    @property
    def display_user_role(self):
        return dict(self.USER_ROLE_CHOICES).get(self.user_role, 'Unknown')
    
    def __str__(self):
        return f'{self.user_role} - {self.display_user_role}'