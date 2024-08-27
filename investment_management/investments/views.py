from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import GovernmentBondPrimary, TreasuryBill, CorporateBond, FixedTermDeposit, User
from .forms import SignUpForm, CreateGovtBondForm, CreateTBillForm, CreateCorporateBondForm, CreateFixedDepositForm, ValuationDate
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.db.models import Sum
from django.core.paginator import Paginator
import csv
import openpyxl
from django.apps import apps
import datetime
from .ecl import LGD


def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html', {})
    else:
        return render(request, 'login.html')

def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully logged in. Welcome back!")
            return redirect('home')
        else:
            messages.error(request, "Invalid Username or Password! Please try again.")
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out!")
    return redirect('login')


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = user.username
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You Have Successfully Registered. Welcome!")
                return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'register.html', {'form': form})

@login_required
def select_investment(request):
    return render(request, 'select_investment.html', {})


@login_required
def add_government_bond(request):
    if request.method == 'POST':
        form = CreateGovtBondForm(request.POST)
        if form.is_valid():
            govt_bond = form.save(commit=False)
            govt_bond.manager = request.user
            govt_bond.save()
            messages.success(request, "Government Bond Added Successfully!")
            return HttpResponseRedirect(reverse('add_govt_bond'))
    else:
        form = CreateGovtBondForm()
    return render(request, 'add_government_bond.html', {'form': form})


@login_required
def add_treasury_bill(request):
    if request.method == 'POST':
        form = CreateTBillForm(request.POST)
        if form.is_valid():
            t_bill = form.save(commit=False)
            t_bill.manager = request.user
            t_bill.save()
            messages.success(request, "Treasury Bill Added Successfully!")
            return HttpResponseRedirect(reverse('add_t_bill'))
    else:
        form = CreateTBillForm()
    return render(request, 'add_treasury_bill.html', {'form': form})


@login_required
def add_corporate_bond(request):
    if request.method == 'POST':
        form = CreateCorporateBondForm(request.POST)
        if form.is_valid():
            corporate_bond = form.save(commit=False)
            corporate_bond.manager = request.user
            corporate_bond.save()
            messages.success(request, "Corporate Bond Added Successfully!")
            return HttpResponseRedirect(reverse('add_corporate_bond'))
    else:
        form = CreateCorporateBondForm()
    return render(request, 'add_corporate_bond.html', {'form': form})


@login_required
def add_fixed_deposit(request):
    if request.method == 'POST':
        form = CreateFixedDepositForm(request.POST)
        if form.is_valid():
            fixed_deposit = form.save(commit=False)
            fixed_deposit.manager = request.user
            fixed_deposit.save()
            messages.success(request, "Fixed Deposit Added Successfully!")
            return HttpResponseRedirect(reverse('add_fixed_deposit'))
    else:
        form = CreateFixedDepositForm()
    return render(request, 'add_fixed_deposit.html', {'form': form})


@login_required
def all_government_bonds(request):
    govt_bonds_list = GovernmentBondPrimary.objects.all().order_by('start_date')
    paginator = Paginator(govt_bonds_list, 10)  # Show 10 government bonds per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'all_govt_bonds.html', {'page_obj': page_obj})

@login_required
def all_treasury_bills(request):
    t_bills_list = TreasuryBill.objects.all().order_by('start_date')
    paginator = Paginator(t_bills_list, 10)  # Show 10 treasury bills per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'all_t_bills.html', {'page_obj': page_obj})

@login_required
def all_corporate_bonds(request):
    corporate_bonds_list = CorporateBond.objects.all().order_by('start_date')
    paginator = Paginator(corporate_bonds_list, 10)  # Show 10 corporate bonds per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'all_corporate_bonds.html', {'page_obj': page_obj})

@login_required
def all_fixed_deposits(request):
    fixed_deposits_list = FixedTermDeposit.objects.all().order_by('start_date')  # Order by start_date or another appropriate field
    paginator = Paginator(fixed_deposits_list, 10)  # Show 10 fixed deposits per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'all_fixed_deposits.html', {'page_obj': page_obj})

#### Utility Functions to Handle Downloads

def generate_csv(model):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={model.__name__}.csv'
    writer = csv.writer(response)

    # Fetching all objects of the model
    objects = model.objects.all()

    if not objects.exists():
        return response

    # Extracting field names from the model
    field_names = [field.name for field in model._meta.fields]

    # Writing header row
    writer.writerow(field_names)

    # Writing data rows
    for obj in objects:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response


