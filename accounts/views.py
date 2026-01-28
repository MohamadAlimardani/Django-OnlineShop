from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from .forms import SignUpForm, OtpForm
from .models import OtpCode
from utils import otputils
import random as rnd
from datetime import timedelta

User = get_user_model()

def generate_otp():
    return str(rnd.randint(100000, 999999))

def _get_pending_user(request):
    user_id = request.session.get('pending_user_id')
    if not user_id:
        return None
    return User.objects.filter(id=user_id).first()

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            OtpCode.objects.filter(user=user).delete()
            
            code = generate_otp()
            OtpCode.objects.create(user=user, code=code)
            otputils.send_Otp_Code(user.phone_number, code)
            
            request.session['pending_user_id'] = user.id
            
            if 'form_errors' in request.session:
                del request.session['form_errors']
            if 'form_data' in request.session:
                del request.session['form_data']
            
            messages.success(request, "Please Verify you're phone number.")
            return redirect('otp_verification')
        
        else:
            request.session['form_errors'] = form.errors.get_json_data()
            request.session['form_data'] = request.POST.dict()
            return redirect('sign_up')
    
    form_errors = request.session.pop('form_errors', None)
    form_data = request.session.pop('form_data', None)
    
    if form_errors and form_data:
        form = SignUpForm()
        
        form.data = form_data
        form.is_bound = True
        form.cleaned_data = {}
        
        form._errors = {}
        for field, error_list in form_errors.items():
            for error in error_list:
                form.add_error(field if field != '__all__' else None, error['message'])
    else:
        form = SignUpForm()

    return render(request, 'components/sign_up.html', {'form': form})

def otp_verification(request):
    user = _get_pending_user(request)
    if not user:
        messages.error(request, "No pending verification found. Please sign up again.")
        return redirect('sign_up')
    
    latest_otp = OtpCode.objects.filter(user=user).order_by('-created_at').first()
    
    cooldown = getattr(settings, "OTP_RESEND_COOLDOWN_SECONDS", 60)
    cooldown_left = 0
    if latest_otp:
        seconds_since_sent = (timezone.now() - latest_otp.created_at).total_seconds()
        cooldown_left = max(0, int(cooldown - seconds_since_sent))
    
    if request.method == 'POST':
        form = OtpForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            
            otp = OtpCode.objects.filter(user=user, code=code).order_by('-created_at').first()
            if not otp:
                messages.error(request, "Invalid verification code.")
                return redirect('otp_verification')
            
            expire_minutes = getattr(settings, "OTP_EXPIRE_MINUTES", 2)
            if timezone.now() > otp.created_at + timedelta(minutes=expire_minutes):
                otp.delete()
                messages.error(request, "Code expired. Please request a new code.")
                return redirect('otp_verification')
            
            user.is_active = True
            user.save()
            otp.delete()
            request.session.pop('pending_user_id', None)
                
            messages.success(request, 'You\'re account has been verified Successfully')
            return redirect('sign_in')
    
    else:
        form = OtpForm()
    
    return render(request, 'components/otp_verification.html', {
        'form': form, 
        'cooldown_left': cooldown_left
    })

def resend_otp(request):
    if request.method != 'POST':
        return redirect('otp_verification')
    
    user = _get_pending_user(request)
    if not user:
        messages.error(request, "No pending verification found. Please sign up again.")
        return redirect('otp_verification')
    
    now = timezone.now()
    
    cooldown = getattr(settings, "OTP_RESEND_COOLDOWN_SECONDS", 120)
    latest_otp = OtpCode.objects.filter(user=user).order_by('-created_at').first()
    
    if latest_otp and now < latest_otp.created_at + timedelta(seconds=cooldown):
        left = int((latest_otp.created_at + timedelta(seconds=cooldown) - now).total_seconds())
        messages.error(request, f"Please wait {left} seconds before resending.")
        return redirect('otp_verification')
    
    max_per_hour = getattr(settings, "OTP_MAX_RESENDS_PER_HOUR", 5)
    one_hour_ago = now - timedelta(hours=1)
    resend_count = OtpCode.objects.filter(user=user, created_at__gte=one_hour_ago).count()
    if resend_count >= max_per_hour:
        messages.error(request, "Too many resend attempts. Please try again later.")
        return redirect('otp_verification')
    
    OtpCode.objects.filter(user=user).delete()
    
    code = generate_otp()
    OtpCode.objects.create(user=user, code=code)
    otputils.send_Otp_Code(user.phone_number, code)
    
    messages.success(request, "A new verification code has been sent.")
    return redirect('otp_verification')
    

def sign_in(request):
    if request.method == 'POST':
        login_id = request.POST['login-identifier']
        password = request.POST['password']

        user = authenticate(request, username=login_id, password=password)

        if user is None:
            try:
                user_obj = User.objects.get(email=login_id)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user is not None:
            login(request, user)
            return redirect('index')

        messages.error(request, "Invalid username/email or password.")
        return redirect('sign_in')

    return render(request, 'components/sign_in.html')

def sign_out(request):
    logout(request)
    return redirect('index')
