import pickle
import os
from collections import UserDict
from datetime import datetime, timedelta

# === Серіалізація ===
DATA_FILE = "addressbook.pkl"

def save_data(book, filename=DATA_FILE):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename=DATA_FILE):
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            return pickle.load(f)
    return AddressBook()


# === Класи ===
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value: str):
        try:
            datetime.strptime(value, "%d.%m.%Y")  # перевірка
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)  # зберігаємо як рядок

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        phone = self.find_phone(phone_number)
        if phone:
            self.phones.remove(phone)
        else:
            raise ValueError("Phone number not found.")

    def edit_phone(self, old_number, new_number):
        old_phone = self.find_phone(old_number)
        if not old_phone:
            raise ValueError("Old phone number not found.")
        self.remove_phone(old_number)
        self.add_phone(new_number)

    def find_phone(self, number):
        for phone in self.phones:
            if phone.value == number:
                return phone
        return None

    def add_birthday(self, birthday_str):
        self.birthday = Birthday(birthday_str)

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday = self.birthday.value if self.birthday else "N/A"
        return f"Name: {self.name.value}, Phones: {phones}, Birthday: {birthday}"

class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name)

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        result = []
        for record in self.data.values():
            if record.birthday:
                bday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                bday_this_year = bday_date.replace(year=today.year)
                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(year=today.year + 1)
                delta_days = (bday_this_year - today).days
                if 0 <= delta_days <= 7:
                    congrat_date = bday_this_year
                    if congrat_date.weekday() == 5:
                        congrat_date += timedelta(days=2)
                    elif congrat_date.weekday() == 6:
                        congrat_date += timedelta(days=1)
                    result.append({
                        "name": record.name.value,
                        "birthday": congrat_date.strftime("%d.%m.%Y")
                    })
        return result

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())


# === Декоратор ===
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError, KeyError) as e:
            return str(e)
    return wrapper


# === Команди ===
@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    else:
        message = "Contact updated."
    record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        raise ValueError("Contact not found.")
    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        raise ValueError("Contact not found.")
    return "; ".join(phone.value for phone in record.phones)

@input_error
def add_birthday(args, book):
    name, bday = args
    record = book.find(name)
    if not record:
        raise ValueError("Contact not found.")
    record.add_birthday(bday)
    return "Birthday added."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record or not record.birthday:
        raise ValueError("Birthday not found.")
    return record.birthday.value

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays this week."
    return "\n".join(f"{item['name']}: {item['birthday']}" for item in upcoming)


# === Парсер команди ===
def parse_input(user_input):
    parts = user_input.strip().split()
    return parts[0].lower(), parts[1:]


# === Головна функція ===
def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            continue

        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(book)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
