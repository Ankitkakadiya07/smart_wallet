from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, timedelta
from .forms import IncomeForm, ExpenseForm
from .models import Category


class IncomeFormTest(TestCase):
    """Test cases for IncomeForm validation and functionality"""
    
    def setUp(self):
        """Set up test categories"""
        self.salary_category, _ = Category.objects.get_or_create(name='Salary')
        self.business_category, _ = Category.objects.get_or_create(name='Business')
    
    def test_valid_income_form(self):
        """Test that valid income form data passes validation"""
        form_data = {
            'category': self.salary_category.id,
            'source': 'Test Job',
            'amount': '5000.00',
            'date': date.today().strftime('%Y-%m-%d'),
            'note': 'Monthly salary'
        }
        
        form = IncomeForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form should be valid but has errors: {form.errors}")
    
    def test_income_form_negative_amount(self):
        """Test that negative amounts are rejected"""
        form_data = {
            'category': self.salary_category.id,
            'source': 'Test Job',
            'amount': '-100.00',
            'date': date.today().strftime('%Y-%m-%d')
        }
        
        form = IncomeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
    
    def test_income_form_zero_amount(self):
        """Test that zero amounts are rejected"""
        form_data = {
            'category': self.salary_category.id,
            'source': 'Test Job',
            'amount': '0.00',
            'date': date.today().strftime('%Y-%m-%d')
        }
        
        form = IncomeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
    
    def test_income_form_empty_source(self):
        """Test that empty source is rejected"""
        form_data = {
            'category': self.salary_category.id,
            'source': '',
            'amount': '1000.00',
            'date': date.today().strftime('%Y-%m-%d')
        }
        
        form = IncomeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('source', form.errors)
    
    def test_income_form_whitespace_source(self):
        """Test that whitespace-only source is rejected"""
        form_data = {
            'category': self.salary_category.id,
            'source': '   ',
            'amount': '1000.00',
            'date': date.today().strftime('%Y-%m-%d')
        }
        
        form = IncomeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('source', form.errors)
    
    def test_income_form_short_source(self):
        """Test that very short source is rejected"""
        form_data = {
            'category': self.salary_category.id,
            'source': 'A',
            'amount': '1000.00',
            'date': date.today().strftime('%Y-%m-%d')
        }
        
        form = IncomeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('source', form.errors)
    
    def test_income_form_future_date_validation(self):
        """Test that far future dates are rejected"""
        future_date = date.today().replace(year=date.today().year + 2)
        form_data = {
            'category': self.salary_category.id,
            'source': 'Test Job',
            'amount': '1000.00',
            'date': future_date.strftime('%Y-%m-%d')
        }
        
        form = IncomeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)
    
    def test_income_form_reasonable_future_date(self):
        """Test that reasonable future dates are accepted"""
        future_date = date.today() + timedelta(days=30)
        form_data = {
            'category': self.salary_category.id,
            'source': 'Test Job',
            'amount': '1000.00',
            'date': future_date.strftime('%Y-%m-%d')
        }
        
        form = IncomeForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form should be valid but has errors: {form.errors}")
    
    def test_income_form_excessive_amount(self):
        """Test that excessive amounts are rejected"""
        form_data = {
            'category': self.salary_category.id,
            'source': 'Test Job',
            'amount': '999999999.99',
            'date': date.today().strftime('%Y-%m-%d')
        }
        
        form = IncomeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)


