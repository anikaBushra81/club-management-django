# Generated by Django 5.0.4 on 2024-07-10 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_monthlyfee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentrecord',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]
