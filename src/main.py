import json
from datetime import date
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "library_data.json"

LIBRARIAN_ID = "lib001"
LIBRARIAN_PASSWORD = "lib123"


class LibrarySystem:
    def __init__(self, data_file: Path):
        self.data_file = data_file
        self.data = {
            "next_book_id": 1,
            "books": [],
            "issues": [],
            "teachers": [],
            "students": [],
        }
        self._load()

    def _load(self):
        if self.data_file.exists():
            with self.data_file.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
                # ensure new keys exist in old data files
                for key in self.data:
                    if key not in loaded:
                        loaded[key] = self.data[key]
                self.data = loaded
        else:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            self._save()

    def _save(self):
        with self.data_file.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    # ── User management ──────────────────────────────────────────────────────

    def register_user(self, role: str, name: str, user_id: str, password: str):
        collection = self.data[role + "s"]  # "teachers" or "students"
        if any(u["id"] == user_id for u in collection):
            raise ValueError(f"{role.capitalize()} ID '{user_id}' already exists.")
        collection.append({"name": name.strip(), "id": user_id.strip(), "password": password})
        self._save()

    def login_user(self, role: str, user_id: str, password: str):
        collection = self.data[role + "s"]
        for u in collection:
            if u["id"] == user_id.strip() and u["password"] == password:
                return u
        return None

    # ── Book management ───────────────────────────────────────────────────────

    def add_book(self, title: str, author: str, copies: int):
        if copies <= 0:
            raise ValueError("Copies must be greater than 0.")
        book = {
            "id": self.data["next_book_id"],
            "title": title.strip(),
            "author": author.strip(),
            "total_copies": copies,
            "available_copies": copies,
        }
        self.data["books"].append(book)
        self.data["next_book_id"] += 1
        self._save()
        return book

    def list_books(self):
        return self.data["books"]

    def search_books(self, keyword: str):
        key = keyword.strip().lower()
        return [
            b for b in self.data["books"]
            if key in b["title"].lower() or key in b["author"].lower()
        ]

    def _find_book(self, book_id: int):
        for book in self.data["books"]:
            if book["id"] == book_id:
                return book
        return None

    # ── Issue / Return ────────────────────────────────────────────────────────

    def issue_book(self, book_id: int, borrower_role: str, borrower_name: str, borrower_id: str):
        book = self._find_book(book_id)
        if not book:
            raise ValueError("Book not found.")
        if book["available_copies"] <= 0:
            raise ValueError("No copies available for this book.")

        issue = {
            "book_id": book_id,
            "borrower_role": borrower_role,       # "teacher" or "student"
            "borrower_name": borrower_name.strip(),
            "borrower_id": borrower_id.strip(),
            "issue_date": str(date.today()),
            "return_date": None,
            "returned": False,
        }
        self.data["issues"].append(issue)
        book["available_copies"] -= 1
        self._save()

    def return_book(self, book_id: int, borrower_id: str):
        book = self._find_book(book_id)
        if not book:
            raise ValueError("Book not found.")

        for issue in self.data["issues"]:
            if (
                issue["book_id"] == book_id
                and issue["borrower_id"] == borrower_id.strip()
                and not issue["returned"]
            ):
                issue["returned"] = True
                issue["return_date"] = str(date.today())
                book["available_copies"] += 1
                self._save()
                return

        raise ValueError("No active issue record found for this ID and book.")

    def books_by_borrower(self, borrower_id: str):
        active = [
            i for i in self.data["issues"]
            if i["borrower_id"] == borrower_id.strip() and not i["returned"]
        ]
        result = []
        for issue in active:
            book = self._find_book(issue["book_id"])
            if book:
                result.append({**book, "issue_date": issue["issue_date"]})
        return result

    def all_active_issues(self):
        return [i for i in self.data["issues"] if not i["returned"]]


# ── Print helpers ─────────────────────────────────────────────────────────────

def print_books(books):
    if not books:
        print("  No books found.")
        return
    print(f"\n  {'ID':<5} {'Title':<30} {'Author':<20} {'Available/Total'}")
    print("  " + "-" * 65)
    for b in books:
        issued = f"  [Issued: {b['issue_date']}]" if "issue_date" in b else ""
        print(f"  {b['id']:<5} {b['title']:<30} {b['author']:<20} {b['available_copies']}/{b['total_copies']}{issued}")


