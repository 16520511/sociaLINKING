from django import forms
from django.contrib.auth import authenticate
from .models import MyUser

class RegisterForm(forms.Form):
    CHOICE = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )

    email = forms.EmailField(label = 'Email Address', max_length = 50)
    firstName = forms.CharField(label = 'First Name', max_length = 50)
    lastName = forms.CharField(label = 'Last Name', max_length = 50) 
    gender = forms.ChoiceField(choices = CHOICE, initial = 'Male')
    age = forms.IntegerField()
    password = forms.CharField(max_length = 50, widget = forms.PasswordInput)
    password2 = forms.CharField(label = 'Confirm Password', max_length = 50, widget = forms.PasswordInput)

    def clean_email(self):
        super().clean()
        email = self.cleaned_data['email']
        takenEmail = []
        for i in MyUser.objects.all():
            takenEmail.append(i.email)
        if email in takenEmail:
            raise forms.ValidationError('This email address has already exists! Please choose another one.')
        return email

    def clean_age(self):
        super().clean
        age = self.cleaned_data['age']
        if age < 12:
            raise forms.ValidationError('You have to be over 12 years old to register.')
        return age

    def clean_password2(self):
        super().clean()
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        if password and password2 and password != password2:
            raise forms.ValidationError('Password doesn''t match.')

class LoginForm(forms.Form):
    email = forms.EmailField(label = 'Email Address', max_length = 50)
    password = forms.CharField(max_length = 50, widget = forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user = authenticate(username = email, password = password)
        if not user:
            raise forms.ValidationError('Login Failed!')
        return self.cleaned_data

class CreateGroupForm(forms.Form):
    title = forms.CharField(label = 'Group Title', max_length = 100)
    description = forms.CharField(label = 'Description', max_length = 300)
    