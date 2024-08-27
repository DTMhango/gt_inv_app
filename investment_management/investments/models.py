from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date
from decimal import Decimal
from .ecl import PD_SOVEREIGN_MOODYS, PD_CORPORATE_MOODYS, LGD
from django.db.models import Sum

class GovernmentBondPrimary(models.Model):
    bond_id = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    maturity_date = models.DateField()
    principal_amount = models.DecimalField(max_digits=15, decimal_places=2)
    maturity_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default="zmw", choices=[("zmw", "ZMW"), ("usd", "USD")])
    coupon_rate = models.DecimalField(max_digits=6, decimal_places=4)
    bond_rating = models.CharField(
        max_length=50,
        choices=[
            ('Aaa', 'Aaa'),
            ('Aa', 'Aa'),
            ('A', 'A'),
            ('Baa', 'Baa'),
            ('Ba', 'Ba'),
            ('B', 'B'),
            ('Caa-C', 'Caa-C'),
        ],
        default='Caa-C'
    )
    counterparty = models.CharField(
        max_length=50,
        choices=[
            ('boz', 'BOZ'),
            ('absa', 'ABSA'),
            ('fnb', 'FNB'),
            ('zanaco', 'ZANACO'),
            ('napsa', "NAPSA"),
        ]
    )
    counterparty_type = models.CharField(max_length=50, default="Sovereign", editable=False)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)

    def clean(self):
        if self.maturity_date <= self.start_date:
            raise ValidationError('Maturity date must be after the start date.')

    def tenure(self):
        return (self.maturity_date - self.start_date).days

    def elapsed_term(self, date):
        return (date - self.start_date).days

    def remaining_term(self, date):
        remaining = (self.maturity_date - date).days
        return remaining if remaining > 0 else 0

    def accrued_interest_on_principal(self, date):
        if date < self.start_date:
            return Decimal(0)
        elif date > self.maturity_date:
            return self.maturity_amount - self.principal_amount
        else:
            return (self.maturity_amount - self.principal_amount) * Decimal(self.elapsed_term(date)) / Decimal(self.tenure())

    def accrued_coupon(self, date):
        if date < self.start_date:
            return Decimal(0)
        elif date > self.maturity_date:
            return Decimal(self.tenure()) / Decimal(365) * self.maturity_amount * self.coupon_rate / Decimal(100)
        else:
            return Decimal(self.elapsed_term(date)) / Decimal(365) * self.maturity_amount * self.coupon_rate / Decimal(100)

    def total_coupons(self, date):
        return self.couponpayment_set.filter(
            date_received__gte=self.start_date,
            date_received__lte=date
        ).aggregate(total=Sum('amount_received'))['total'] or Decimal(0)

    def EAD(self, date):
        if date < self.start_date or date > self.maturity_date:
            return Decimal(0)
        return self.principal_amount + self.accrued_interest_on_principal(date) + self.accrued_coupon(date) - Decimal(self.total_coupons(date) or 0)

    def PD(self):
        return Decimal(PD_SOVEREIGN_MOODYS[self.bond_rating])

    def ECL(self, date):
        if date < self.start_date or date > self.maturity_date:
            return Decimal(0)
        if self.remaining_term(date) > 365:
            return self.PD() * Decimal(LGD) * self.EAD(date)
        else:
            return self.PD() * Decimal(self.remaining_term(date)) / Decimal(365) * Decimal(LGD) * self.EAD(date)

    def get_manager_full_name(self):
        return f"{self.manager.first_name} {self.manager.last_name}"

    def __str__(self):
        return self.bond_id


class CouponPayment(models.Model):
    bond_id = models.ForeignKey(GovernmentBondPrimary, on_delete=models.CASCADE)
    receipting_manager = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    date_received = models.DateField()
    amount_received = models.DecimalField(max_digits=15, decimal_places=2)
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('bank_transfer', 'Bank Transfer'),
            ('cheque', 'Cheque')
        ]
    )

    def __str__(self):
        return f"Coupon Payment {self.amount_received} on {self.date_received}"


