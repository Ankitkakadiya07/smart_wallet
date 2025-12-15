#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create superuser if it doesn't exist
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"

# Create default categories if they don't exist
python manage.py shell -c "
from wallet.models import Category
categories = ['Salary', 'Business', 'Freelancing', 'Investment']
for cat_name in categories:
    category, created = Category.objects.get_or_create(name=cat_name)
    if created:
        print(f'Created category: {cat_name}')
    else:
        print(f'Category already exists: {cat_name}')
"