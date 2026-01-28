from django import forms
from django.contrib.auth import get_user_model
from .validators import *
from .models import OtpCode

User = get_user_model()

def normalize_ir_mobile(phone_number: str) -> str | None:
    phone_number = (phone_number or "").strip()

    if re.fullmatch(r"9\d{9}", phone_number):          # 912xxx6789
        return "0" + phone_number                      # -> 0912xxx6789

    if re.fullmatch(r"09\d{9}", phone_number):         # 0912xxx6789
        return phone_number

    if re.fullmatch(r"\+98\d{10}", phone_number):      # +98912xxx6789
        return "0" + phone_number[3:]                  # -> 0912xxx6789

    if re.fullmatch(r"98\d{10}", phone_number):        # 98912xxx6789
        return "0" + phone_number[2:]                  # -> 0912xxx6789

    return None

class SignUpForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username','phone_number', 'email', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Password'})
        }

    def clean_first_name(self):
        f_name = self.cleaned_data.get('first_name').capitalize()
        errors = first_name_validator(f_name)
        if errors:
            raise forms.ValidationError(errors)
        return f_name

    def clean_last_name(self):
        l_name = self.cleaned_data.get('last_name').capitalize()
        errors = last_name_validator(l_name)
        if errors:
            raise forms.ValidationError(errors)
        return l_name

    def clean_username(self):
        username = self.cleaned_data.get('username')
        errors = username_validator(username)
        if User.objects.filter(username=username).exists():
            errors.append("Username already exists.")
        if errors:
            raise forms.ValidationError(errors)
        return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        errors = phone_number_validator(phone_number)
        # if User.objects.filter(phone_number=phone_number).exists():
        #     raise forms.ValidationError("Phone number already exists.")
        if errors:
            raise forms.ValidationError(errors)
        return normalize_ir_mobile(phone_number)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean_password(self):
        pw = self.cleaned_data.get('password')
        errors = password_validator(pw)
        if errors:
            raise forms.ValidationError(errors)
        return pw

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match.")
        
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class OtpForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Verification Code'})
    )
