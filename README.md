# Library Management System (Django)

Student-oriented Library Management System built with Django.

## Features
- Add books
- View/search books
- Issue a book to a student
- Return issued books
- View active issues by student ID
- Django admin for managing records

## Requirements
- Python 3.8+
- Django 4.2+

## Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Open: http://127.0.0.1:8000/

Admin panel:
```bash
python manage.py createsuperuser
```
Then open: http://127.0.0.1:8000/admin/
