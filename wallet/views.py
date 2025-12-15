from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.db.models import Sum, Q
from django.db import models
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from decimal import Decimal
import json
import csv
from datetime import datetime
from .models import Income, Expense, Category
from .forms import IncomeForm, ExpenseForm

# Create your views here.

class DashboardView(TemplateView):
    """Dashboard view for financial overview"""
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        """Add financial summary data to template context"""
        context = super().get_context_data(**kwargs)
        
        # Calculate financial totals
        context['total_income'] = self.calculate_total_income()
        context['total_expenses'] = self.calculate_total_expenses()
        context['current_balance'] = self.calculate_balance(
            context['total_income'], 
            context['total_expenses']
        )
        
        # Get recent transactions for display
        context['recent_income'] = self.get_recent_income()
        context['recent_expenses'] = self.get_recent_expenses()
        
        return context
    
    def calculate_total_income(self):
        """Calculate total income from all income transactions"""
        total = Income.objects.aggregate(
            total=Sum('amount')
        )['total']
        return total if total is not None else Decimal('0.00')
    
    def calculate_total_expenses(self):
        """Calculate total expenses from all expense transactions"""
        total = Expense.objects.aggregate(
            total=Sum('amount')
        )['total']
        return total if total is not None else Decimal('0.00')
    
    def calculate_balance(self, total_income, total_expenses):
        """Calculate current financial balance (income - expenses)"""
        return total_income - total_expenses
    
    def get_recent_income(self, limit=5):
        """Get recent income transactions for dashboard display"""
        return Income.objects.select_related('category').order_by('-date', '-created_at')[:limit]
    
    def get_recent_expenses(self, limit=5):
        """Get recent expense transactions for dashboard display"""
        return Expense.objects.order_by('-date', '-created_at')[:limit]

class IncomeListView(ListView):
    """List view for displaying all income records"""
    model = Income
    template_name = 'income/income_list.html'
    context_object_name = 'income_list'
    paginate_by = 10
    
    def get_queryset(self):
        """Get income transactions with search and filter functionality"""
        queryset = Income.objects.select_related('category').order_by('-date', '-created_at')
        
        # Return base queryset if no request (for testing)
        if not hasattr(self, 'request') or not self.request:
            return queryset
        
        # Search functionality
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                models.Q(source__icontains=search_query) |
                models.Q(note__icontains=search_query) |
                models.Q(category__name__icontains=search_query)
            )
        
        # Category filter
        category_filter = self.request.GET.get('category', '').strip()
        if category_filter:
            queryset = queryset.filter(category__name=category_filter)
        
        # Date range filter
        date_from = self.request.GET.get('date_from', '').strip()
        date_to = self.request.GET.get('date_to', '').strip()
        
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=to_date)
            except ValueError:
                pass
        
        # Amount range filter
        amount_min = self.request.GET.get('amount_min', '').strip()
        amount_max = self.request.GET.get('amount_max', '').strip()
        
        if amount_min:
            try:
                min_amount = Decimal(amount_min)
                queryset = queryset.filter(amount__gte=min_amount)
            except (ValueError, TypeError):
                pass
        
        if amount_max:
            try:
                max_amount = Decimal(amount_max)
                queryset = queryset.filter(amount__lte=max_amount)
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add additional context for the template"""
        context = super().get_context_data(**kwargs)
        
        # Calculate totals for filtered results
        filtered_queryset = self.get_queryset()
        context['total_income'] = filtered_queryset.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        context['filtered_count'] = filtered_queryset.count()
        
        # Add filter context (handle case when no request)
        if hasattr(self, 'request') and self.request:
            context['search_query'] = self.request.GET.get('search', '')
            context['category_filter'] = self.request.GET.get('category', '')
            context['date_from'] = self.request.GET.get('date_from', '')
            context['date_to'] = self.request.GET.get('date_to', '')
            context['amount_min'] = self.request.GET.get('amount_min', '')
            context['amount_max'] = self.request.GET.get('amount_max', '')
        else:
            context['search_query'] = ''
            context['category_filter'] = ''
            context['date_from'] = ''
            context['date_to'] = ''
            context['amount_min'] = ''
            context['amount_max'] = ''
        
        # Add categories for filter dropdown
        context['categories'] = Category.objects.all().order_by('name')
        
        return context


class IncomeCreateView(CreateView):
    """Create view for adding new income transactions"""
    model = Income
    form_class = IncomeForm
    template_name = 'income/income_form.html'
    success_url = reverse_lazy('wallet:income_list')
    
    def form_valid(self, form):
        """Handle successful form submission"""
        messages.success(self.request, 'Income transaction created successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors"""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Add context for template"""
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Add New Income'
        context['submit_text'] = 'Create Income'
        return context


class IncomeUpdateView(UpdateView):
    """Update view for editing existing income records"""
    model = Income
    form_class = IncomeForm
    template_name = 'income/income_form.html'
    success_url = reverse_lazy('wallet:income_list')
    
    def form_valid(self, form):
        """Handle successful form submission"""
        messages.success(self.request, 'Income transaction updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors"""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Add context for template"""
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Income: {self.object.source}'
        context['submit_text'] = 'Update Income'
        return context


class IncomeDeleteView(DeleteView):
    """Delete view for removing income transactions"""
    model = Income
    template_name = 'income/income_confirm_delete.html'
    success_url = reverse_lazy('wallet:income_list')
    context_object_name = 'income'
    
    def delete(self, request, *args, **kwargs):
        """Handle successful deletion"""
        messages.success(request, 'Income transaction deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Add context for template"""
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('wallet:income_list')
        return context

