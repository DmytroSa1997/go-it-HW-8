from datetime import datetime, timedelta
import re
import pickle

# Декоратор для обробки помилок
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Invalid number of arguments. Please provide the correct number of arguments."
        except KeyError:
            return "Contact not found."
    return inner

# Функції для збереження та завантаження даних
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

# Базовий клас Field
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Клас для імені
class Name(Field):
    pass

# Клас для телефону з валідацією
class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Phone number must contain 10 digits.")
        super().__init__(value)

    @staticmethod
    def validate_phone(phone):
        return bool(re.match(r'^\d{10}$', phone))

# Клас для дня народження з валідацією (зберігає рядок)
class Birthday(Field):
    def __init__(self, value):
        if not self.validate_date(value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)  # Зберігаємо значення як рядок

    @staticmethod
    def validate_date(date_str):
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
            return True
        except ValueError:
            return False

# Клас для запису контакту
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        if not any(p.value == old_phone for p in self.phones):
            raise ValueError("Phone number not found.")
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(str(p) for p in self.phones)
        birthday = str(self.birthday) if self.birthday else "Not set"
        return f"Contact name: {self.name}, phones: {phones}, birthday: {birthday}"