from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from accounts.models import *
from contentManager.models import Sliders, PostBlog 
from payments.models import *

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from datetime import timedelta
from django.utils import timezone
import json

from django.conf import settings
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from payments.views import *
import warnings


warnings.filterwarnings('ignore')

@login_required(login_url='/login/')
def homePage(request):
    slider = Sliders.objects.all()
    posts = PostBlog.objects.all().order_by('-created_at')
    paginator = Paginator(posts, 5)
    
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if page_number is None:
        page_number=1
    info = {
        'title' : 'KyauClub',
        'page_obj': page_obj,
        'slider': slider,
        'has_next': True if int(page_number) <= int(paginator.num_pages) else False,
        }
    # if request.is_ajax():   # ei command ta django 4.0  te bilupto hoye gese. etar bodole nicherta
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'partials/post_list.html', info)
    return render(request, 'index.html', info)


@login_required(login_url='/login/')
def aboutUs(request):
    data = {
        'title': 'About Us',
    }
    return render(request, 'aboutUs.html', data)


@login_required(login_url='/login/')
def profile_card(request):
    profile = UserProfile.objects.filter(user = request.user).first()
    
    if request.method == "POST":
        pfp = False
        if 'profile_picture' in request.FILES:
            pfp = request.FILES['profile_picture']
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        
        # Check if the email is already in use by another user
        if request.user.email != email:
            if User.objects.filter(email=email).exclude(username=request.user.username).exists():
                error_msg = "Email already exists. Please choose a different email."
                data = {'error_msg': error_msg}
                # return HttpResponse(json.dumps(data), content_type='application/json')
                return JsonResponse(data)
                
        if profile is not None:
            upUser = User.objects.get(username=request.user)
            upUser.first_name=fname
            upUser.last_name=lname
            upUser.email=email
            upUser.save()
            if pfp :
                profile.profile_picture = pfp
            profile.phone=phone
            profile.save()
            request.session['profile_picture'] = profile.profile_picture.url
        return JsonResponse({'success': True})
    return render(request, 'profile_card.html', {'profile':profile, 'title':'Profile'})


def denied_access(request):
    return render(request, 'denied_page.html')



def signup(request):
    data = {
            'title': 'Signup',
        }
    if request.user.is_authenticated:
        return redirect('/')
    return render(request, 'signup.html', data)


def submission(request):
    try:
        if request.method == 'POST':
            pfp = request.FILES['profile_picture']
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            uname = request.POST.get('username')
            email = request.POST.get('email')
            pwd = request.POST.get('password')
            phone = request.POST.get('phone')
            blood_group = request.POST.get('blood_group')
            utype = request.POST.get('user_type')
            student_id = request.POST.get('student_id')
            batch = request.POST.get('batch')
            official_id = request.POST.get('official_id')
            designation = request.POST.get('designation')
            
            data = {
                    'title': 'Signup',
                    'fname':fname,
                    'lname':lname,
                    'user_type': utype,
                    'uname':uname,
                    'email':email,
                    'phone': phone,
                    'blood_group': blood_group,                   
                    }
            if User.objects.filter(username = uname).exists():
                data['error'] = 'uname'
                data['error_msg'] = "*Username already exist"
                return render(request, 'signup.html', data)
            
            if User.objects.filter(email = email).exists():
                data['error'] = 'email'
                data['error_msg'] = "*email already exist. Try another one"
                return render(request, 'signup.html', data)
            
            if student_id:
                if UserProfile.objects.filter(student_id = student_id).exists() or UserProfile.objects.filter(official_id = student_id).exists():
                    data['error'] = 'student'
                    data['error_msg'] = "*Student ID already exist"
                    data['student_id'] = student_id
                    data['batch'] = batch
                    return render(request, 'signup.html', data)
                
            elif official_id:
                if UserProfile.objects.filter(student_id = official_id).exists() or UserProfile.objects.filter(official_id = official_id).exists():
                    data['error'] = 'official'
                    data['error_msg'] = "*Official ID already exist"
                    data['official_id'] = official_id
                    data['designation'] = designation
                    return render(request, 'signup.html', data)
            
            user = User.objects.create_user(username=uname, email=email, password=pwd, first_name=fname, last_name=lname)
            if utype == 'student':
                profile = UserProfile.objects.create(
                    user = user,
                    user_type = utype,
                    phone = phone,
                    blood_group = blood_group,
                    student_id = student_id,
                    batch = batch
                    )
            else:
                profile = UserProfile.objects.create(
                    user = user,
                    user_type = utype,
                    phone = phone,
                    blood_group = blood_group,
                    official_id = official_id,
                    designation = designation
                    )
            
            if pfp :
                profile.profile_picture = pfp
            profile.save()
            messages.success(request, "Registration successfull. Login to your account !")
            return redirect("/login/")
        else:
            return redirect('/signup/')
    except Exception as e:
        return HttpResponse("Error occurred: {}".format(e))