def generate_excel(model):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{model._meta.model_name}.xlsx"'

    wb = openpyxl.Workbook()
    ws = wb.active
    field_names = [field.name for field in model._meta.fields]
    ws.append(field_names)

    for obj in model.objects.all():
        row = []
        for field in field_names:
            value = getattr(obj, field)
            if isinstance(value, User):
                value = value.username
            row.append(value)
        ws.append(row)

    wb.save(response)
    return response

#### Download Functions

@login_required
def download_model_csv(request, model_name):
    try:
        model = apps.get_model('investments', model_name)
    except LookupError:
        raise Http404("Model not found")
    
    return generate_csv(model)

@login_required
def download_model_excel(request, model_name):
    try:
        model = apps.get_model('investments', model_name)
    except LookupError:
        raise Http404("Model not found")
    
    return generate_excel(model)


#### Expected Returns
from collections import defaultdict
from decimal import Decimal

@login_required
def expected_returns(request):
    # Calculate the end of the previous month
    today = datetime.date.today()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)
    
    if request.method == "POST":
        form = ValuationDate(request.POST)
        if form.is_valid():
            date = form.cleaned_data['valuation_date']
        else:
            date = last_day_of_previous_month
    else:
        form = ValuationDate(initial={'valuation_date': last_day_of_previous_month})
        date = last_day_of_previous_month

    government_bonds = GovernmentBondPrimary.objects.filter(start_date__lte=date)
    treasury_bills = TreasuryBill.objects.filter(start_date__lte=date)
    corporate_bonds = CorporateBond.objects.filter(start_date__lte=date)
    fixed_deposits = FixedTermDeposit.objects.filter(start_date__lte=date)
    
    bond_data = defaultdict(lambda: {'principal': Decimal(0), 'interest': Decimal(0), 'count': 0, 'accrued': Decimal(0)})
    t_bill_data = defaultdict(lambda: {'principal': Decimal(0), 'interest': Decimal(0), 'count': 0, 'accrued': Decimal(0)})
    c_bond_data = defaultdict(lambda: {'principal': Decimal(0), 'interest': Decimal(0), 'count': 0, 'accrued': Decimal(0)})
    fd_data = defaultdict(lambda: {'principal': Decimal(0), 'interest': Decimal(0), 'count': 0, 'accrued': Decimal(0)})

    all_data = defaultdict(lambda: {'principal': Decimal(0), 'interest': Decimal(0), 'count': 0, 'accrued': Decimal(0)})

    for bond in government_bonds:
        currency = bond.currency
        bond_data[currency]['principal'] += bond.principal_amount
        bond_data[currency]['interest'] += bond.accrued_interest_on_principal(date)
        bond_data[currency]['count'] += 1
        bond_data[currency]['accrued'] += bond.principal_amount + bond.accrued_interest_on_principal(date)

    for t_bill in treasury_bills:
        currency = t_bill.currency
        t_bill_data[currency]['principal'] += t_bill.principal_amount
        t_bill_data[currency]['interest'] += t_bill.accrued_interest(date)
        t_bill_data[currency]['count'] += 1
        t_bill_data[currency]['accrued'] += t_bill.accrued_principal(date)

    for c_bond in corporate_bonds:
        currency = c_bond.currency
        c_bond_data[currency]['principal'] += c_bond.principal_amount
        c_bond_data[currency]['interest'] += c_bond.accrued_interest(date)
        c_bond_data[currency]['count'] += 1
        c_bond_data[currency]['accrued'] += c_bond.accrued_principal(date)

    for fd in fixed_deposits:
        currency = fd.currency
        fd_data[currency]['principal'] += fd.principal_amount
        fd_data[currency]['interest'] += fd.accrued_interest(date)
        fd_data[currency]['count'] += 1
        fd_data[currency]['accrued'] += fd.accrued_principal(date)

    # Aggregate all data
    for data in [bond_data, t_bill_data, c_bond_data, fd_data]:
        for currency, values in data.items():
            all_data[currency]['principal'] += values['principal']
            all_data[currency]['interest'] += values['interest']
            all_data[currency]['count'] += values['count']
            all_data[currency]['accrued'] += values['accrued']

    total_bond_data = {
        'principal': sum(bond_data[currency]['principal'] for currency in bond_data),
        'interest': sum(bond_data[currency]['interest'] for currency in bond_data),
        'count': sum(bond_data[currency]['count'] for currency in bond_data),
        'accrued': sum(bond_data[currency]['accrued'] for currency in bond_data),
    }

    total_t_bill_data = {
        'principal': sum(t_bill_data[currency]['principal'] for currency in t_bill_data),
        'interest': sum(t_bill_data[currency]['interest'] for currency in t_bill_data),
        'count': sum(t_bill_data[currency]['count'] for currency in t_bill_data),
        'accrued': sum(t_bill_data[currency]['accrued'] for currency in t_bill_data),
    }

    total_c_bond_data = {
        'principal': sum(c_bond_data[currency]['principal'] for currency in c_bond_data),
        'interest': sum(c_bond_data[currency]['interest'] for currency in c_bond_data),
        'count': sum(c_bond_data[currency]['count'] for currency in c_bond_data),
        'accrued': sum(c_bond_data[currency]['accrued'] for currency in c_bond_data),
    }

    total_fd_data = {
        'principal': sum(fd_data[currency]['principal'] for currency in fd_data),
        'interest': sum(fd_data[currency]['interest'] for currency in fd_data),
        'count': sum(fd_data[currency]['count'] for currency in fd_data),
        'accrued': sum(fd_data[currency]['accrued'] for currency in fd_data),
    }

    total_all_data = {
        'principal': sum(all_data[currency]['principal'] for currency in all_data),
        'interest': sum(all_data[currency]['interest'] for currency in all_data),
        'count': sum(all_data[currency]['count'] for currency in all_data),
        'accrued': sum(all_data[currency]['accrued'] for currency in all_data),
    }

    context = {
        'government_bonds': government_bonds,
        'treasury_bills': treasury_bills,
        'corporate_bonds': corporate_bonds,
        'fixed_deposits': fixed_deposits,
        'bond_data': dict(bond_data),  # Convert defaultdict to a regular dict for easier template handling
        'total_bond_data': total_bond_data,
        't_bill_data': dict(t_bill_data),
        'total_t_bill_data': total_t_bill_data,
        'c_bond_data': dict(c_bond_data),
        'total_c_bond_data': total_c_bond_data,
        'fd_data': dict(fd_data),
        'total_fd_data': total_fd_data,
        'all_data': dict(all_data),
        'total_all_data': total_all_data,
        'form': form,
        'valuation_date': date
    }

    return render(request, 'expected_returns.html', context)

