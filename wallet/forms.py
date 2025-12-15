from django import forms
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date
from .models import Income, Expense, Category


class IncomeForm(forms.ModelForm):
    """Form for creating and editing income transactions"""
    
    class Meta:
        model = Income
        fields = ['category', 'source', 'amount', 'date', 'note']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'source': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter income source',
                'required': True,
                'maxlength': 100
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Optional notes about this income',
                'rows': 3
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default date to today if creating new income
        if not self.instance.pk:
            self.fields['date'].initial = date.today()
    
    def clean_amount(self):
        """Custom validation for amount field"""
        amount = self.cleaned_data.get('amount')
        if amount is not None:
            if amount <= 0:
                raise ValidationError("Amount must be greater than zero.")
            if amount > Decimal('99999999.99'):
                raise ValidationError("Amount cannot exceed $99,999,999.99.")
        return amount
    
    def clean_source(self):
        """Custom validation for source field"""
        source = self.cleaned_data.get('source')
        if source:
            source = source.strip()
            if not source:
                raise ValidationError("Source cannot be empty or contain only spaces.")
            if len(source) < 2:
                raise ValidationError("Source must be at least 2 characters long.")
        return source
    
    def clean_date(self):
        """Custom validation for date field"""
        transaction_date = self.cleaned_data.get('date')
        if transaction_date:
            # Allow future dates but warn if too far in the future
            if transaction_date > date.today().replace(year=date.today().year + 1):
                raise ValidationError("Date cannot be more than one year in the future.")
        return transaction_date


class ExpenseForm(forms.ModelForm):
    """Form for creating and editing expense transactions"""
    
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter expense title',
                'required': True,
                'maxlength': 100
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default date to today if creating new expense
        if not self.instance.pk:
            self.fields['date'].initial = date.today()
    
    def clean_amount(self):
        """Custom validation for amount field"""
        amount = self.cleaned_data.get('amount')
        if amount is not None:
            if amount <= 0:
                raise ValidationError("Amount must be greater than zero.")
            if amount > Decimal('99999999.99'):
                raise ValidationError("Amount cannot exceed $99,999,999.99.")
        return amount
    
    def clean_title(self):
        """Custom validation for title field"""
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip()
            if not title:
                raise ValidationError("Title cannot be empty or contain only spaces.")
            if len(title) < 2:
                raise ValidationError("Title must be at least 2 characters long.")
        return title
    
    def clean_date(self):
        """Custom validation for date field"""
        transaction_date = self.cleaned_data.get('date')
        if transaction_date:
            # Allow future dates but warn if too far in the future
            if transaction_date > date.today().replace(year=date.today().year + 1):
                raise ValidationError("Date cannot be more than one year in the future.")
        return transaction_date


# Custom validators that can be reused
def validate_positive_amount(value):
    """Validator to ensure amount is positive"""
    if value <= 0:
        raise ValidationError("Amount must be greater than zero.")


def validate_reasonable_date(value):
    """Validator to ensure date is reasonable"""
    if value > date.today().replace(year=date.today().year + 1):
        raise ValidationError("Date cannot be more than one year in the future.")


def validate_non_empty_string(value):
    """Validator to ensure string is not empty after stripping whitespace"""
    if not value or not value.strip():
        raise ValidationError("This field cannot be empty or contain only spaces.")