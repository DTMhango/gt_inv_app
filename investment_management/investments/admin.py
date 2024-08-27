from django.contrib import admin
from .models import FixedTermDeposit, GovernmentBondPrimary, TreasuryBill, CorporateBond

@admin.register(FixedTermDeposit)
class FixedTermDepositAdmin(admin.ModelAdmin):
    list_display = ('fxd_id', 'start_date', 'maturity_date', 'principal_amount', 'currency', 'interest_rate', 'bank_rating', 'counterparty', 'manager')

@admin.register(GovernmentBondPrimary)
class GovernmentBondPrimaryAdmin(admin.ModelAdmin):
    list_display = ('bond_id', 'start_date', 'maturity_date', 'principal_amount', 'maturity_amount', 'currency', 'coupon_rate', 'bond_rating', 'counterparty', 'manager')

@admin.register(TreasuryBill)
class TreasuryBillAdmin(admin.ModelAdmin):
    list_display = ('t_bill_id', 'start_date', 'maturity_date', 'principal_amount', 'maturity_amount', 'currency', 't_bill_rating', 'counterparty', 'manager')

@admin.register(CorporateBond)
class CorporateBondAdmin(admin.ModelAdmin):
    list_display = ('bond_id', 'start_date', 'maturity_date', 'principal_amount', 'currency', 'interest_rate', 'bond_rating', 'counterparty', 'manager')