class TreasuryBill(models.Model):
    t_bill_id = models.CharField(max_length=50)
    start_date = models.DateField()
    maturity_date = models.DateField()
    principal_amount = models.DecimalField(max_digits=15, decimal_places=2)
    maturity_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default="zmw", choices=[("zmw", "ZMW"), ("usd", "USD")])
    t_bill_rating = models.CharField(
        max_length=50,
        choices=[
            ('Aaa', 'Aaa'),
            ('Aa', 'Aa'),
            ('A', 'A'),
            ('Baa', 'Baa'),
            ('Ba', 'Ba'),
            ('B', 'B'),
            ('Caa-C', 'Caa-C'),
        ],
        default='Caa-C'
    )
    counterparty = models.CharField(
        max_length=50,
        choices=[
            ('absa', 'ABSA'),
            ('fnb', 'FNB'),
            ('zanaco', 'ZANACO'),
            ('napsa', "NAPSA"),
        ],
    )
    counterparty_type = models.CharField(max_length=50, default="Sovereign", editable=False)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)

    def clean(self):
        if self.maturity_date <= self.start_date:
            raise ValidationError('Maturity date must be after the start date.')

    def tenure(self):
        return (self.maturity_date - self.start_date).days

    def elapsed_term(self, date):
        return (date - self.start_date).days

    def remaining_term(self, date):
        remaining = (self.maturity_date - date).days
        return remaining if remaining > 0 else 0

    def accrued_principal(self, date):
        if date < self.start_date:
            return Decimal(0)
        elif date > self.maturity_date:
            return self.maturity_amount
        else:
            return self.principal_amount + (self.maturity_amount - self.principal_amount) * Decimal(self.elapsed_term(date)) / Decimal(self.tenure())

    def accrued_interest(self, date):
        if date < self.start_date:
            return Decimal(0)
        elif date > self.maturity_date:
            return self.maturity_amount - self.principal_amount
        else:
            return (self.maturity_amount - self.principal_amount) * Decimal(self.elapsed_term(date)) / Decimal(self.tenure())

    def EAD(self, date):
        if date < self.start_date or date > self.maturity_date:
            return Decimal(0)
        return self.accrued_principal(date)

    def PD(self):
        return Decimal(PD_SOVEREIGN_MOODYS[self.t_bill_rating])

    def ECL(self, date):
        if date < self.start_date or date > self.maturity_date:
            return Decimal(0)
        if self.remaining_term(date) >= 364:
            return self.PD() * Decimal(LGD) * self.EAD(date)
        else:
            return self.PD() * Decimal(self.remaining_term(date)) / Decimal(365) * Decimal(LGD) * self.EAD(date)

    def get_manager_full_name(self):
        return f"{self.manager.first_name} {self.manager.last_name}"

    def __str__(self):
        return self.t_bill_id


class CorporateBond(models.Model):
    bond_id = models.CharField(max_length=50)
    counterparty = models.CharField(
        max_length=50,
        choices=[
            ('bayport', 'Bayport'),
            ('reiz', 'REIZ'),
            ('ifc', 'IFC'),
        ]
    )
    start_date = models.DateField()
    maturity_date = models.DateField()
    principal_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default="zmw", choices=[('zmw', 'ZMW'), ('usd', 'USD')])
    interest_rate = models.DecimalField(max_digits=6, decimal_places=4)
    bond_rating = models.CharField(
        max_length=50,
        choices=[
            ('Aaa', 'Aaa'),
            ('Aa', 'Aa'),
            ('A', 'A'),
            ('Baa', 'Baa'),
            ('Ba', 'Ba'),
            ('B', 'B'),
            ('Caa-C', 'Caa-C'),
        ]
    )
    counterparty_type = models.CharField(max_length=50, default="Corporate", editable=False)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)

    def clean(self):
        if self.maturity_date <= self.start_date:
            raise ValidationError('Maturity date must be after the start date.')

    def tenure(self):
        return (self.maturity_date - self.start_date).days

    def maturity_amount(self):
        return self.principal_amount + self.interest_rate / Decimal(100) * self.principal_amount * Decimal(self.tenure()) / Decimal(365)

    def elapsed_term(self, date):
        return (date - self.start_date).days

    def remaining_term(self, date):
        remaining = (self.maturity_date - date).days
        return remaining if remaining > 0 else 0

    def accrued_principal(self, date):
        if date < self.start_date:
            return Decimal(0)
        elif date > self.maturity_date:
            return self.maturity_amount()
        else:
            return self.principal_amount + self.interest_rate / Decimal(100) * self.principal_amount * Decimal(self.elapsed_term(date)) / Decimal(365)

    def accrued_interest(self, date):
        if date < self.start_date:
            return Decimal(0)
        elif date > self.maturity_date:
            return self.maturity_amount() - self.principal_amount
        else:
            return self.interest_rate / Decimal(100) * self.principal_amount * Decimal(self.elapsed_term(date)) / Decimal(365)

    def EAD(self, date):
        if date < self.start_date or date > self.maturity_date:
            return Decimal(0)
        return self.accrued_principal(date)

    def PD(self):
        return Decimal(PD_CORPORATE_MOODYS[self.bond_rating])

    def ECL(self, date):
        if date < self.start_date or date > self.maturity_date:
            return Decimal(0)
        if self.remaining_term(date) >= 364:
            return self.PD() * Decimal(LGD) * self.EAD(date)
        else:
            return self.PD() * Decimal(self.remaining_term(date)) / Decimal(365) * Decimal(LGD) * self.EAD(date)

    def get_manager_full_name(self):
        return f"{self.manager.first_name} {self.manager.last_name}"

    def __str__(self):
        return self.bond_id


