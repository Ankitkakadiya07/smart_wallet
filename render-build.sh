#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies one by one to handle potential issues
pip install Django==4.2.16
pip install python-decouple==3.8
pip install whitenoise==6.6.0
pip install gunicorn==21.2.0
pip install dj-database-url==2.1.0

# Try to install psycopg2-binary, fallback to psycopg2 if it fails
pip install psycopg2-binary==2.9.9 || pip install psycopg2==2.9.9

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