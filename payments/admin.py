from django.contrib import admin
from .models import *


# Register models here.
class MemberFeeAdminView(admin.ModelAdmin):
    list_display=['id', 'u_type', 'fee']
admin.site.register(MemberFee, MemberFeeAdminView)

class PaymentRecordAdminView(admin.ModelAdmin):
    list_display=['user', 'user_type','payment_id', 'amount', 'statement', 'created_at' ]
admin.site.register(PaymentRecord, PaymentRecordAdminView)

# Register models here.
class MonthlyFeeAdminView(admin.ModelAdmin):
    list_display=['user', 'user_type', 'month', 'amount_due', 'is_paid']
admin.site.register(MonthlyFee, MonthlyFeeAdminView)