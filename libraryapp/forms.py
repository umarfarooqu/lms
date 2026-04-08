from django import forms

from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author"]


class IssueForm(forms.Form):
    book = forms.ModelChoiceField(queryset=Book.objects.none(), empty_label="Select book")
    student_name = forms.CharField(max_length=120, required=False)
    student_id = forms.CharField(max_length=50, required=False)
    employee_name = forms.CharField(max_length=120, required=False)
    employee_id = forms.CharField(max_length=50, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["book"].queryset = Book.objects.filter(available_copies__gt=0).order_by("title")


class BarcodeGenerateForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=5000)


class BarcodeExcelUploadForm(forms.Form):
    file = forms.FileField()
