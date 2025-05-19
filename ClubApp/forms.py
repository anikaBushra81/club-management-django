
from django import forms

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=100)
