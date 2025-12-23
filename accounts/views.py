from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from .forms import SignUpForm

User = get_user_model()

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            form.save()
            
            if 'form_errors' in request.session:
                del request.session['form_errors']
            if 'form_data' in request.session:
                del request.session['form_data']
            
            messages.success(request, "Your account has been created. You can now log in.")
            return redirect('sign_in')
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

    return render(request, 'sign_up.html', {'form': form})


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

    return render(request, 'sign_in.html')

def sign_out(request):
    logout(request)
    return redirect('index')