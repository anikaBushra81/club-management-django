from django.db import models
from django.conf import settings
from datetime import date
from django.utils import timezone
import datetime



class MemberFee(models.Model):
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('official', 'Official'),
    ]
    id = models.AutoField(primary_key=True)
    u_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, unique=True)
    fee = models.IntegerField(default=0)
    
    def __str__(self) -> str:
        return self.u_type
    
class PaymentRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=15)
    payment_id = models.CharField(max_length=100, unique=True)  
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    statement = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.created_at:
            # Get current UTC time
            utc_now = timezone.now()
            # Convert UTC time to Dhaka time (GMT +6:00)
            dhaka_time = utc_now + timezone.timedelta(hours=6)
            self.created_at = dhaka_time
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Payment {self.payment_id} - {self.user}'
    
    
class MonthlyFee(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=15)
    month = models.DateField(default=date.today().replace(day=1))
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id:  # Only set the default value for new records
            member_fee = MemberFee.objects.filter(u_type=self.user_type).first()
            if member_fee:
                self.amount_due = member_fee.fee
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} - {self.month.strftime("%B %Y")}'

