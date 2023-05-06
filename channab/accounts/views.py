from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import  FarmMemberCreationForm, MobileAuthenticationForm, CustomUserCreationForm, ProfileUpdateForm
from django.shortcuts import render, redirect, get_object_or_404

class SignupView(CreateView):
    form_class = FarmMemberCreationForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/signup.html'

    def form_valid(self, form):
        print("Form is valid")

        user = form.save(commit=False)

        if self.request.user.is_authenticated and hasattr(self.request.user, 'farm') and self.request.user.role == 'admin':
            user.role = 'read_only'
            user.farm = self.request.user.farm
            print("User has a farm and is admin")
        else:
            user.role = 'admin'
            print("User role set to admin")

        user.save()
        print("User role:", user.role)
        print("User farm:", user.farm)

        if user.role == 'admin' and user.farm is None:
            self.create_farm_for_user(user, form)
        else:
            print("Farm creation condition not met")

        self.object = user
        print("User created:", self.object)
        return HttpResponseRedirect(self.get_success_url())

    def create_farm_for_user(self, user, form):
        print("Creating farm for user")
        farm_name = form.cleaned_data.get("farm_name")
        print("Submitted farm name:", farm_name)

        if not farm_name:
            farm_name = f"{user.first_name}'s Farm"
        print("Final farm name:", farm_name)
        user.create_farm_and_save(farm_name=farm_name)
        print("User farm after creation:", user.farm)

    def form_invalid(self, form):
        print("Form is invalid")
        print(form.errors)
        return super().form_invalid(form)


def login_view(request):
    if request.method == 'POST':
        form = MobileAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(reverse('home:home'))
        else:
            print("Form is invalid")
            print(form.errors)
    else:
        form = MobileAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


from .forms import ProfileForm
from .models import Profile, CustomUser

def user_profile(request):
    if not request.user.is_authenticated:
        return redirect('accounts/login')

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)
        profile.save()

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = ProfileUpdateForm(instance=profile)

    # Fetch farm members if the user is an admin
    farm_members = []
    if request.user.role == 'admin':
        farm_members = CustomUser.objects.filter(farm=request.user.farm)

    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile, 'farm_members': farm_members})


from .forms import ProfileUpdateForm

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            print("Form saved successfully")
            return redirect('accounts:user_profile')
        else:
            print("Form is not valid")
            print(form.errors)
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def create_farm_member(request):
    if request.method == 'POST':
        form = FarmMemberCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'read_only'
            user.farm = request.user.farm
            user.save()
            return redirect('accounts:user_profile')
    else:
        form = FarmMemberCreationForm()

    return render(request, 'accounts/create_farm_member.html', {'form': form})

def edit_member(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)

    if not hasattr(user, 'profile'):
        Profile.objects.create(user=user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user.profile)

        if form.is_valid():
            form.save()
            return redirect('accounts:user_profile')

    else:
        form = ProfileUpdateForm(instance=user.profile)

    context = {
        'form': form,
        'member': user
    }

    return render(request, 'accounts/edit_member.html', context)



def delete_member(request, pk):
    member = get_object_or_404(CustomUser, pk=pk)

    if request.method == 'POST':
        member.delete()
        # Redirect to the member list page or any other page after successful deletion
        return redirect('accounts:user_profile')

    context = {
        'member': member
    }

    return render(request, 'accounts/delete_member_confirm.html', context)

@login_required
def farm_member_list(request):
    if request.user.role != 'admin':
        return redirect('home:home')

    farm_members = CustomUser.objects.filter(farm=request.user.farm)

    context = {
        'farm_members': farm_members,
    }

    return render(request, 'accounts/farm_member_list.html', context)

def member_detail(request, member_id):
    member = get_object_or_404(CustomUser, pk=member_id)  # Use CustomUser instead of FarmMember
    return render(request, 'accounts/member_detail.html', {'member': member})

from .forms import SalaryComponentForm
from .models import SalaryComponent

@login_required
def salary_components(request, member_id):
    member = get_object_or_404(CustomUser, pk=member_id)
    components = SalaryComponent.objects.filter(member=member)

    context = {
        'member': member,
        'components': components,
    }
    return render(request, 'accounts/salary_components.html', context)

@login_required
def add_salary_component(request, member_id):
    member = get_object_or_404(CustomUser, pk=member_id)

    if request.method == 'POST':
        form = SalaryComponentForm(request.POST)
        if form.is_valid():
            component = form.save(commit=False)
            component.member = member
            component.save()
            return redirect('accounts:salary_components', member_id=member.pk)
    else:
        form = SalaryComponentForm()

    context = {
        'form': form,
        'member': member
    }
    return render(request, 'accounts/add_salary_component.html', context)


def logout_view(request):
    logout(request)
    return redirect(reverse('home:home'))