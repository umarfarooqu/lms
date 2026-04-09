import openpyxl
from django.core.management.base import BaseCommand, CommandError

from libraryapp.models import BarcodeRecord, Book


class Command(BaseCommand):
    help = "Import books from an Excel file (.xlsx)"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to the Excel file")
        parser.add_argument(
            "--sheet",
            type=str,
            default=None,
            help="Sheet name (defaults to the first sheet)",
        )

    def handle(self, *args, **options):
        path = options["file"]
        sheet_name = options["sheet"]

        try:
            wb = openpyxl.load_workbook(path, data_only=True)
        except FileNotFoundError:
            raise CommandError(f"File not found: {path}")

        ws = wb[sheet_name] if sheet_name else wb.active

        created = 0
        skipped = 0
        errors = 0

        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            # Expected columns: S.No., Barcode, Book Name, Author Name
            if len(row) < 4:
                continue

            _, barcode, title, author = row[0], row[1], row[2], row[3]

            barcode = str(barcode).strip() if barcode else ""
            title = str(title).strip() if title else ""
            author = str(author).strip() if author else ""

            if not title or not barcode:
                self.stderr.write(f"  Row {row_idx}: skipping — missing title or barcode")
                skipped += 1
                continue

            if Book.objects.filter(book_code=barcode).exists():
                self.stdout.write(f"  Row {row_idx}: already exists ({barcode}), skipping")
                skipped += 1
                continue

            try:
                book = Book.objects.create(
                    title=title,
                    author=author,
                    book_code=barcode,
                    program_code="18",
                    total_copies=1,
                    available_copies=1,
                )
                # Register barcode record
                BarcodeRecord.objects.get_or_create(
                    code=barcode,
                    defaults={"is_used": True, "book": book},
                )
                created += 1
                self.stdout.write(f"  Created: [{barcode}] {title}")
            except Exception as exc:
                self.stderr.write(f"  Row {row_idx}: ERROR — {exc}")
                errors += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created: {created} | Skipped: {skipped} | Errors: {errors}"
            )
        )
