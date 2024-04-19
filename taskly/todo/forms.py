from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from django import forms
from .models import Task, Profile



class CreateUserForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone_number']
        


class LoginForm(AuthenticationForm):
    
    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())
    

class PasswordResetEmailForm(forms.Form):
    
    email = forms.EmailField(label='Email')
    
    

class PasswordUpdateForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']

    

class CreateTaskForm(forms.ModelForm):
    
    class Meta:
        
        model = Task
        fields = ['title', 'content', 'status' , 'do_to', ] 
        exclude = ['user', ]
        
        widgets = {
            'do_to': forms.DateInput(attrs={'type': 'date'}),
        }


    
class UpdateProfilePhoneNumberForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number']
    

class UpdateUserForm(forms.ModelForm):
    
    password = None
    
    class Meta:
        
        model = User
        fields = ['username', 'email',]
        exclude = ['password1', 'password2',]
        
        
class UpdateProfileForm(forms.ModelForm):
    profile_pic = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file', 'id': 'id_profile_pic'}))
    
    class Meta:
        model = Profile
        fields = ['profile_pic',]

