# Generated by Django 5.0.4 on 2024-05-05 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_usersrole_delete_userrole'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersrole',
            name='user_role',
            field=models.CharField(choices=[('vice_president', 'Vice President'), ('treasurer', 'Treasurer'), ('general_secretary', 'General Secretary')], max_length=25, unique=True),
        ),
    ]
