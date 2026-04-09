from urllib.parse import quote

from django.db import models
from django.utils import timezone


def _to_numeric_code(value):
    if not value:
        return None
    text = str(value).strip()
    if text.isdigit() and text.startswith("18"):
        return int(text)
    return None


class Book(models.Model):
    CODE_START = 18000000001

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=120)
    program_code = models.CharField(max_length=20, default="18")
    book_code = models.CharField(max_length=40, unique=True, blank=True, null=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.book_code} - {self.title}"

    def _generate_book_code(self):
        next_code = BarcodeRecord.get_next_code_number(start=self.CODE_START)
        self.book_code = str(next_code)
        self.program_code = "18"

    @property
    def barcode_url(self):
        return (
            "https://quickchart.io/barcode"
            f"?text={quote(self.book_code)}&format=png&type=code128&width=320&height=90&showtext=true"
        )

    def save(self, *args, **kwargs):
        if not self.book_code:
            self._generate_book_code()
        super().save(*args, **kwargs)


class BarcodeRecord(models.Model):
    code = models.CharField(max_length=40, unique=True)
    is_used = models.BooleanField(default=False)
    book = models.OneToOneField(Book, null=True, blank=True, on_delete=models.SET_NULL, related_name="barcode_record")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} ({'used' if self.is_used else 'free'})"

    @property
    def barcode_url(self):
        return (
            "https://quickchart.io/barcode"
            f"?text={quote(self.code)}&format=png&type=code128&width=320&height=90&showtext=true"
        )

    @classmethod
    def get_next_code_number(cls, start=18000000001):
        max_code = start - 1

        for code in Book.objects.exclude(book_code__isnull=True).values_list("book_code", flat=True):
            numeric = _to_numeric_code(code)
            if numeric and numeric > max_code:
                max_code = numeric

        for code in cls.objects.values_list("code", flat=True):
            numeric = _to_numeric_code(code)
            if numeric and numeric > max_code:
                max_code = numeric

        return max_code + 1 if max_code >= start else start

    def mark_used(self, book):
        self.book = book
        self.is_used = True
        self.save(update_fields=["book", "is_used"])


class BookIssue(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="issues")
    student_name = models.CharField(max_length=120, blank=True, default="")
    student_id = models.CharField(max_length=50, blank=True, default="")
    employee_name = models.CharField(max_length=120, blank=True, default="")
    employee_id = models.CharField(max_length=50, blank=True, default="")
    subject = models.CharField(max_length=200, blank=True, default="")
    issued_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-issued_at"]

    def __str__(self):
        name = self.student_name or self.employee_name
        return f"{name} -> {self.book.title}"

    @property
    def is_returned(self):
        return self.returned_at is not None

    def mark_returned(self):
        if self.returned_at is None:
            self.returned_at = timezone.now()
            self.save(update_fields=["returned_at"])
