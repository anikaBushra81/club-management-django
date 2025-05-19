from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from ClubApp import views
import payments

 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.logging, name='login'),
    path('logout/', views.log_out, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('submission/', views.submission, name='submission'),
    path('profile/', views.profile_card, name='profile'),
    path('', views.homePage, name='homePage'),
    path('about-us/', views.aboutUs, name='about'),
    path('forgot_password/', views.reset_password_request, name='forgot_password'),
    path('reset_password/<token>/<uidb64>/', views.reset_password, name='reset_password'),
    # path('select-role/', views.assign_role_to_users, name='select_role'),
    path('select-role/', views.userRoleCrud, name='select_role'),
    path('denied-access/', views.denied_access, name='denied_access'),
    path('content/', include('contentManager.urls')),
    # path('payment/', views.payment_view, name='payment'),
    path('pay-choice', views.pay_choice, name='pay_choice'),
    path('create_payment/', views.create_payment, name='create_payment'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment-status/<status>/<key>', views.pay_status, name='payment_status'),
    path('view-transactions/', payments.views.user_transactions, name='user_transactions'),
    path('monthly-transactions/', payments.views.monthly_transactions, name='monthly_transactions'),
    path('print-monthly-transactions/', payments.views.print_monthly_transactions, name='print_monthly_transactions'),
]

# The following line will work as long as the DEBUG is True. [DURING REAL TIME PRODUCTION use onno code]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
