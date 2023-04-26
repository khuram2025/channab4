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
        else:
            user.role = 'admin'
        
        user.save()
        self.object = user
        print("User created:", self.object)
        return HttpResponseRedirect(self.get_success_url())

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




def logout_view(request):
    logout(request)
    return redirect(reverse('home:home'))