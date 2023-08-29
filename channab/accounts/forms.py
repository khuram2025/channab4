from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser, Employee, SalaryTransaction
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
        fields = ['profile_picture', 'first_name', 'last_name', 'city', 'email', 'facebook', 'youtube', 'joining_date']

class ProfileUpdateForm(forms.ModelForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, initial='read_only', required=False)

    class Meta:
        model = Profile
        fields = ('profile_picture', 'first_name', 'last_name', 'city', 'facebook', 'youtube', 'joining_date', 'end_date')

    joining_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    # Add this field
    mobile = forms.CharField(max_length=17, required=False)

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['role'].initial = self.instance.user.role
            # Initialize mobile field with the user's mobile number
            self.fields['mobile'].initial = self.instance.user.mobile

    def save(self, commit=True):
        profile = super(ProfileUpdateForm, self).save(commit=False)
        profile.user.role = self.cleaned_data['role']
        if commit:
            profile.save()
            profile.user.save()
        return profile

class FarmMemberCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
    farm_name = forms.CharField(label="Farm Name", required=False)

    class Meta:
        model = CustomUser
        fields = ('mobile', 'first_name', 'last_name', 'farm_name')
        labels = {
            'mobile': 'Mobile Number',
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(FarmMemberCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class ResetPasswordForm(forms.Form):
    new_password1 = forms.CharField(label="New password", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Confirm new password", widget=forms.PasswordInput)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2


from django import forms
from .models import SalaryComponent, Farm

class SalaryComponentForm(forms.ModelForm):
    class Meta:
        model = SalaryComponent
        fields = ['name', 'amount', 'duration']

class SalaryTransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        member = kwargs.pop('member', None)
        farm = kwargs.pop('farm', None)
        super(SalaryTransactionForm, self).__init__(*args, **kwargs)

        if member:
            self.fields['farm_member'].queryset = CustomUser.objects.filter(pk=member.pk)
        elif farm:
            self.fields['farm_member'].queryset = CustomUser.objects.filter(farm=farm)
            self.fields['component'].queryset = SalaryComponent.objects.filter(member__farm=farm)

    class Meta:
        model = SalaryTransaction
        fields = ('farm_member', 'component', 'amount_paid', 'transaction_date', 'description' )

class FarmUpdateForm(forms.ModelForm):
    class Meta:
        model = Farm
        fields = ['name', 'description', 'location', 'profile_picture']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['full_name', 'mobile', 'profile_picture', 'address', 'role']
