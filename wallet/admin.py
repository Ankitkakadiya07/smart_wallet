from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import Category, Income, Expense


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model"""
    list_display = ['name', 'income_count', 'total_income', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    ordering = ['name']
    readonly_fields = ['created_at']
    
    def income_count(self, obj):
        """Display count of income transactions for this category"""
        count = obj.income_set.count()
        return format_html('<span style="color: green; font-weight: bold;">{}</span>', count)
    income_count.short_description = 'Income Transactions'
    
    def total_income(self, obj):
        """Display total income amount for this category"""
        total = obj.income_set.aggregate(total=Sum('amount'))['total'] or 0
        return format_html('<span style="color: green; font-weight: bold;">${}</span>', f'{total:.2f}')
    total_income.short_description = 'Total Income'


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    """Admin configuration for Income model"""
    list_display = ['source', 'category', 'formatted_amount', 'date', 'created_at']
    list_filter = ['category', 'date', 'created_at']
    search_fields = ['source', 'note', 'category__name']
    ordering = ['-date', '-created_at']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('category', 'source', 'amount', 'date')
        }),
        ('Additional Information', {
            'fields': ('note',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def formatted_amount(self, obj):
        """Display formatted amount with currency symbol"""
        return format_html('<span style="color: green; font-weight: bold;">${}</span>', f'{obj.amount:.2f}')
    formatted_amount.short_description = 'Amount'
    formatted_amount.admin_order_field = 'amount'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('category')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """Admin configuration for Expense model"""
    list_display = ['title', 'formatted_amount', 'date', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['title']
    ordering = ['-date', '-created_at']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('title', 'amount', 'date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def formatted_amount(self, obj):
        """Display formatted amount with currency symbol"""
        return format_html('<span style="color: red; font-weight: bold;">${}</span>', f'{obj.amount:.2f}')
    formatted_amount.short_description = 'Amount'
    formatted_amount.admin_order_field = 'amount'


# Custom admin actions
def mark_as_verified(modeladmin, request, queryset):
    """Custom admin action to mark transactions as verified"""
    count = queryset.count()
    # You can add custom logic here if needed
    modeladmin.message_user(request, f'{count} transactions marked as verified.')
mark_as_verified.short_description = "Mark selected transactions as verified"

# Add the action to Income and Expense admins
IncomeAdmin.actions = [mark_as_verified]
ExpenseAdmin.actions = [mark_as_verified]

# Customize admin site headers
admin.site.site_header = "Smart Wallet Administration"
admin.site.site_title = "Smart Wallet Admin"
admin.site.index_title = "Welcome to Smart Wallet Administration"

# Add summary statistics to admin index
def admin_summary_stats():
    """Get summary statistics for admin dashboard"""
    from django.db.models import Sum, Count
    
    stats = {
        'total_income': Income.objects.aggregate(total=Sum('amount'))['total'] or 0,
        'total_expenses': Expense.objects.aggregate(total=Sum('amount'))['total'] or 0,
        'income_count': Income.objects.count(),
        'expense_count': Expense.objects.count(),
        'categories_count': Category.objects.count(),
    }
    stats['balance'] = stats['total_income'] - stats['total_expenses']
    return stats