from collections import defaultdict


@login_required
def ecl_metrics(request):
    # Calculate the end of the previous month
    today = datetime.date.today()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)

    if request.method == "POST":
        form = ValuationDate(request.POST)
        if form.is_valid():
            date = form.cleaned_data['valuation_date']
        else:
            date = last_day_of_previous_month
    else:
        form = ValuationDate(initial={'valuation_date': last_day_of_previous_month})
        date = last_day_of_previous_month

    government_bonds = GovernmentBondPrimary.objects.filter(start_date__lte=date)
    treasury_bills = TreasuryBill.objects.filter(start_date__lte=date)
    corporate_bonds = CorporateBond.objects.filter(start_date__lte=date)
    fixed_deposits = FixedTermDeposit.objects.filter(start_date__lte=date)

    bond_data = defaultdict(lambda: {'EAD': Decimal(0), 'PD': Decimal(0), 'LGD': Decimal(0), 'ECL': Decimal(0), 'count': 0})
    t_bill_data = defaultdict(lambda: {'EAD': Decimal(0), 'PD': Decimal(0), 'LGD': Decimal(0), 'ECL': Decimal(0), 'count': 0})
    c_bond_data = defaultdict(lambda: {'EAD': Decimal(0), 'PD': Decimal(0), 'LGD': Decimal(0), 'ECL': Decimal(0), 'count': 0})
    fd_data = defaultdict(lambda: {'EAD': Decimal(0), 'PD': Decimal(0), 'LGD': Decimal(0), 'ECL': Decimal(0), 'count': 0})

    all_data = defaultdict(lambda: {'EAD': Decimal(0), 'PD': Decimal(0), 'LGD': Decimal(0), 'ECL': Decimal(0), 'count': 0})

    for bond in government_bonds:
        currency = bond.currency
        bond_data[currency]['EAD'] += bond.EAD(date)
        bond_data[currency]['PD'] += bond.PD()
        bond_data[currency]['LGD'] += Decimal(LGD)
        bond_data[currency]['ECL'] += bond.ECL(date)
        bond_data[currency]['count'] += 1

    for t_bill in treasury_bills:
        currency = t_bill.currency
        t_bill_data[currency]['EAD'] += t_bill.EAD(date)
        t_bill_data[currency]['PD'] += t_bill.PD()
        t_bill_data[currency]['LGD'] += Decimal(LGD)
        t_bill_data[currency]['ECL'] += t_bill.ECL(date)
        t_bill_data[currency]['count'] += 1

    for c_bond in corporate_bonds:
        currency = c_bond.currency
        c_bond_data[currency]['EAD'] += c_bond.EAD(date)
        c_bond_data[currency]['PD'] += c_bond.PD()
        c_bond_data[currency]['LGD'] += Decimal(LGD)
        c_bond_data[currency]['ECL'] += c_bond.ECL(date)
        c_bond_data[currency]['count'] += 1

    for fd in fixed_deposits:
        currency = fd.currency
        fd_data[currency]['EAD'] += fd.EAD(date)
        fd_data[currency]['PD'] += fd.PD()
        fd_data[currency]['LGD'] += Decimal(LGD)
        fd_data[currency]['ECL'] += fd.ECL(date)
        fd_data[currency]['count'] += 1

    # Aggregate all data
    for data in [bond_data, t_bill_data, c_bond_data, fd_data]:
        for currency, values in data.items():
            all_data[currency]['EAD'] += values['EAD']
            all_data[currency]['PD'] += values['PD']
            all_data[currency]['LGD'] += values['LGD']
            all_data[currency]['ECL'] += values['ECL']
            all_data[currency]['count'] += values['count']

    def average(data, key):
        total = sum(data[currency][key] for currency in data)
        count = sum(data[currency]['count'] for currency in data)
        return total / count if count else Decimal(0)

    total_bond_data = {
        'EAD': sum(bond_data[currency]['EAD'] for currency in bond_data),
        'PD': average(bond_data, 'PD'),
        'LGD': average(bond_data, 'LGD'),
        'ECL': sum(bond_data[currency]['ECL'] for currency in bond_data),
        'count': sum(bond_data[currency]['count'] for currency in bond_data),
    }

    total_t_bill_data = {
        'EAD': sum(t_bill_data[currency]['EAD'] for currency in t_bill_data),
        'PD': average(t_bill_data, 'PD'),
        'LGD': average(t_bill_data, 'LGD'),
        'ECL': sum(t_bill_data[currency]['ECL'] for currency in t_bill_data),
        'count': sum(t_bill_data[currency]['count'] for currency in t_bill_data),
    }

    total_c_bond_data = {
        'EAD': sum(c_bond_data[currency]['EAD'] for currency in c_bond_data),
        'PD': average(c_bond_data, 'PD'),
        'LGD': average(c_bond_data, 'LGD'),
        'ECL': sum(c_bond_data[currency]['ECL'] for currency in c_bond_data),
        'count': sum(c_bond_data[currency]['count'] for currency in c_bond_data),
    }

    total_fd_data = {
        'EAD': sum(fd_data[currency]['EAD'] for currency in fd_data),
        'PD': average(fd_data, 'PD'),
        'LGD': average(fd_data, 'LGD'),
        'ECL': sum(fd_data[currency]['ECL'] for currency in fd_data),
        'count': sum(fd_data[currency]['count'] for currency in fd_data),
    }

    total_all_data = {
        'EAD': sum(all_data[currency]['EAD'] for currency in all_data),
        'PD': average(all_data, 'PD'),
        'LGD': average(all_data, 'LGD'),
        'ECL': sum(all_data[currency]['ECL'] for currency in all_data),
        'count': sum(all_data[currency]['count'] for currency in all_data),
    }

    context = {
        'government_bonds': government_bonds,
        'treasury_bills': treasury_bills,
        'corporate_bonds': corporate_bonds,
        'fixed_deposits': fixed_deposits,
        'bond_data': dict(bond_data),  # Convert defaultdict to a regular dict for easier template handling
        'total_bond_data': total_bond_data,
        't_bill_data': dict(t_bill_data),
        'total_t_bill_data': total_t_bill_data,
        'c_bond_data': dict(c_bond_data),
        'total_c_bond_data': total_c_bond_data,
        'fd_data': dict(fd_data),
        'total_fd_data': total_fd_data,
        'all_data': dict(all_data),
        'total_all_data': total_all_data,
        'form': form,
        'valuation_date': date
    }

    return render(request, 'ecl_metrics.html', context)

