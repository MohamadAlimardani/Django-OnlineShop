from django import forms
from django.contrib.auth import get_user_model
from .validators import (
    first_name_validator, 
    last_name_validator, 
    username_validator, 
    password_validator
)

User = get_user_model()

class SignUpForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Password'})
        }

    def clean_first_name(self):
        f_name = self.cleaned_data.get('first_name')
        errors = first_name_validator(f_name)
        if errors:
            raise forms.ValidationError(errors)
        return f_name

    def clean_last_name(self):
        l_name = self.cleaned_data.get('last_name')
        errors = last_name_validator(l_name)
        if errors:
            raise forms.ValidationError(errors)
        return l_name

    def clean_username(self):
        username = self.cleaned_data.get('username')
        errors = username_validator(username)
        if User.objects.filter(username=username).exists():
            errors.append("Username already exists")
        if errors:
            raise forms.ValidationError(errors)
        return username

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