def logging(request): 
    data = {
            'title': 'Login',
        }
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        utype = request.POST.get('user_type')
        student_id = request.POST.get('student_id')
        official_id = request.POST.get('official_id')
        pwd = request.POST.get('password')        
        if utype == 'student':
            if UserProfile.objects.filter(student_id = student_id).exists():
                uprofile = UserProfile.objects.get(student_id = student_id)
                username = uprofile.user
                user = authenticate(username = username, password = pwd)
                if user is None:
                    data['user_type'] = utype
                    data['student_id'] = student_id
                    messages.error(request, "*Invalid Password")
                    return render(request, 'login.html', data)
                else:                    
                    login(request, user)
                    profile =  UserProfile.objects.get(user=user)
                    request.session['profile_picture'] = profile.profile_picture.url
                    request.session['utype'] = profile.user_type
                    request.session['uid'] = profile.student_id
                    # generateRoleSession(request)
                    return redirect('/')
            else:
                data['user_type'] = utype
                data['student_id'] = student_id
                messages.error(request, "*Invalid Student ID")
                return render(request, 'login.html', data)
            
        elif utype == 'official':
            if UserProfile.objects.filter(official_id = official_id).exists():
                uprofile = UserProfile.objects.get(official_id = official_id)
                username = uprofile.user
                user = authenticate(username = username, password = pwd)
                if user is None:
                    data['user_type'] = utype
                    data['official_id'] = official_id
                    messages.error(request, "*Invalid Password")
                    return render(request, 'login.html', data)
                else:
                    login(request, user)
                    profile =  UserProfile.objects.get(user=user)
                    request.session['profile_picture'] = profile.profile_picture.url
                    request.session['utype'] = profile.user_type
                    request.session['uid'] = profile.official_id
                    # generateRoleSession(request)
                    return redirect('/')
            else:
                data['user_type'] = utype
                data['official_id'] = official_id
                messages.error(request, "*Invalid Official ID")
                return render(request, 'login.html', data)
    return render(request, 'login.html', data)


def log_out(request):
    if request.user.is_authenticated:
        request.session.flush()
        logout(request)
        return redirect(f'/login/?logged_out={True}')
    else:
        return redirect("/login/")
    
    
# forget password functionality  
TOKEN_EXPIRY_DURATION = timedelta(minutes=2)

def reset_password_request(request):
    if request.method == "GET":        
        referrer = request.META.get('HTTP_REFERER')
        if not referrer:
            if request.user.is_authenticated:
                return redirect('/')
            messages.error(request, "Access denied! Please use the forget password option from the login page.")
            return redirect('/login/')
        return render(request, 'forgot_password.html')
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        user = User.objects.filter(username=uname).first()
        if user :
            if(user.email == str(email)):
                try:
                    uprofile = UserProfile.objects.get(user = user.pk)
                    uprofile.password_reset_token_created = timezone.now()
                    uprofile.save()
                    # Generate user primary key's hash
                    uidb64 = force_str(urlsafe_base64_encode(force_bytes(user.pk)))
                    # Generate unique token
                    token = default_token_generator.make_token(user)
                    # Create reset link        
                    reset_link = request.build_absolute_uri(reverse('reset_password', kwargs={'token': token, 'uidb64': uidb64}))
                    # Send reset email
                    subject = 'Reset your password'
                    message = render_to_string('reset_password_email.html', {'user': user, 'reset_link': reset_link})
                    send_mail(subject, message, 'riadeb44985@gmail.com', [user.email], html_message=message)
                    messages.success(request, 'Password reset link sent to your email.')
                    return redirect('forgot_password')
                except:
                    messages.error(request, 'Something went wrong...')
            else:
                messages.error(request, '*Invalid email address.')
        else:
            messages.error(request, '*Invalid username.')
    return render(request, 'forgot_password.html')


def reset_password(request, token, uidb64):
    if request.user.is_authenticated:
        return redirect('/')
    userpk = urlsafe_base64_decode(uidb64).decode()
    user = User.objects.filter(pk=eval(userpk)).first()
    uprofile = UserProfile.objects.get(user=user.pk)
    if user and default_token_generator.check_token(user, token):
        if (uprofile.password_reset_token_created + TOKEN_EXPIRY_DURATION) < timezone.now():
            messages.error(request, 'Password reset link has expired. Please request a new one.')
            return redirect('forgot_password')
    else:
        messages.error(request, 'Invalid reset link.')
        return redirect('forgot_password')
    if request.method == 'POST':
        new_password = request.POST.get('new_password')        
        user.set_password(new_password)
        user.save()
        messages.success(request, 'Password reset successfully.')
        return redirect('login')    
    return render(request, 'reset_password.html', {'token': token, 'uidb64': uidb64})





def admin_required(user):
    return user.is_superuser
