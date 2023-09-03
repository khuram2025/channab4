from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser,  SalaryTransaction
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
    last_name = forms.CharField(max_length=30, required=False)  # make this optional
    mobile = forms.CharField(max_length=17, required=False)  # make this optional

    class Meta:
        model = Profile
        fields = ('profile_picture', 'first_name', 'last_name', 'city', 'facebook', 'youtube', 'joining_date', 'end_date')

    joining_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False  # make this optional if not already
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )

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
    mobile = forms.CharField(max_length=17, required=False)


    # Additional fields for Farm Member creation
    member_name = forms.CharField(label="Member Name", required=False)
    location = forms.CharField(label="Location", required=False)
    join_date = forms.DateField(label="Join Date", required=False, widget=forms.SelectDateWidget)
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, initial="labour", required=False, widget=forms.HiddenInput)


    class Meta:
        model = CustomUser
        fields = ('mobile', 'first_name', 'last_name', 'farm_name', 'member_name', 'location', 'join_date', 'role')
        labels = {
            'mobile': 'Mobile Number',
        }
    join_date = forms.DateField(
        label="Join Date", 
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )


    def __init__(self, *args, **kwargs):
        # Extract the custom 'signup' argument and remove it from kwargs
        self.is_signup = kwargs.pop('signup', False)
        super(FarmMemberCreationForm, self).__init__(*args, **kwargs)
        
        # Adjust fields based on context
        if self.is_signup:
            self.fields['mobile'].required = True
            del self.fields['member_name']
            del self.fields['location']
            del self.fields['join_date']
            del self.fields['role']
        else:
            # self.fields['mobile'].required = False
            # del self.fields['mobile']
            del self.fields['password1']
            del self.fields['password2']
            del self.fields['farm_name']
            del self.fields['first_name']
            del self.fields['last_name']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(FarmMemberCreationForm, self).save(commit=False)
        if "password1" in self.cleaned_data:
            user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
        return user

    def clean_mobile(self):
        mobile = self.cleaned_data.get("mobile")
        if mobile:  # Only perform the check if a mobile number is provided
            if CustomUser.objects.filter(mobile=mobile).exists():
                raise forms.ValidationError("A user with this mobile number already exists.")
        elif self.is_signup:  # No mobile number is provided and it's a signup form
            raise forms.ValidationError("Mobile number is required for signup.")
        else:
            mobile = None  # Ensure empty strings are not saved to the database
        return mobile




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
