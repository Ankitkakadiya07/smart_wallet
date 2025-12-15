from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Income URLs
    path('income/', views.IncomeListView.as_view(), name='income_list'),
    path('income/add/', views.IncomeCreateView.as_view(), name='income_create'),
    path('income/<int:pk>/edit/', views.IncomeUpdateView.as_view(), name='income_update'),
    path('income/<int:pk>/delete/', views.IncomeDeleteView.as_view(), name='income_delete'),
    
    # Expense URLs
    path('expense/', views.ExpenseListView.as_view(), name='expense_list'),
    path('expense/add/', views.ExpenseCreateView.as_view(), name='expense_create'),
    path('expense/<int:pk>/edit/', views.ExpenseUpdateView.as_view(), name='expense_update'),
    path('expense/<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='expense_delete'),
    
    # API endpoints for AJAX operations
    path('api/dashboard-data/', views.DashboardDataAPIView.as_view(), name='api_dashboard_data'),
    path('api/transactions/', views.TransactionAPIView.as_view(), name='api_transactions'),
    
    # Income API endpoints
    path('api/income/', views.IncomeAPIView.as_view(), name='api_income_list'),
    path('api/income/<int:pk>/', views.IncomeAPIView.as_view(), name='api_income_detail'),
    
    # Expense API endpoints
    path('api/expense/', views.ExpenseAPIView.as_view(), name='api_expense_list'),
    path('api/expenses/', views.ExpenseAPIView.as_view(), name='api_expenses'),
    path('api/expense/<int:pk>/', views.ExpenseAPIView.as_view(), name='api_expense_detail'),
    
    # Category API endpoints
    path('api/categories/', views.CategoryAPIView.as_view(), name='api_categories'),
    
    # Export functionality
    path('export/', views.ExportDataView.as_view(), name='export_data'),
    
    # Search API
    path('api/search/', views.SearchAPIView.as_view(), name='api_search'),
]