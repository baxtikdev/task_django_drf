from django import forms
from django.contrib.auth.forms import UserCreationForm

from common.users.models import User


class Login(forms.Form):
    phone = forms.CharField(label='Phone', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())


class Register(UserCreationForm):
    class Meta:
        model = User
        fields = ['phone', 'username', 'password1', 'password2']
