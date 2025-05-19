from django.shortcuts import render
from django.core.paginator import Paginator
from datetime import timedelta
import datetime
from .models import *
import warnings
from decimal import Decimal


warnings.filterwarnings('ignore')

def has_cleared_month_fee(user, month):
    # current_month = date.today().replace(day=1)
    monthly_fee = MonthlyFee.objects.filter(user=user, month=month).first()
    
    if monthly_fee:
        return monthly_fee.is_paid
    return False



def record_month_payment(user, user_type, month, amount):
    amount = Decimal(amount)
    if amount <= 0:
        pass
    else:
        if has_cleared_month_fee(user, month) is False:        
            monthly_fee, created = MonthlyFee.objects.get_or_create(user=user, user_type=user_type, month=month)
            if monthly_fee.amount_due <= amount:
                amount = amount-monthly_fee.amount_due
                monthly_fee.amount_due = 0
                monthly_fee.is_paid = True
            else:
                monthly_fee.amount_due -= amount
                amount = 0
                if monthly_fee.amount_due == 0:
                    monthly_fee.is_paid = True
            monthly_fee.save()
        else:
            month = (month + timedelta(days=32)).replace(day=1)
        return record_month_payment(user, user_type, month, amount)
    

def user_transactions(request):
    payrecords = PaymentRecord.objects.filter(user = request.user).order_by('-created_at')
    paginator = Paginator(payrecords, 5)
    
    page_number = request.GET.get('page')
    transactions = paginator.get_page(page_number)
    return render(request, 'transactions.html', {"transactions":transactions})


def monthly_transactions(request):
    transactions_list = MonthlyFee.objects.filter(user=request.user).order_by('-month')
    paginator = Paginator(transactions_list, 15)

    page_number = request.GET.get('page')
    transactions = paginator.get_page(page_number)
    return render(request, 'monthly_transactions.html', {"transactions":transactions})


def print_monthly_transactions(request):
    transactions = MonthlyFee.objects.filter(user=request.user).order_by('-month')[:6]
    return render(request, "mon_trans_print.html", {"transactions":transactions, 'timeNow':datetime.datetime.now()})