@user_passes_test(admin_required, login_url='/denied-access/')
def userRoleCrud(request):
    usr = UsersRole.objects.all()
    if request.method == 'POST':
        par = request.GET.get('key')
        if par=='src':
            data = json.loads((request.body).decode('utf-8'))
            st_user = UserProfile.objects.filter(student_id = data['uid']).first()
            ofi_user = UserProfile.objects.filter(official_id = data['uid']).first()
            if st_user:
                user_profile = st_user
            elif ofi_user:
                user_profile = ofi_user
            else:
                search_response = {
                'error_msg': "*Id not found !",
                }
                return HttpResponse(json.dumps(search_response), content_type='application/json')
            search_response = {
                'uname': user_profile.user.username,
                'user_type': user_profile.user_type,
                'email': user_profile.user.email
            }
            return HttpResponse(json.dumps(search_response), content_type='application/json')
        elif par=='res':
            data = json.loads((request.body).decode('utf-8'))
            role = data['user_role']
            user_id = data['uid']
            #
            st_user = UserProfile.objects.filter(student_id = user_id).first()
            ofi_user = UserProfile.objects.filter(official_id = user_id).first()
            if st_user:
                user_profile = st_user.user
            elif ofi_user:
                user_profile = ofi_user.user
            else:
                search_response = {
                'res_msg': "Id not found !",
                }
                return HttpResponse(json.dumps(search_response), content_type='application/json')

            # Update or create UserRoleSelect object for the user
            try:
                usr, created = UsersRole.objects.get_or_create(user_role = role, user = user_profile)            
                usr.uid = ''
                usr.save()
            except:
                usr, created = UsersRole.objects.get_or_create(user_role = role)
                usr.user = user_profile
                usr.uid = ''
                usr.save()

            # Show success or error message
            if created:
                res_msg = f"User: '{user_profile.username}' assigned as '{usr.display_user_role}' successfully."
            else:
                res_msg = f"New '{usr.display_user_role}' updated to '{user_profile.username}' successfully."
            search_response = {
                'res_msg': res_msg,
                }
            return HttpResponse(json.dumps(search_response), content_type='application/json')
        
        elif par=='del':
            user_role = request.POST.get('user_role')
            usr = UsersRole.objects.get(user_role=user_role)
            usr.delete()
            usr = UsersRole.objects.all()
            # return render(request, 'user_role_crud.html', {'userRoles' : usr})
            return redirect('/select-role/')
        
    return render(request, 'user_role_crud.html', {'userRoles' : usr})



@login_required(login_url='/login/')
def pay_choice(request):
    profile = UserProfile.objects.get(user=request.user)
    membFee = MemberFee.objects.get(u_type=profile.user_type)
    return render(request, 'pay_choice.html', {'memberFee':membFee})



stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

@csrf_exempt
def create_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Create a PaymentIntent with the order amount and currency
            intent = stripe.PaymentIntent.create(
                amount=int(data['amount'])*100,
                currency='usd',
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return HttpResponseBadRequest(json.dumps({'error': str(e)}), content_type='application/json')
    else:
        return redirect('/pay-choice')



def checkout(request):
    if request.method == "POST":
        amount = request.POST.get('amount')
        statement = request.POST.get('statement')
        user_type = request.POST.get('user_type')
        return render(request, 'checkout.html', {
            'stripe_pub_key': settings.STRIPE_TEST_PUBLIC_KEY,
            'amount':amount,
            'statement':statement,
        })
    # below for 'GET' req
    else:
        payment_intent_id = request.GET.get('payment_intent')
        user_type = request.GET.get('user_type')
        try:
            paymentIntent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if paymentIntent.status == "succeeded":
                if PaymentRecord.objects.filter(payment_id = paymentIntent.id).exists():
                    key = force_str(urlsafe_base64_encode(force_bytes(paymentIntent.id)))
                    return redirect(reverse('payment_status',kwargs={'status':'1', 'key':key}))
                
                # data entry to PaymentRecord table
                payrecord = PaymentRecord.objects.create(
                                                        user=request.user,
                                                        user_type = str(user_type),
                                                        payment_id = paymentIntent.id,
                                                        amount = int(paymentIntent.amount)/100,
                                                        statement = f"{user_type} fee",
                                                        )
                payrecord.save()
                record_month_payment(
                                    request.user, str(user_type), 
                                    date.today().replace(day=1), 
                                    int(paymentIntent.amount)/100
                                    )
                key = force_str(urlsafe_base64_encode(force_bytes(paymentIntent.id)))
                return redirect(reverse('payment_status',kwargs={'status':'1', 'key':key}))
            
            else:
                return redirect(reverse('payment_status',kwargs={'status':'0', 'key':'error'}))
            
        except Exception as e:
            return HttpResponse("The Page is not directly accessible...")
        

def pay_status(request, status, key):
    if status == '1' and (key != 'error'):
        try:
            pay_id = urlsafe_base64_decode(key).decode()
        except:
            return HttpResponse('Countered an error while fetching status...')        
        return render(request, 'payment_success.html', {'pay_id':pay_id})
    elif status == '0' and (key=='error'):
        return render(request, 'payment_error.html')
    else:
        return HttpResponse('Countered an error while fetching status...') 
    