class ExpenseListView(ListView):
    """List view for displaying all expense records"""
    model = Expense
    template_name = 'expense/expense_list.html'
    context_object_name = 'expense_list'
    paginate_by = 10
    
    def get_queryset(self):
        """Get expense transactions with search and filter functionality"""
        queryset = Expense.objects.order_by('-date', '-created_at')
        
        # Return base queryset if no request (for testing)
        if not hasattr(self, 'request') or not self.request:
            return queryset
        
        # Search functionality
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                models.Q(title__icontains=search_query)
            )
        
        # Date range filter
        date_from = self.request.GET.get('date_from', '').strip()
        date_to = self.request.GET.get('date_to', '').strip()
        
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=to_date)
            except ValueError:
                pass
        
        # Amount range filter
        amount_min = self.request.GET.get('amount_min', '').strip()
        amount_max = self.request.GET.get('amount_max', '').strip()
        
        if amount_min:
            try:
                min_amount = Decimal(amount_min)
                queryset = queryset.filter(amount__gte=min_amount)
            except (ValueError, TypeError):
                pass
        
        if amount_max:
            try:
                max_amount = Decimal(amount_max)
                queryset = queryset.filter(amount__lte=max_amount)
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add additional context for the template"""
        context = super().get_context_data(**kwargs)
        
        # Calculate totals for filtered results
        filtered_queryset = self.get_queryset()
        context['total_expenses'] = filtered_queryset.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        context['filtered_count'] = filtered_queryset.count()
        
        # Add filter context (handle case when no request)
        if hasattr(self, 'request') and self.request:
            context['search_query'] = self.request.GET.get('search', '')
            context['date_from'] = self.request.GET.get('date_from', '')
            context['date_to'] = self.request.GET.get('date_to', '')
            context['amount_min'] = self.request.GET.get('amount_min', '')
            context['amount_max'] = self.request.GET.get('amount_max', '')
        else:
            context['search_query'] = ''
            context['date_from'] = ''
            context['date_to'] = ''
            context['amount_min'] = ''
            context['amount_max'] = ''
        
        return context


class ExpenseCreateView(CreateView):
    """Create view for adding new expense transactions"""
    model = Expense
    form_class = ExpenseForm
    template_name = 'expense/expense_form.html'
    success_url = reverse_lazy('wallet:expense_list')
    
    def form_valid(self, form):
        """Handle successful form submission"""
        messages.success(self.request, 'Expense transaction created successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors"""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Add context for template"""
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Add New Expense'
        context['submit_text'] = 'Create Expense'
        return context


class ExpenseUpdateView(UpdateView):
    """Update view for editing existing expense records"""
    model = Expense
    form_class = ExpenseForm
    template_name = 'expense/expense_form.html'
    success_url = reverse_lazy('wallet:expense_list')
    
    def form_valid(self, form):
        """Handle successful form submission"""
        messages.success(self.request, 'Expense transaction updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors"""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Add context for template"""
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Expense: {self.object.title}'
        context['submit_text'] = 'Update Expense'
        return context


class ExpenseDeleteView(DeleteView):
    """Delete view for removing expense transactions"""
    model = Expense
    template_name = 'expense/expense_confirm_delete.html'
    success_url = reverse_lazy('wallet:expense_list')
    context_object_name = 'expense'
    
    def delete(self, request, *args, **kwargs):
        """Handle successful deletion"""
        messages.success(request, 'Expense transaction deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Add context for template"""
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('wallet:expense_list')
        return context