class ExpenseFormTest(TestCase):
    """Test cases for ExpenseForm validation and functionality"""
    
    def test_valid_expense_form(self):
        """Test that valid expense form data passes validation"""
        form_data = {
            'title': 'Office Supplies',
            'amount': '250.00',
            'date': date.today().strftime('%Y-%m-%d')
        }
        
        form = ExpenseForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form should be valid but has errors: {form.errors}")
    
    def test_expense_form_negative_amount(self):
        """Test that negative amounts are rejected"""
        form_data = {
            'title': 'Test Expense',
            'amount': '-50.00',
            'date': date.today().strftime('%Y-%m-%d')
        }
        
        form = ExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
    
    def test_expense_form_zero_amount(self):
        """Test that zero amounts are rejected"""
        form_data = {
            'title': 'Test Expense',
            'amount': '0.00',
            'date': date.today().strftime('%Y-%m-%d')
        }
        
        form = ExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
    
    def test_expense_form_empty_title(self):
        """Test that empty title is rejected"""
        form_data = {
            'title': '',
            'amount': '100.00',
            'date': date.today().strftime('%Y-%m-%d')
        }
        
        form = ExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_expense_form_whitespace_title(self):
        """Test that whitespace-only title is rejected"""
        form_data = {
            'title': '   ',
            'amount': '100.00',
            'date': date.today().strftime('%Y-%m-%d')
        }
        
        form = ExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_expense_form_short_title(self):
        """Test that very short title is rejected"""
        form_data = {
            'title': 'A',
            'amount': '100.00',
            'date': date.today().strftime('%Y-%m-%d')
        }
        
        form = ExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_expense_form_future_date_validation(self):
        """Test that far future dates are rejected"""
        future_date = date.today().replace(year=date.today().year + 2)
        form_data = {
            'title': 'Test Expense',
            'amount': '100.00',
            'date': future_date.strftime('%Y-%m-%d')
        }
        
        form = ExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)
    
    def test_expense_form_reasonable_future_date(self):
        """Test that reasonable future dates are accepted"""
        future_date = date.today() + timedelta(days=30)
        form_data = {
            'title': 'Test Expense',
            'amount': '100.00',
            'date': future_date.strftime('%Y-%m-%d')
        }
        
        form = ExpenseForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form should be valid but has errors: {form.errors}")
    
    def test_expense_form_excessive_amount(self):
        """Test that excessive amounts are rejected"""
        form_data = {
            'title': 'Test Expense',
            'amount': '999999999.99',
            'date': date.today().strftime('%Y-%m-%d')
        }
        
        form = ExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)


class FormInitializationTest(TestCase):
    """Test form initialization and default values"""
    
    def setUp(self):
        """Set up test categories"""
        self.salary_category, _ = Category.objects.get_or_create(name='Salary')
    
    def test_income_form_default_date(self):
        """Test that income form initializes with today's date"""
        form = IncomeForm()
        self.assertEqual(form.fields['date'].initial, date.today())
    
    def test_expense_form_default_date(self):
        """Test that expense form initializes with today's date"""
        form = ExpenseForm()
        self.assertEqual(form.fields['date'].initial, date.today())
    
    def test_income_form_widget_attributes(self):
        """Test that income form has proper widget attributes"""
        form = IncomeForm()
        
        # Check that form fields have proper CSS classes
        self.assertIn('form-control', form.fields['source'].widget.attrs['class'])
        self.assertIn('form-control', form.fields['amount'].widget.attrs['class'])
        self.assertIn('form-control', form.fields['date'].widget.attrs['class'])
        self.assertIn('form-control', form.fields['note'].widget.attrs['class'])
        self.assertIn('form-select', form.fields['category'].widget.attrs['class'])
        
        # Check that required fields are marked as required
        self.assertTrue(form.fields['source'].widget.attrs['required'])
        self.assertTrue(form.fields['amount'].widget.attrs['required'])
        self.assertTrue(form.fields['date'].widget.attrs['required'])
        self.assertTrue(form.fields['category'].widget.attrs['required'])
    
    def test_expense_form_widget_attributes(self):
        """Test that expense form has proper widget attributes"""
        form = ExpenseForm()
        
        # Check that form fields have proper CSS classes
        self.assertIn('form-control', form.fields['title'].widget.attrs['class'])
        self.assertIn('form-control', form.fields['amount'].widget.attrs['class'])
        self.assertIn('form-control', form.fields['date'].widget.attrs['class'])
        
        # Check that required fields are marked as required
        self.assertTrue(form.fields['title'].widget.attrs['required'])
        self.assertTrue(form.fields['amount'].widget.attrs['required'])
        self.assertTrue(form.fields['date'].widget.attrs['required'])