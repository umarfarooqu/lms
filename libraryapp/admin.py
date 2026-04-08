from django.contrib import admin, messages

from .models import BarcodeRecord, Book, BookIssue


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "book_code", "title", "author", "program_code", "available_copies", "total_copies")
    search_fields = ("book_code", "title", "author", "program_code")


@admin.action(description="Delete selected barcode records")
def delete_selected_barcodes(modeladmin, request, queryset):
    count, _ = queryset.delete()
    modeladmin.message_user(request, f"Deleted {count} barcode records.", level=messages.SUCCESS)


@admin.action(description="Delete all unused barcode records")
def delete_unused_barcodes(modeladmin, request, queryset):
    unused_qs = BarcodeRecord.objects.filter(is_used=False)
    count, _ = unused_qs.delete()
    modeladmin.message_user(request, f"Deleted {count} unused barcode records.", level=messages.SUCCESS)


@admin.register(BarcodeRecord)
class BarcodeRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "is_used", "book", "created_at")
    search_fields = ("code", "book__title", "book__book_code")
    list_filter = ("is_used",)
    actions = [delete_selected_barcodes, delete_unused_barcodes]


@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = ("id", "book", "student_name", "student_id", "issued_at", "returned_at")
    search_fields = ("student_name", "student_id", "book__title", "book__book_code")
    list_filter = ("returned_at",)