@method_decorator(csrf_exempt, name='dispatch')
class DashboardDataAPIView(View):
    """API view for dashboard data refresh"""
    
    def get(self, request):
        """Get updated dashboard data as JSON"""
        try:
            # Calculate financial totals
            total_income = Income.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            current_balance = total_income - total_expenses
            
            # Get recent transactions
            recent_income = Income.objects.select_related('category').order_by('-date', '-created_at')[:5]
            recent_expenses = Expense.objects.order_by('-date', '-created_at')[:5]
            
            # Combine and sort recent transactions
            recent_transactions = []
            
            for income in recent_income:
                recent_transactions.append({
                    'id': income.id,
                    'type': 'income',
                    'title': income.source,
                    'category': income.category.name,
                    'amount': float(income.amount),
                    'date': income.date.isoformat(),
                    'note': income.note or ''
                })
            
            for expense in recent_expenses:
                recent_transactions.append({
                    'id': expense.id,
                    'type': 'expense',
                    'title': expense.title,
                    'category': 'Expense',
                    'amount': float(expense.amount),
                    'date': expense.date.isoformat(),
                    'note': ''
                })
            
            # Sort by date (newest first)
            recent_transactions.sort(key=lambda x: x['date'], reverse=True)
            recent_transactions = recent_transactions[:10]  # Limit to 10 most recent
            
            return JsonResponse({
                'status': 'success',
                'totalIncome': float(total_income),
                'totalExpenses': float(total_expenses),
                'currentBalance': float(current_balance),
                'recent_transactions': recent_transactions
            }, status=200)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to retrieve dashboard data: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class IncomeAPIView(View):
    """API view for income AJAX operations"""
    
    def get(self, request, pk=None):
        """Get income transactions as JSON"""
        try:
            if pk:
                # Get single income transaction
                try:
                    income = Income.objects.select_related('category').get(pk=pk)
                    return JsonResponse({
                        'status': 'success',
                        'data': {
                            'id': income.id,
                            'source': income.source,
                            'category': {
                                'id': income.category.id,
                                'name': income.category.name
                            },
                            'amount': float(income.amount),
                            'date': income.date.isoformat(),
                            'note': income.note or '',
                            'created_at': income.created_at.isoformat(),
                            'updated_at': income.updated_at.isoformat()
                        }
                    }, status=200)
                except Income.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Income transaction not found'
                    }, status=404)
            else:
                # Get all income transactions
                income_list = Income.objects.select_related('category').order_by('-date', '-created_at')
                
                transactions = []
                for income in income_list:
                    transactions.append({
                        'id': income.id,
                        'source': income.source,
                        'category': {
                            'id': income.category.id,
                            'name': income.category.name
                        },
                        'amount': float(income.amount),
                        'date': income.date.isoformat(),
                        'note': income.note or '',
                        'created_at': income.created_at.isoformat(),
                        'updated_at': income.updated_at.isoformat()
                    })
                
                total_income = Income.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                
                return JsonResponse({
                    'status': 'success',
                    'transactions': transactions,
                    'stats': {
                        'total': float(total_income),
                        'count': len(transactions)
                    }
                }, status=200)
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to retrieve income data: {str(e)}'
            }, status=500)
    
    def post(self, request):
        """Create new income transaction via AJAX"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['category_id', 'source', 'amount', 'date']
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Missing required field: {field}'
                    }, status=400)
            
            # Get category
            try:
                category = Category.objects.get(pk=data['category_id'])
            except Category.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid category ID'
                }, status=400)
            
            # Parse and validate date
            try:
                transaction_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid date format. Use YYYY-MM-DD'
                }, status=400)
            
            # Validate amount
            try:
                amount = Decimal(str(data['amount']))
                if amount <= 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Amount must be greater than zero'
                    }, status=400)
            except (ValueError, TypeError):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid amount format'
                }, status=400)
            
            # Create income transaction
            income = Income.objects.create(
                category=category,
                source=data['source'].strip(),
                amount=amount,
                date=transaction_date,
                note=data.get('note', '').strip()
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Income transaction created successfully',
                'data': {
                    'id': income.id,
                    'source': income.source,
                    'category': {
                        'id': income.category.id,
                        'name': income.category.name
                    },
                    'amount': float(income.amount),
                    'date': income.date.isoformat(),
                    'note': income.note or '',
                    'created_at': income.created_at.isoformat()
                }
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to create income transaction: {str(e)}'
            }, status=500)
    
    def put(self, request, pk):
        """Update income transaction via AJAX"""
        try:
            data = json.loads(request.body)
            
            # Get income transaction
            try:
                income = Income.objects.get(pk=pk)
            except Income.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Income transaction not found'
                }, status=404)
            
            # Update fields if provided
            if 'category_id' in data:
                try:
                    category = Category.objects.get(pk=data['category_id'])
                    income.category = category
                except Category.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid category ID'
                    }, status=400)
            
            if 'source' in data:
                if not data['source'].strip():
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Source cannot be empty'
                    }, status=400)
                income.source = data['source'].strip()
            
            if 'amount' in data:
                try:
                    amount = Decimal(str(data['amount']))
                    if amount <= 0:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Amount must be greater than zero'
                        }, status=400)
                    income.amount = amount
                except (ValueError, TypeError):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid amount format'
                    }, status=400)
            
            if 'date' in data:
                try:
                    income.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                except ValueError:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid date format. Use YYYY-MM-DD'
                    }, status=400)
            
            if 'note' in data:
                income.note = data['note'].strip()
            
            income.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Income transaction updated successfully',
                'data': {
                    'id': income.id,
                    'source': income.source,
                    'category': {
                        'id': income.category.id,
                        'name': income.category.name
                    },
                    'amount': float(income.amount),
                    'date': income.date.isoformat(),
                    'note': income.note or '',
                    'updated_at': income.updated_at.isoformat()
                }
            }, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to update income transaction: {str(e)}'
            }, status=500)
    
    def delete(self, request, pk):
        """Delete income transaction via AJAX"""
        try:
            income = Income.objects.get(pk=pk)
            income_data = {
                'id': income.id,
                'source': income.source,
                'amount': float(income.amount)
            }
            income.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Income transaction deleted successfully',
                'data': income_data
            }, status=200)
            
        except Income.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Income transaction not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to delete income transaction: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ExpenseAPIView(View):
    """API view for expense AJAX operations"""
    
    def get(self, request, pk=None):
        """Get expense transactions as JSON"""
        try:
            if pk:
                # Get single expense transaction
                try:
                    expense = Expense.objects.get(pk=pk)
                    return JsonResponse({
                        'status': 'success',
                        'data': {
                            'id': expense.id,
                            'title': expense.title,
                            'amount': float(expense.amount),
                            'date': expense.date.isoformat(),
                            'created_at': expense.created_at.isoformat(),
                            'updated_at': expense.updated_at.isoformat()
                        }
                    }, status=200)
                except Expense.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Expense transaction not found'
                    }, status=404)
            else:
                # Get all expense transactions
                expense_list = Expense.objects.order_by('-date', '-created_at')
                
                transactions = []
                for expense in expense_list:
                    transactions.append({
                        'id': expense.id,
                        'title': expense.title,
                        'amount': float(expense.amount),
                        'date': expense.date.isoformat(),
                        'created_at': expense.created_at.isoformat(),
                        'updated_at': expense.updated_at.isoformat()
                    })
                
                total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                
                return JsonResponse({
                    'status': 'success',
                    'transactions': transactions,
                    'stats': {
                        'total': float(total_expenses),
                        'count': len(transactions)
                    }
                }, status=200)
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to retrieve expense data: {str(e)}'
            }, status=500)
    
    def post(self, request):
        """Create new expense transaction via AJAX"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['title', 'amount', 'date']
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Missing required field: {field}'
                    }, status=400)
            
            # Parse and validate date
            try:
                transaction_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid date format. Use YYYY-MM-DD'
                }, status=400)
            
            # Validate amount
            try:
                amount = Decimal(str(data['amount']))
                if amount <= 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Amount must be greater than zero'
                    }, status=400)
            except (ValueError, TypeError):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid amount format'
                }, status=400)
            
            # Create expense transaction
            expense = Expense.objects.create(
                title=data['title'].strip(),
                amount=amount,
                date=transaction_date
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Expense transaction created successfully',
                'data': {
                    'id': expense.id,
                    'title': expense.title,
                    'amount': float(expense.amount),
                    'date': expense.date.isoformat(),
                    'created_at': expense.created_at.isoformat()
                }
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to create expense transaction: {str(e)}'
            }, status=500)
    
    def put(self, request, pk):
        """Update expense transaction via AJAX"""
        try:
            data = json.loads(request.body)
            
            # Get expense transaction
            try:
                expense = Expense.objects.get(pk=pk)
            except Expense.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Expense transaction not found'
                }, status=404)
            
            # Update fields if provided
            if 'title' in data:
                if not data['title'].strip():
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Title cannot be empty'
                    }, status=400)
                expense.title = data['title'].strip()
            
            if 'amount' in data:
                try:
                    amount = Decimal(str(data['amount']))
                    if amount <= 0:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Amount must be greater than zero'
                        }, status=400)
                    expense.amount = amount
                except (ValueError, TypeError):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid amount format'
                    }, status=400)
            
            if 'date' in data:
                try:
                    expense.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                except ValueError:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid date format. Use YYYY-MM-DD'
                    }, status=400)
            
            expense.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Expense transaction updated successfully',
                'data': {
                    'id': expense.id,
                    'title': expense.title,
                    'amount': float(expense.amount),
                    'date': expense.date.isoformat(),
                    'updated_at': expense.updated_at.isoformat()
                }
            }, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to update expense transaction: {str(e)}'
            }, status=500)
    
    def delete(self, request, pk):
        """Delete expense transaction via AJAX"""
        try:
            expense = Expense.objects.get(pk=pk)
            expense_data = {
                'id': expense.id,
                'title': expense.title,
                'amount': float(expense.amount)
            }
            expense.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Expense transaction deleted successfully',
                'data': expense_data
            }, status=200)
            
        except Expense.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Expense transaction not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to delete expense transaction: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class TransactionAPIView(View):
    """API view for general transaction operations"""
    
    def get(self, request):
        """Get all transactions as JSON"""
        try:
            # Get all income and expense transactions
            income_list = Income.objects.select_related('category').order_by('-date', '-created_at')
            expense_list = Expense.objects.order_by('-date', '-created_at')
            
            transactions = []
            
            # Add income transactions
            for income in income_list:
                transactions.append({
                    'id': income.id,
                    'type': 'income',
                    'title': income.source,
                    'category': {
                        'id': income.category.id,
                        'name': income.category.name
                    },
                    'amount': float(income.amount),
                    'date': income.date.isoformat(),
                    'note': income.note or '',
                    'created_at': income.created_at.isoformat(),
                    'updated_at': income.updated_at.isoformat()
                })
            
            # Add expense transactions
            for expense in expense_list:
                transactions.append({
                    'id': expense.id,
                    'type': 'expense',
                    'title': expense.title,
                    'category': {
                        'id': None,
                        'name': 'Expense'
                    },
                    'amount': float(expense.amount),
                    'date': expense.date.isoformat(),
                    'note': '',
                    'created_at': expense.created_at.isoformat(),
                    'updated_at': expense.updated_at.isoformat()
                })
            
            # Sort by date (newest first)
            transactions.sort(key=lambda x: x['date'], reverse=True)
            
            # Calculate totals
            total_income = Income.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            return JsonResponse({
                'status': 'success',
                'transactions': transactions,
                'stats': {
                    'totalIncome': float(total_income),
                    'totalExpenses': float(total_expenses),
                    'currentBalance': float(total_income - total_expenses),
                    'totalTransactions': len(transactions)
                }
            }, status=200)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to retrieve transaction data: {str(e)}'
            }, status=500)
    
    def post(self, request):
        """Create new transaction via AJAX (supports both income and expense)"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            if 'type' not in data or data['type'] not in ['income', 'expense']:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid or missing transaction type. Must be "income" or "expense"'
                }, status=400)
            
            transaction_type = data['type']
            
            if transaction_type == 'income':
                # Handle income creation
                required_fields = ['amount', 'description']
                for field in required_fields:
                    if field not in data or not data[field]:
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Missing required field: {field}'
                        }, status=400)
                
                # Get default category (Salary) or create if not exists
                category, created = Category.objects.get_or_create(name='Salary')
                
                # Parse and validate amount
                try:
                    amount = Decimal(str(data['amount']))
                    if amount <= 0:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Amount must be greater than zero'
                        }, status=400)
                except (ValueError, TypeError):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid amount format'
                    }, status=400)
                
                # Create income transaction
                income = Income.objects.create(
                    category=category,
                    source=data['description'].strip(),
                    amount=amount,
                    date=datetime.now().date(),
                    note=data.get('note', '').strip()
                )
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Income transaction created successfully',
                    'data': {
                        'id': income.id,
                        'type': 'income',
                        'title': income.source,
                        'amount': float(income.amount),
                        'date': income.date.isoformat(),
                        'created_at': income.created_at.isoformat()
                    }
                }, status=200)
                
            elif transaction_type == 'expense':
                # Handle expense creation
                required_fields = ['amount', 'description']
                for field in required_fields:
                    if field not in data or not data[field]:
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Missing required field: {field}'
                        }, status=400)
                
                # Parse and validate amount
                try:
                    amount = Decimal(str(data['amount']))
                    if amount <= 0:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Amount must be greater than zero'
                        }, status=400)
                except (ValueError, TypeError):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid amount format'
                    }, status=400)
                
                # Create expense transaction
                expense = Expense.objects.create(
                    title=data['description'].strip(),
                    amount=amount,
                    date=datetime.now().date()
                )
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Expense transaction created successfully',
                    'data': {
                        'id': expense.id,
                        'type': 'expense',
                        'title': expense.title,
                        'amount': float(expense.amount),
                        'date': expense.date.isoformat(),
                        'created_at': expense.created_at.isoformat()
                    }
                }, status=200)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to create transaction: {str(e)}'
            }, status=500)
    
    def put(self, request):
        """Update transaction via AJAX (supports both income and expense)"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            if 'id' not in data:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Missing required field: id'
                }, status=400)
            
            transaction_id = data['id']
            
            # Try to find the transaction in both income and expense tables
            income_transaction = None
            expense_transaction = None
            
            try:
                income_transaction = Income.objects.get(pk=transaction_id)
            except Income.DoesNotExist:
                try:
                    expense_transaction = Expense.objects.get(pk=transaction_id)
                except Expense.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Transaction not found'
                    }, status=404)
            
            if income_transaction:
                # Update income transaction
                if 'amount' in data:
                    try:
                        amount = Decimal(str(data['amount']))
                        if amount <= 0:
                            return JsonResponse({
                                'status': 'error',
                                'message': 'Amount must be greater than zero'
                            }, status=400)
                        income_transaction.amount = amount
                    except (ValueError, TypeError):
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Invalid amount format'
                        }, status=400)
                
                if 'description' in data:
                    if not data['description'].strip():
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Description cannot be empty'
                        }, status=400)
                    income_transaction.source = data['description'].strip()
                
                income_transaction.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Income transaction updated successfully',
                    'data': {
                        'id': income_transaction.id,
                        'type': 'income',
                        'title': income_transaction.source,
                        'amount': float(income_transaction.amount),
                        'updated_at': income_transaction.updated_at.isoformat()
                    }
                }, status=200)
                
            elif expense_transaction:
                # Update expense transaction
                if 'amount' in data:
                    try:
                        amount = Decimal(str(data['amount']))
                        if amount <= 0:
                            return JsonResponse({
                                'status': 'error',
                                'message': 'Amount must be greater than zero'
                            }, status=400)
                        expense_transaction.amount = amount
                    except (ValueError, TypeError):
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Invalid amount format'
                        }, status=400)
                
                if 'description' in data:
                    if not data['description'].strip():
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Description cannot be empty'
                        }, status=400)
                    expense_transaction.title = data['description'].strip()
                
                expense_transaction.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Expense transaction updated successfully',
                    'data': {
                        'id': expense_transaction.id,
                        'type': 'expense',
                        'title': expense_transaction.title,
                        'amount': float(expense_transaction.amount),
                        'updated_at': expense_transaction.updated_at.isoformat()
                    }
                }, status=200)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to update transaction: {str(e)}'
            }, status=500)
    
    def delete(self, request):
        """Delete transaction via AJAX (supports both income and expense)"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            if 'id' not in data:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Missing required field: id'
                }, status=400)
            
            transaction_id = data['id']
            
            # Try to find the transaction in both income and expense tables
            income_transaction = None
            expense_transaction = None
            
            try:
                income_transaction = Income.objects.get(pk=transaction_id)
            except Income.DoesNotExist:
                try:
                    expense_transaction = Expense.objects.get(pk=transaction_id)
                except Expense.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Transaction not found'
                    }, status=404)
            
            if income_transaction:
                # Delete income transaction
                transaction_data = {
                    'id': income_transaction.id,
                    'type': 'income',
                    'title': income_transaction.source,
                    'amount': float(income_transaction.amount)
                }
                income_transaction.delete()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Income transaction deleted successfully',
                    'data': transaction_data
                }, status=200)
                
            elif expense_transaction:
                # Delete expense transaction
                transaction_data = {
                    'id': expense_transaction.id,
                    'type': 'expense',
                    'title': expense_transaction.title,
                    'amount': float(expense_transaction.amount)
                }
                expense_transaction.delete()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Expense transaction deleted successfully',
                    'data': transaction_data
                }, status=200)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to delete transaction: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CategoryAPIView(View):
    """API view for category operations"""
    
    def get(self, request):
        """Get all categories as JSON"""
        try:
            categories = Category.objects.all().order_by('name')
            
            category_list = []
            for category in categories:
                category_list.append({
                    'id': category.id,
                    'name': category.name,
                    'created_at': category.created_at.isoformat()
                })
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'categories': category_list,
                    'count': len(category_list)
                }
            }, status=200)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to retrieve categories: {str(e)}'
            }, status=500)


class ExportDataView(View):
    """Export financial data to CSV format"""
    
    def get(self, request):
        """Export transactions to CSV"""
        export_type = request.GET.get('type', 'all')  # all, income, expense
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        # Create HTTP response with CSV content type
        response = HttpResponse(content_type='text/csv')
        
        if export_type == 'income':
            response['Content-Disposition'] = 'attachment; filename="income_transactions.csv"'
            self._export_income_csv(response, date_from, date_to)
        elif export_type == 'expense':
            response['Content-Disposition'] = 'attachment; filename="expense_transactions.csv"'
            self._export_expense_csv(response, date_from, date_to)
        else:
            response['Content-Disposition'] = 'attachment; filename="all_transactions.csv"'
            self._export_all_csv(response, date_from, date_to)
        
        return response
    
    def _export_income_csv(self, response, date_from, date_to):
        """Export income transactions to CSV"""
        writer = csv.writer(response)
        writer.writerow(['Date', 'Category', 'Source', 'Amount', 'Note', 'Created At'])
        
        queryset = Income.objects.select_related('category').order_by('-date')
        
        # Apply date filters
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=to_date)
            except ValueError:
                pass
        
        for income in queryset:
            writer.writerow([
                income.date.strftime('%Y-%m-%d'),
                income.category.name,
                income.source,
                str(income.amount),
                income.note or '',
                income.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
    
    def _export_expense_csv(self, response, date_from, date_to):
        """Export expense transactions to CSV"""
        writer = csv.writer(response)
        writer.writerow(['Date', 'Title', 'Amount', 'Created At'])
        
        queryset = Expense.objects.order_by('-date')
        
        # Apply date filters
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=to_date)
            except ValueError:
                pass
        
        for expense in queryset:
            writer.writerow([
                expense.date.strftime('%Y-%m-%d'),
                expense.title,
                str(expense.amount),
                expense.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
    
    def _export_all_csv(self, response, date_from, date_to):
        """Export all transactions to CSV"""
        writer = csv.writer(response)
        writer.writerow(['Date', 'Type', 'Category', 'Title/Source', 'Amount', 'Note', 'Created At'])
        
        # Get income transactions
        income_queryset = Income.objects.select_related('category').order_by('-date')
        expense_queryset = Expense.objects.order_by('-date')
        
        # Apply date filters
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                income_queryset = income_queryset.filter(date__gte=from_date)
                expense_queryset = expense_queryset.filter(date__gte=from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                income_queryset = income_queryset.filter(date__lte=to_date)
                expense_queryset = expense_queryset.filter(date__lte=to_date)
            except ValueError:
                pass
        
        # Combine and sort transactions
        transactions = []
        
        for income in income_queryset:
            transactions.append({
                'date': income.date,
                'type': 'Income',
                'category': income.category.name,
                'title': income.source,
                'amount': income.amount,
                'note': income.note or '',
                'created_at': income.created_at
            })
        
        for expense in expense_queryset:
            transactions.append({
                'date': expense.date,
                'type': 'Expense',
                'category': 'Expense',
                'title': expense.title,
                'amount': -expense.amount,  # Negative for expenses
                'note': '',
                'created_at': expense.created_at
            })
        
        # Sort by date (newest first)
        transactions.sort(key=lambda x: x['date'], reverse=True)
        
        for transaction in transactions:
            writer.writerow([
                transaction['date'].strftime('%Y-%m-%d'),
                transaction['type'],
                transaction['category'],
                transaction['title'],
                str(transaction['amount']),
                transaction['note'],
                transaction['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            ])


class SearchAPIView(View):
    """API view for advanced search functionality"""
    
    def get(self, request):
        """Perform search across income and expense transactions"""
        try:
            query = request.GET.get('q', '').strip()
            transaction_type = request.GET.get('type', 'all')  # all, income, expense
            limit = int(request.GET.get('limit', 10))
            
            results = []
            
            if not query:
                return JsonResponse({
                    'status': 'success',
                    'results': [],
                    'message': 'No search query provided'
                })
            
            if transaction_type in ['all', 'income']:
                # Search income transactions
                income_results = Income.objects.select_related('category').filter(
                    Q(source__icontains=query) |
                    Q(note__icontains=query) |
                    Q(category__name__icontains=query)
                ).order_by('-date')[:limit]
                
                for income in income_results:
                    results.append({
                        'id': income.id,
                        'type': 'income',
                        'title': income.source,
                        'category': income.category.name,
                        'amount': float(income.amount),
                        'date': income.date.isoformat(),
                        'note': income.note or '',
                        'url': f'/income/{income.id}/edit/'
                    })
            
            if transaction_type in ['all', 'expense']:
                # Search expense transactions
                expense_results = Expense.objects.filter(
                    Q(title__icontains=query)
                ).order_by('-date')[:limit]
                
                for expense in expense_results:
                    results.append({
                        'id': expense.id,
                        'type': 'expense',
                        'title': expense.title,
                        'category': 'Expense',
                        'amount': float(expense.amount),
                        'date': expense.date.isoformat(),
                        'note': '',
                        'url': f'/expense/{expense.id}/edit/'
                    })
            
            # Sort results by date
            results.sort(key=lambda x: x['date'], reverse=True)
            
            return JsonResponse({
                'status': 'success',
                'results': results[:limit],
                'count': len(results),
                'query': query
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Search failed: {str(e)}'
            }, status=500)
