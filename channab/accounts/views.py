from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


from farm_finances.models import Expense, ExpenseCategory
from .models import Farm
from .forms import  FarmMemberCreationForm, MobileAuthenticationForm,  ProfileUpdateForm, ResetPasswordForm, SalaryTransactionForm, FarmUpdateForm
from django.shortcuts import render, redirect, get_object_or_404

class SignupView(CreateView):
    form_class = FarmMemberCreationForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/signup.html'

    def get_form_kwargs(self):
        kwargs = super(SignupView, self).get_form_kwargs()
        kwargs['signup'] = True
        return kwargs

    def form_valid(self, form):
        user = form.save(commit=False)
        
        print("Form cleaned_data:", form.cleaned_data)
        
        user.role = 'admin'
        user.save()
        farm_name = form.cleaned_data.get("farm_name")
        user.create_farm_and_save(farm_name=farm_name)
        
        print("User role after save:", user.role)
        print("User farm after save:", user.farm)
        
        self.object = user
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        print("Form is invalid")
        print("Form errors:", form.errors)
        print("POST data:", self.request.POST)
        return super().form_invalid(form)


def login_view(request):
    if request.method == 'POST':
        form = MobileAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # If 'remember_me' is not checked in the form, set the session to expire when the user closes the browser.
            if not request.POST.get('remember_me', False):
                request.session.set_expiry(0)

            return redirect(reverse('home:home'))
        else:
            print("Form is invalid")
            print(form.errors)
            print(request.POST)
    else:
        form = MobileAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        mobile_number = request.data.get("mobile_number")
        password = request.data.get("password")
        user = authenticate(request, username=mobile_number, password=password)
        if user is not None:
            # login successful
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_401_UNAUTHORIZED)





from .forms import ProfileForm
from .models import Profile, CustomUser, SalaryTransaction

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
        form = FarmMemberCreationForm(request.POST, signup=False)
        print("POST data received:", request.POST)  # Debugging line

        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'labour'

            user.farm = request.user.farm
            user.save()
            print("User created:", user)  # Debugging line

            # Create or update the Profile for the user
            profile, created = Profile.objects.get_or_create(user=user)
            profile.first_name = form.cleaned_data['member_name']
            profile.city = form.cleaned_data['location']
            profile.joining_date = form.cleaned_data['join_date']

            profile.save()
            print("Profile created/updated:", profile)  # Debugging line

            return redirect('accounts:user_profile')
        else:
            print("Form errors:", form.errors)  # Debugging line
    else:
        form = FarmMemberCreationForm(signup=False)

    return render(request, 'accounts/create_farm_member.html', {'form': form})



@login_required
def reset_password(request, pk):
    if request.user.role != 'admin':
        return HttpResponseForbidden("You are not allowed to perform this action")

    member = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            member.set_password(form.cleaned_data["new_password1"])
            member.save()
            return redirect('accounts:member_detail', member_id=pk)
    else:
        form = ResetPasswordForm()

    context = {
        'form': form,
        'member': member,
    }
    return render(request, 'accounts/reset_password.html', context)

def edit_member(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)

    if not hasattr(user, 'profile'):
        Profile.objects.create(user=user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user.profile)

        if form.is_valid():
            form.save()
            return redirect('accounts:member_detail', member_id=pk)

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
        return redirect('accounts:farm_member_list')

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

from datetime import date
from dateutil.relativedelta import relativedelta

def calculate_salary_status(member):
    from datetime import date
    from accounts.models import SalaryTransaction

    salary_transactions = SalaryTransaction.objects.filter(farm_member=member)

    salary_status = {}
    total_salary_received = 0

    for transaction in salary_transactions:
        component_name = transaction.component.name
        if component_name not in salary_status:
            salary_status[component_name] = transaction.amount_paid
        else:
            salary_status[component_name] += transaction.amount_paid

        total_salary_received += transaction.amount_paid

    salary_status["total_salary_received"] = total_salary_received

    for key, value in salary_status.items():
        if key != "total_salary_received":
            salary_status[key] = {"received_amount": value, "sum_with_total": value + total_salary_received}

    today = date.today()

    today = date.today()

    if hasattr(member, 'profile') and member.profile.joining_date is not None:
        joining_date = member.profile.joining_date
        end_date = member.profile.end_date
        if end_date and end_date < today:
            # If end date is provided and it's in the past, use the end date for calculations
            days_worked = (end_date - joining_date).days
        else:
            days_worked = (today - joining_date).days

        daily_salary = member.total_salary() / 30
        expected_salary_till_now = round(days_worked * daily_salary)  # Round to the nearest integer
        remaining_salary = expected_salary_till_now - total_salary_received
    else:
        # Handle the case when joining_date is None. For example:
        days_worked = 0
        daily_salary = 0
        expected_salary_till_now = 0
        remaining_salary = 0

    salary_status["expected_salary_till_now"] = expected_salary_till_now
    salary_status["remaining_salary"] = remaining_salary

    return salary_status



