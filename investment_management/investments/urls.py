from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    # path('about/', views.about, name='about'),
    path('register/', views.register_user, name='register'),
    path('select_investment/', views.select_investment, name='select_investment'),
    path('expected_returns/', views.expected_returns, name='expected_returns'),
    path('expected_credit_loss/', views.ecl_metrics, name='ecl_metrics'),
    path('add_government_bond/', views.add_government_bond, name='add_govt_bond'),
    path('add_treasury_bill/', views.add_treasury_bill, name='add_t_bill'),
    path('add_corporate_bond/', views.add_corporate_bond, name='add_corporate_bond'),
    path('add_fixed_deposit/', views.add_fixed_deposit, name='add_fixed_deposit'),
    path('all_government_bonds/', views.all_government_bonds, name='all_govt_bonds'),
    path('all_treasury_bills/', views.all_treasury_bills, name='all_t_bills'),
    path('all_corporate_bonds/', views.all_corporate_bonds, name='all_corporate_bonds'),
    path('all_fixed_deposits/', views.all_fixed_deposits, name='all_fixed_deposits'),
    path('download/csv/<str:model_name>/', views.download_model_csv, name='download_model_csv'),
    path('download/excel/<str:model_name>/', views.download_model_excel, name='download_model_excel'),
]