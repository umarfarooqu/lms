import random
from datetime import datetime, timedelta
from django.utils import timezone
from libraryapp.models import Book, BookIssue

# Delete previous demo records
deleted, _ = BookIssue.objects.filter(employee_name__in=[
    'Umar Farooque','Ayesha Alam','Sudhakar Kumar','Shakti Nath Singh','Divya Prabha','Ashika Sawli'
]).delete()
deleted2, _ = BookIssue.objects.filter(student_name__in=[
    'Umar Farooque','Ayesha Alam','Sudhakar Kumar','Shakti Nath Singh','Divya Prabha','Ashika Sawli'
]).delete()
print("Deleted", deleted + deleted2, "old records")

employees = [
    ('Umar Farooque', 'EMP2024001'),
    ('Ayesha Alam', 'EMP2024002'),
    ('Sudhakar Kumar', 'EMP2024003'),
    ('Shakti Nath Singh', 'EMP2024004'),
    ('Divya Prabha', 'EMP2024005'),
    ('Ashika Sawli', 'EMP2024006'),
]

books = list(Book.objects.all())
start_date = datetime(2024, 8, 1, tzinfo=timezone.UTC)
end_date = datetime(2026, 4, 1, tzinfo=timezone.UTC)

created = 0
for name, eid in employees:
    num_issues = random.randint(3, 6)
    used_books = random.sample(books, min(num_issues, len(books)))
    for book in used_books:
        issue_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        is_returned = random.random() > 0.3
        returned_date = None
        if is_returned:
            returned_date = issue_date + timedelta(days=random.randint(1, 365))
            if returned_date > end_date:
                returned_date = None
        issue = BookIssue.objects.create(
            book=book,
            employee_name=name,
            employee_id=eid,
            returned_at=returned_date,
        )
        # auto_now_add bypassed via update
        BookIssue.objects.filter(pk=issue.pk).update(issued_at=issue_date)
        created += 1

print("Created", created, "issue records")
