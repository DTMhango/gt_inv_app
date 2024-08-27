from typing import Any
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import GovernmentBondPrimary, FixedTermDeposit, TreasuryBill, CorporateBond


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}), max_length=50)
    last_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}), max_length=50)
    email = forms.EmailField(label="", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args: Any, **kwargs: Any):
        super(SignUpForm, self).__init__(*args, **kwargs)
        
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.username = f"{user.first_name}_{user.last_name}"

        # Check if the generated username already exists
        if User.objects.filter(username=user.username).exists():
            user.username = f"{user.username}_{User.objects.count()}"
        
        if commit:
            user.save()
        return user


class DateInput(forms.DateInput):
    input_type = 'date'

class ValuationDate(forms.Form):
    valuation_date = forms.DateField(label='Set Valuation Date', widget=DateInput(attrs={'type': 'date', 'class': 'form-control'}))

class CreateGovtBondForm(forms.ModelForm):

    class Meta:
        model = GovernmentBondPrimary
        fields = ['bond_id', 'start_date', 'maturity_date', 'principal_amount', 'maturity_amount', 'coupon_rate', 'bond_rating', 'counterparty', 'manager']
        widgets = {
            'start_date': DateInput(),
            'maturity_date': DateInput(),
        }
        exclude = ("manager",)


    def __init__(self, *args, **kwargs):
        super(CreateGovtBondForm, self).__init__(*args, **kwargs)

        self.fields['bond_id'].widget.attrs['class'] = 'form-control'
        self.fields['bond_id'].widget.attrs['placeholder'] = 'Unique Bond ID'
        self.fields['bond_id'].label = 'Bond ID'

        self.fields['start_date'].widget.attrs['class'] = 'form-control'
        self.fields['start_date'].widget.attrs['placeholder'] = 'Select Start Date'
        self.fields['start_date'].label = 'Select Start Date'

        self.fields['maturity_date'].widget.attrs['class'] = 'form-control'
        self.fields['maturity_date'].widget.attrs['placeholder'] = 'Select Maturity Date'
        self.fields['maturity_date'].label = 'Select Maturity Date'

        self.fields['principal_amount'].widget.attrs['class'] = 'form-control'
        self.fields['principal_amount'].widget.attrs['placeholder'] = 'Enter Principal Amount'
        self.fields['principal_amount'].label = 'Principal Amount'

        self.fields['maturity_amount'].widget.attrs['class'] = 'form-control'
        self.fields['maturity_amount'].widget.attrs['placeholder'] = 'Enter Maturity Amount'
        self.fields['maturity_amount'].label = 'Maturity Amount'

        self.fields['coupon_rate'].widget.attrs['class'] = 'form-control'
        self.fields['coupon_rate'].widget.attrs['placeholder'] = 'Enter Bond Coupon Rate'
        self.fields['coupon_rate'].label = 'Bond Coupon Rate'

        self.fields['bond_rating'].widget.attrs['class'] = 'form-control'
        self.fields['bond_rating'].widget.attrs['placeholder'] = 'Select Bond Rating'

        self.fields['counterparty'].widget.attrs['class'] = 'form-control'
        self.fields['counterparty'].widget.attrs['placeholder'] = 'Select Counterparty'


class CreateTBillForm(forms.ModelForm):

    class Meta:
        model = TreasuryBill
        fields = ['t_bill_id', 'start_date', 'maturity_date', 'principal_amount', 'maturity_amount', 't_bill_rating', 'counterparty', 'manager']
        widgets = {
            'start_date': DateInput(),
            'maturity_date': DateInput(),
        }
        exclude = ("manager",)


    def __init__(self, *args, **kwargs):
        super(CreateTBillForm, self).__init__(*args, **kwargs)

        self.fields['t_bill_id'].widget.attrs['class'] = 'form-control'
        self.fields['t_bill_id'].widget.attrs['placeholder'] = 'Unique Treasury Bill ID'
        self.fields['t_bill_id'].label = 'Treasury Bill ID'

        self.fields['start_date'].widget.attrs['class'] = 'form-control'
        self.fields['start_date'].label = 'Select Start Date'

        self.fields['maturity_date'].widget.attrs['class'] = 'form-control'
        self.fields['maturity_date'].label = 'Select Maturity Date'

        self.fields['principal_amount'].widget.attrs['class'] = 'form-control'
        self.fields['principal_amount'].widget.attrs['placeholder'] = 'Enter Principal Amount'
        self.fields['principal_amount'].label = 'Principal Amount'

        self.fields['maturity_amount'].widget.attrs['class'] = 'form-control'
        self.fields['maturity_amount'].widget.attrs['placeholder'] = 'Enter Maturity Amount'
        self.fields['maturity_amount'].label = 'Maturity Amount'

        self.fields['t_bill_rating'].widget.attrs['class'] = 'form-control'
        self.fields['t_bill_rating'].widget.attrs['placeholder'] = 'Select T-Bill Rating'
        self.fields['t_bill_rating'].label = 'Treasury Bill Rating'

        self.fields['counterparty'].widget.attrs['class'] = 'form-control'
        self.fields['counterparty'].widget.attrs['placeholder'] = 'Select Counterparty'


