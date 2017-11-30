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


class ProfileForm(forms.Form):
    grade = forms.IntegerField(min_value=0, max_value=12)
    avatar = forms.ImageField(required=False)
    bio = forms.CharField(max_length=300, widget=forms.Textarea, required=False)

    def clean_grade(self):
        grade = self.cleaned_data.get('grade')

        if grade < 0:
            raise forms.ValidationError("Grade should be a positive Integer")
        if grade > 12:
            raise forms.ValidationError("Grade should be no larger than 12")
        return grade


class AnswerSubmitForm(forms.Form):
    """
    Django Form to check the submited answer
    """
    record_id = forms.IntegerField(min_value=1)
    index = forms.IntegerField(min_value=0, max_value=3)


class EditProfileForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=200)
    grade = forms.IntegerField(min_value=0, max_value=12)
    avatar = forms.ImageField(required=False)
    bio = forms.CharField(max_length=300, widget=forms.Textarea, required=False)

    def clean_grade(self):
        grade = self.cleaned_data.get('grade')

        if grade < 0:
            raise forms.ValidationError("Grade should be a positive Integer")
        if grade > 12:
            raise forms.ValidationError("Grade should be no larger than 12")
        return grade