from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import CustomUser

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=15, required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(required=False,
                              widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'user_type', 'address', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class CustomUserChangeForm(UserChangeForm):
    password = None  # Hide password field

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'user_type', 'address', 'profile_picture')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

    def clean_username(self):
        username_or_email = self.cleaned_data['username']
        if '@' in username_or_email:
            if not User.objects.filter(email=username_or_email).exists():
                raise forms.ValidationError("This email is not registered.")
        else:
            if not User.objects.filter(username=username_or_email).exists():
                raise forms.ValidationError("This username is not registered.")
        return username_or_email
