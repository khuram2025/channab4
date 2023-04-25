from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser
from django.contrib.auth.models import User

class MobileAuthenticationForm(AuthenticationForm):
    mobile = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'mobile'}),
        label='Mobile',
    )

    def __init__(self, *args, **kwargs):
        super(MobileAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'] = self.fields.pop('mobile')


from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    
    mobile = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'mobile'}),
        label='Mobile',
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password1'}),
        label='Password',
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password2'}),
        label='Confirm Password',
    )


    class Meta:
        model = CustomUser
        fields = ('mobile', 'password1', 'password2')  # Add 'mobile' to the fields


from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'first_name', 'last_name', 'city', 'email', 'facebook', 'youtube']

class ProfileUpdateForm(forms.ModelForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, initial='read_only', required=False)

    class Meta:
        model = Profile
        fields = ('profile_picture', 'first_name', 'last_name', 'city', 'email', 'facebook', 'youtube')

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['role'].initial = self.instance.user.role

    def save(self, commit=True):
        profile = super(ProfileUpdateForm, self).save(commit=False)
        profile.user.role = self.cleaned_data['role']
        if commit:
            profile.save()
            profile.user.save()
        return profile