class FixedTermDeposit(models.Model):
    fxd_id = models.CharField(max_length=50)
    start_date = models.DateField()
    maturity_date = models.DateField()
    principal_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, choices=[('zmw', 'ZMW'), ('usd', 'USD')])
    interest_rate = models.DecimalField(max_digits=6, decimal_places=4)
    bank_rating = models.CharField(
        max_length=50,
        choices=[
            ('Aaa', 'Aaa'),
            ('Aa', 'Aa'),
            ('A', 'A'),
            ('Baa', 'Baa'),
            ('Ba', 'Ba'),
            ('B', 'B'),
            ('Caa-C', 'Caa-C'),
        ]
    )
    counterparty = models.CharField(
        max_length=50,
        choices=[
            ('ab_bank', 'AB Bank'),
            ('absa', 'ABSA'),
            ('access_bank', 'Access Bank'),
            ('atlas_mara', 'Atlas Mara'),
            ('ecobank', "Ecobank"),
            ('efc', 'EFC'),
            ('first_alliance', 'First Alliance'),
            ('fmc', 'FMC'),
            ('fnb', 'FNB'),
            ('indo', 'Indo Zambia Bank'),
            ('izwe', 'IZWE'),
            ('lion_finance', 'Lion Finance'),
            ('lolc', 'LOLC'),
            ('mfz', 'MFZ'),
            ('stanbic', 'Stanbic Bank'),
            ('zanaco', 'ZANACO'),
        ]
    )
    counterparty_type = models.CharField(max_length=50, default="Corporate", editable=False)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)

    def clean(self):
        if self.maturity_date <= self.start_date:
            raise ValidationError('Maturity date must be after the start date.')

    def tenure(self):
        return (self.maturity_date - self.start_date).days

    def maturity(self):
        return self.principal_amount * (1 + self.interest_rate / Decimal(100)) ** (Decimal(self.tenure()) / Decimal(365))

    def elapsed_term(self, date):
        return (date - self.start_date).days
    
    def remaining_term(self, date):
        remaining = (self.maturity_date - date).days
        return remaining if remaining > 0 else 0

    def accrued_principal(self, date):
        if date < self.start_date:
            return Decimal(0)
        elif date > self.maturity_date:
            return self.maturity()
        else:
            return self.principal_amount * (1 + self.interest_rate / Decimal(100)) ** (Decimal(self.elapsed_term(date)) / Decimal(365))

    def accrued_interest(self, date):
        if date < self.start_date:
            return Decimal(0)
        elif date > self.maturity_date:
            return self.maturity() - self.principal_amount
        else:
            return self.principal_amount * (1 + self.interest_rate / Decimal(100)) ** (Decimal(self.elapsed_term(date)) / Decimal(365)) - self.principal_amount

    def EAD(self, date):
        if date < self.start_date or date > self.maturity_date:
            return Decimal(0)
        return self.accrued_principal(date)

    def PD(self):
        return Decimal(PD_CORPORATE_MOODYS[self.bank_rating])

    def ECL(self, date):
        if date < self.start_date or date > self.maturity_date:
            return Decimal(0)
        if self.remaining_term(date) >= 365:
            return self.PD() * Decimal(LGD) * self.EAD(date)
        else:
            return self.PD() * Decimal(self.remaining_term(date)) / Decimal(365) * Decimal(LGD) * self.EAD(date)

    def get_manager_full_name(self):
        return f"{self.manager.first_name} {self.manager.last_name}"

    def __str__(self):
        return self.fxd_id