@login_required
def member_detail(request, member_id):
    member = get_object_or_404(CustomUser, pk=member_id)
    salary_transactions = SalaryTransaction.objects.filter(farm_member=member)
    salary_status = calculate_salary_status(member)
    
    # List of keys you want to exclude
    excluded_keys = ["total_salary_received", "expected_salary_till_now", "remaining_salary"]
    
    if request.method == 'POST':
        form = SalaryComponentForm(request.POST)
        if form.is_valid():
            salary_component = form.save(commit=False)
            salary_component.member = member
            salary_component.save()
            return redirect('accounts:member_detail', member_id=member_id)
    else:
        form = SalaryComponentForm()

    return render(request, 'accounts/member_detail.html', {
        'member': member, 
        'form': form, 
        'salary_transactions': salary_transactions, 
        'salary_status': salary_status,
        'excluded_keys': excluded_keys
    })


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

@login_required
def update_salary_component(request, member_id, component_id):
    member = get_object_or_404(CustomUser, pk=member_id)
    component = get_object_or_404(SalaryComponent, pk=component_id, member=member)

    if request.method == 'POST':
        form = SalaryComponentForm(request.POST, instance=component)
        if form.is_valid():
            form.save()
            return redirect('accounts:salary_components', member_id=member.pk)
    else:
        form = SalaryComponentForm(instance=component)

    context = {
        'form': form,
        'member': member,
        'component': component
    }
    return render(request, 'accounts/update_salary_component.html', context)

@login_required
def delete_salary_component(request, member_id, component_id):
    member = get_object_or_404(CustomUser, pk=member_id)
    component = get_object_or_404(SalaryComponent, pk=component_id, member=member)

    if request.method == 'POST':
        component.delete()
        return redirect('accounts:member_detail', member_id=member.pk)  # Redirecting to member_detail
    
    context = {
        'member': member,
        'component': component
    }
    return render(request, 'accounts/delete_salary_component_confirm.html', context)



@login_required
def salary_transaction_list(request):
    # Get the user's farm
    farm = request.user.farm

    # Filter the transactions by the user's farm using the farm_member relationship
    transactions = SalaryTransaction.objects.filter(farm_member__farm=farm)

    return render(request, 'accounts/salary_transaction_list.html', {'salary_transactions': transactions})




from django.http import JsonResponse

def get_salary_components(request, user_id):
    components = SalaryComponent.objects.filter(member_id=user_id).values('id', 'name')
    return JsonResponse(list(components), safe=False)


@login_required
def salary_transaction_update(request, pk=None):
    farm = request.user.farm

    if pk is not None:
        transaction = SalaryTransaction.objects.get(pk=pk)
        print("Existing transaction found:", transaction)
        edit_mode = True
    else:
        transaction = None
        edit_mode = False

    if request.method == 'POST':
        form = SalaryTransactionForm(request.POST, instance=transaction, farm=farm)
        if form.is_valid():
            transaction = form.save()  
            
            # Create or retrieve the salary expense category for the farm
            salary_category, created = ExpenseCategory.objects.get_or_create(farm=farm, name='Salary')

            # Try to get the associated expense
            try:
                expense = Expense.objects.get(salary_transaction=transaction)
            except Expense.DoesNotExist:
                # If not found, create a new expense instance
                expense = Expense(user=request.user, farm=farm)

            # Update the expense instance with the salary transaction data
            expense.date = transaction.transaction_date
            expense.description = f'Salary for {transaction.farm_member} - {transaction.component.name}'
            expense.amount = transaction.amount_paid
            expense.category = salary_category
            expense.salary_transaction = transaction

            # Save the expense instance
            expense.save()

            return redirect('accounts:salary_transaction_list')


    else:
        form = SalaryTransactionForm(instance=transaction, farm=farm)
    context = {
        'form': form,
        'edit_mode': edit_mode,
        'salary_transaction': transaction
    }    
    return render(request, 'accounts/salary_transaction_form.html', context)

