from django.urls import path

from . import views

urlpatterns = [
    path("librarian/login/", views.librarian_login, name="librarian_login"),
    path("librarian/logout/", views.librarian_logout, name="librarian_logout"),
    path("", views.book_list, name="book_list"),
    path("add-book/", views.add_book, name="add_book"),
    path("issue-book/", views.issue_book, name="issue_book"),
    path("return-book/", views.return_book_by_code, name="return_book_by_code"),
    path("return-book/<int:issue_id>/", views.return_book, name="return_book"),
    path("student-issues/", views.student_issues, name="student_issues"),
    path("barcode-module/", views.barcode_module, name="barcode_module"),
    path("barcode-module/generate/", views.generate_barcodes, name="generate_barcodes"),
    path("barcode-module/export/", views.export_barcode_sheet, name="export_barcode_sheet"),
    path("barcode-module/upload/", views.upload_barcode_sheet, name="upload_barcode_sheet"),
    path("barcode-module/print-unused-a4/", views.print_barcodes_a4, name="print_barcodes_a4"),
    path("search-module/", views.search_module, name="search_module"),
    path("reports-module/", views.reports_module, name="reports_module"),
    path("reports-module/export/<str:report_type>/", views.export_report_csv, name="export_report_csv"),
    path("issue-log/", views.issue_log, name="issue_log"),
]