class CreateCorporateBondForm(forms.ModelForm):

    class Meta:
        model = CorporateBond
        fields = ['bond_id', 'start_date', 'maturity_date', 'principal_amount', 'interest_rate', 'bond_rating', 'counterparty', 'manager']
        widgets = {
            'start_date': DateInput(),
            'maturity_date': DateInput(),
        }
        exclude = ("manager",)


    def __init__(self, *args, **kwargs):
        super(CreateCorporateBondForm, self).__init__(*args, **kwargs)

        self.fields['bond_id'].widget.attrs['class'] = 'form-control'
        self.fields['bond_id'].widget.attrs['placeholder'] = 'Unique Treasury Bill ID'
        self.fields['bond_id'].label = 'Treasury Bill ID'

        self.fields['start_date'].widget.attrs['class'] = 'form-control'
        self.fields['start_date'].label = 'Select Start Date'

        self.fields['maturity_date'].widget.attrs['class'] = 'form-control'
        self.fields['maturity_date'].label = 'Select Maturity Date'

        self.fields['principal_amount'].widget.attrs['class'] = 'form-control'
        self.fields['principal_amount'].widget.attrs['placeholder'] = 'Enter Principal Amount'
        self.fields['principal_amount'].label = 'Principal Amount'

        # self.fields['maturity_amount'].widget.attrs['class'] = 'form-control'
        # self.fields['maturity_amount'].widget.attrs['placeholder'] = 'Enter Maturity Amount'
        # self.fields['maturity_amount'].label = 'Maturity Amount'

        self.fields['interest_rate'].widget.attrs['class'] = 'form-control'
        self.fields['interest_rate'].widget.attrs['placeholder'] = 'Enter Bond Interest Rate'
        self.fields['interest_rate'].label = 'Bond Interest Rate'

        self.fields['bond_rating'].widget.attrs['class'] = 'form-control'
        self.fields['bond_rating'].widget.attrs['placeholder'] = 'Select Bond Rating'
        self.fields['bond_rating'].label = 'Bond Rating'

        self.fields['counterparty'].widget.attrs['class'] = 'form-control'
        self.fields['counterparty'].widget.attrs['placeholder'] = 'Select Counterparty'


class CreateFixedDepositForm(forms.ModelForm):

    class Meta:
        model = FixedTermDeposit
        fields = ['fxd_id', 'start_date', 'maturity_date', 'principal_amount', 'interest_rate', 'currency', 'counterparty', 'bank_rating', 'manager']
        widgets = {
            'start_date': DateInput(),
            'maturity_date': DateInput(),
        }
        exclude = ("manager",)


    def __init__(self, *args, **kwargs):
        super(CreateFixedDepositForm, self).__init__(*args, **kwargs)

        self.fields['fxd_id'].widget.attrs['class'] = 'form-control'
        self.fields['fxd_id'].widget.attrs['placeholder'] = 'Unique Fixed Deposit ID'
        self.fields['fxd_id'].label = 'Fixed Deposit ID'

        self.fields['start_date'].widget.attrs['class'] = 'form-control'
        self.fields['start_date'].label = 'Select Start Date'

        self.fields['maturity_date'].widget.attrs['class'] = 'form-control'
        self.fields['maturity_date'].label = 'Select Maturity Date'

        self.fields['principal_amount'].widget.attrs['class'] = 'form-control'
        self.fields['principal_amount'].widget.attrs['placeholder'] = 'Enter Principal Amount'
        self.fields['principal_amount'].label = 'Principal Amount'

        self.fields['interest_rate'].widget.attrs['class'] = 'form-control'
        self.fields['interest_rate'].widget.attrs['placeholder'] = 'Enter Interest Rate'
        self.fields['interest_rate'].label = 'Interest Rate'

        self.fields['currency'].widget.attrs['class'] = 'form-control'
        # self.fields['maturity_amount'].widget.attrs['placeholder'] = 'Enter Maturity Amount'
        self.fields['currency'].label = 'Select Currency'

        self.fields['bank_rating'].widget.attrs['class'] = 'form-control'
        self.fields['bank_rating'].widget.attrs['placeholder'] = 'Select Rating'
        self.fields['bank_rating'].label = 'Bank Rating'

        self.fields['counterparty'].widget.attrs['class'] = 'form-control'
        self.fields['counterparty'].widget.attrs['placeholder'] = 'Select Counterparty'
        self.fields['counterparty'].label = 'Bank'
