from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import random
from wallet.models import Category, Income, Expense


class Command(BaseCommand):
    help = 'Populate the database with sample financial data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--income-count',
            type=int,
            default=10,
            help='Number of sample income transactions to create'
        )
        parser.add_argument(
            '--expense-count',
            type=int,
            default=8,
            help='Number of sample expense transactions to create'
        )

    def handle(self, *args, **options):
        income_count = options['income_count']
        expense_count = options['expense_count']

        self.stdout.write('Creating sample data...')

        # Sample income sources
        income_sources = [
            'Salary - Tech Corp',
            'Freelance Project',
            'Consulting Work',
            'Side Business',
            'Investment Returns',
            'Bonus Payment',
            'Contract Work',
            'Part-time Job',
            'Rental Income',
            'Dividend Payment'
        ]

        # Sample expense titles
        expense_titles = [
            'Grocery Shopping',
            'Gas Station',
            'Restaurant Dinner',
            'Coffee Shop',
            'Online Shopping',
            'Utility Bill',
            'Phone Bill',
            'Internet Bill',
            'Movie Tickets',
            'Gym Membership'
        ]

        # Create sample income transactions
        categories = list(Category.objects.all())
        created_income = 0

        for i in range(income_count):
            try:
                Income.objects.create(
                    category=random.choice(categories),
                    source=random.choice(income_sources),
                    amount=Decimal(str(round(random.uniform(100, 5000), 2))),
                    date=date.today() - timedelta(days=random.randint(0, 90)),
                    note=f'Sample income transaction #{i+1}' if random.choice([True, False]) else ''
                )
                created_income += 1
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Failed to create income #{i+1}: {e}')
                )

        # Create sample expense transactions
        created_expenses = 0

        for i in range(expense_count):
            try:
                Expense.objects.create(
                    title=random.choice(expense_titles),
                    amount=Decimal(str(round(random.uniform(10, 500), 2))),
                    date=date.today() - timedelta(days=random.randint(0, 90))
                )
                created_expenses += 1
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Failed to create expense #{i+1}: {e}')
                )

        # Display summary
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_income} income transactions '
                f'and {created_expenses} expense transactions'
            )
        )

        # Show current totals
        total_income = Income.objects.count()
        total_expenses = Expense.objects.count()
        
        self.stdout.write(f'Total income transactions in database: {total_income}')
        self.stdout.write(f'Total expense transactions in database: {total_expenses}')