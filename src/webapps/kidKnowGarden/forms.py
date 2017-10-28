from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20)
    email = forms.EmailField(max_length=200)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    password1 = forms.CharField(max_length=30,
                                label='Password',
                                widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=30,
                                label='Confirm Password',
                                widget=forms.PasswordInput)

    def clean(self):
        clean_data = super(RegisterForm, self).clean()

        password1 = clean_data.get('password1')
        password2 = clean_data.get('password2')

        if password1 and password2 and password1 != password2:
            msg = "Passwords did not match."
            self.add_error('password1', msg)
            self.add_error('password2', msg)
            raise forms.ValidationError(msg)

        return clean_data

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        return username