@login_required
def salary_transaction_update_member(request, member_id, pk):
    farm = request.user.farm
    try:
        member = CustomUser.objects.get(pk=member_id)
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound("FarmMember not found")

    if pk is not None:
        try:
            transaction = SalaryTransaction.objects.get(farm_member=member, pk=pk)
            print("Existing transaction found:", transaction)
            edit_mode = True
        except SalaryTransaction.DoesNotExist:
            transaction = None
            edit_mode = False

    if request.method == 'POST':
        form = SalaryTransactionForm(request.POST, instance=transaction, farm=farm, member=member)
        if form.is_valid():
            if transaction is not None:
                transaction.transaction_date = form.cleaned_data['transaction_date']
                transaction.farm_member = form.cleaned_data['farm_member']
                transaction.component = form.cleaned_data['component']
                transaction.amount_paid = form.cleaned_data['amount_paid']
                transaction.save()
            else:
                transaction = form.save(commit=False)
                transaction.farm_member = member
                transaction.save()

            # Create or retrieve the salary expense category for the farm
            salary_category, created = ExpenseCategory.objects.get_or_create(farm=farm, name='Salary')

            # other code here...

            return redirect('accounts:salary_transaction_list')
    else:
        form = SalaryTransactionForm(instance=transaction, farm=farm, member=member)
        if not edit_mode:
            form.fields['farm_member'].initial = member

    context = {
        'form': form,
        'edit_mode': edit_mode,
        'salary_transaction': transaction,
        'member': member
    }
    
    return render(request, 'accounts/salary_transaction_form.html', context)


from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView

# Your other views...

class SalaryTransactionUpdateView(UpdateView):
    model = SalaryTransaction
    form_class = SalaryTransactionForm
    template_name = 'accounts/salary_transaction_form.html'

    def get_form_kwargs(self):
        kwargs = super(SalaryTransactionUpdateView, self).get_form_kwargs()
        kwargs['farm'] = self.request.user.farm  # Replace `farm` with the correct attribute to get the farm instance for the logged-in user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('accounts:salary_transaction_list')


@login_required
def salary_transaction_delete(request, pk):
    transaction = SalaryTransaction.objects.get(pk=pk)
    transaction_pk = transaction.pk

    expenses = Expense.objects.filter(salary_transaction=transaction)
    
    if expenses.exists():
        for expense in expenses:
            expense_pk = expense.pk
            print(f"Related expense found for transaction id {transaction_pk}: Expense id {expense_pk}")
            expense.delete()
            print(f"Deleting related expense with id {expense_pk}")
    else:
        print(f"No related expense found for transaction id {transaction_pk}")

    transaction.delete()
    print(f"Deleting salary transaction with id {transaction_pk}")

    return redirect('accounts:salary_transaction_list')

def farm_view(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')  # Redirect to login page if the user is not authenticated

    farm = get_object_or_404(Farm, admin=request.user)  # Get the farm that is associated with the logged-in user
    farm_members = []
    if request.user.role == 'admin':
        farm_members = CustomUser.objects.filter(farm=request.user.farm)

    context = {
        'farm': farm,
        'farm_members': farm_members
    }
    return render(request, 'accounts/farm_detail.html', context)

def edit_farm(request, farm_id):
    farm = get_object_or_404(Farm, pk=farm_id)
    
    if request.user != farm.admin:
        return HttpResponseForbidden("You don't have permission to edit this farm")

    if request.method == "POST":
        form = FarmUpdateForm(request.POST, request.FILES, instance=farm)
        if form.is_valid():
            form.save()
            return redirect('accounts:farm_detail')  # Redirect to farm detail page
    else:
        form = FarmUpdateForm(instance=farm)

    return render(request, 'accounts/edit_farm.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect(reverse('home:home'))