def print_issues(issues):
    if not issues:
        print("  No active issues.")
        return
    print(f"\n  {'Book ID':<8} {'Borrower':<20} {'Role':<10} {'ID':<12} {'Issue Date'}")
    print("  " + "-" * 65)
    for i in issues:
        print(f"  {i['book_id']:<8} {i['borrower_name']:<20} {i['borrower_role']:<10} {i['borrower_id']:<12} {i['issue_date']}")


# ── Menus ─────────────────────────────────────────────────────────────────────

def librarian_menu(system: LibrarySystem):
    while True:
        print("\n===== Librarian Panel =====")
        print("1. Add Book")
        print("2. View All Books")
        print("3. Search Book")
        print("4. Issue Book")
        print("5. Return Book")
        print("6. View All Active Issues")
        print("7. Register Teacher")
        print("8. Register Student")
        print("9. Logout")

        choice = input("Enter choice (1-9): ").strip()

        try:
            if choice == "1":
                title = input("Title: ")
                author = input("Author: ")
                copies = int(input("Number of copies: "))
                book = system.add_book(title, author, copies)
                print(f"  Book added with ID {book['id']}.")

            elif choice == "2":
                print_books(system.list_books())

            elif choice == "3":
                keyword = input("Keyword (title/author): ")
                print_books(system.search_books(keyword))

            elif choice == "4":
                book_id = int(input("Book ID: "))
                print("  Issue to: 1. Teacher  2. Student")
                rc = input("  Choose (1/2): ").strip()
                role = "teacher" if rc == "1" else "student"
                borrower_name = input("Borrower Name: ")
                borrower_id = input("Borrower ID: ")
                system.issue_book(book_id, role, borrower_name, borrower_id)
                print("  Book issued successfully.")

            elif choice == "5":
                book_id = int(input("Book ID: "))
                borrower_id = input("Borrower ID: ")
                system.return_book(book_id, borrower_id)
                print("  Book returned successfully.")

            elif choice == "6":
                print_issues(system.all_active_issues())

            elif choice == "7":
                name = input("Teacher Name: ")
                uid = input("Teacher ID: ")
                pwd = input("Password: ")
                system.register_user("teacher", name, uid, pwd)
                print("  Teacher registered.")

            elif choice == "8":
                name = input("Student Name: ")
                uid = input("Student ID: ")
                pwd = input("Password: ")
                system.register_user("student", name, uid, pwd)
                print("  Student registered.")

            elif choice == "9":
                print("  Logging out...")
                break

            else:
                print("  Invalid choice.")

        except ValueError as e:
            print(f"  Error: {e}")


def borrower_menu(system: LibrarySystem, user: dict, role: str):
    print(f"\n  Welcome, {user['name']}! ({role.capitalize()})")

    while True:
        print(f"\n===== {role.capitalize()} Panel =====")
        print("1. View All Books")
        print("2. Search Book")
        print("3. My Borrowed Books")
        print("4. Logout")

        choice = input("Enter choice (1-4): ").strip()

        try:
            if choice == "1":
                print_books(system.list_books())

            elif choice == "2":
                keyword = input("Keyword (title/author): ")
                print_books(system.search_books(keyword))

            elif choice == "3":
                print_books(system.books_by_borrower(user["id"]))

            elif choice == "4":
                print("  Logging out...")
                break

            else:
                print("  Invalid choice.")

        except ValueError as e:
            print(f"  Error: {e}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    system = LibrarySystem(DATA_FILE)

    while True:
        print("\n========================================")
        print("     Library Management System")
        print("========================================")
        print("1. Librarian Login")
        print("2. Teacher Login")
        print("3. Student Login")
        print("4. Exit")

        role = input("Select (1-4): ").strip()

        if role == "1":
            uid = input("  Librarian ID: ").strip()
            pwd = input("  Password: ").strip()
            if uid == LIBRARIAN_ID and pwd == LIBRARIAN_PASSWORD:
                librarian_menu(system)
            else:
                print("  Wrong ID or password.")

        elif role == "2":
            uid = input("  Teacher ID: ").strip()
            pwd = input("  Password: ").strip()
            user = system.login_user("teacher", uid, pwd)
            if user:
                borrower_menu(system, user, "teacher")
            else:
                print("  Wrong ID or password.")

        elif role == "3":
            uid = input("  Student ID: ").strip()
            pwd = input("  Password: ").strip()
            user = system.login_user("student", uid, pwd)
            if user:
                borrower_menu(system, user, "student")
            else:
                print("  Wrong ID or password.")

        elif role == "4":
            print("Exiting... Goodbye!")
            break

        else:
            print("  Invalid choice.")


if __name__ == "__main__":
    main()
