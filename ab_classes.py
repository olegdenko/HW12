from collections import UserDict
from datetime import datetime, date
import re
import pickle
import itertools


class BirthdayError(Exception):
    ...


class DuplicatePhoneError(Exception):
    ...


class NotValidNumber(Exception):
    ...


class Field:
    def __init__(self, value) -> None:
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value


class Name(Field):
    def __str__(self):
        return self.value


class Phone(Field):
    def __init__(self, value=None):
        self._value = None
        if value is not None:
            self.value = value

    def _validate_phone(self, value):
        if not re.match(r"^\d{7,15}$", value):
            raise ValueError("Invalid phone number format")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._validate_phone(new_value)
        self._value = new_value

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return self.value


class Birthday(Field):
    def __init__(self, value):
        self._validate_birthday(value)
        self._value = datetime.strptime(value, "%d-%m-%Y").date()

    def _validate_birthday(self, value):
        try:
            datetime.strptime(value, "%d-%m-%Y")
        except ValueError:
            raise BirthdayError("Invalid birthday format. Use DD-MM-YYYY format.")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._validate_birthday(new_value)
        self._value = datetime.strptime(new_value, "%d-%m-%Y").date()

    def days_to_birthday(self):
        if not self._value:
            return None

        current_date = datetime.now().date()
        given_date = date(current_date.year, self._value.month, self._value.day)
        if given_date < current_date:
            given_date = date(current_date.year + 1, self._value.month, self._value.day)

        delta = given_date - current_date
        return delta.days

    def __str__(self) -> str:
        return self._value.strftime("%d-%m-%Y") if self._value else ""


class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = name
        self.phones = []
        if phone:
            self.add_phone(phone)
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone: Phone):
        if phone not in self.phones:
            self.phones.append(phone)
            return f"Phone {phone} added to contact {self.name}"

        return f"Phone {phone} already present in contact {self.name}"

    def change_phone(self, old_phone, new_phone):
        for idx, phone in enumerate(self.phones):
            if old_phone.value == phone.value:
                self.phones[idx] = new_phone
                return f"Old phone {old_phone} changed to {new_phone}"

        return f"{old_phone} not present in phonebook"

    def change_birthday(self, new_birthday):
        self.birthday = Birthday(new_birthday)

    def __str__(self):
        phone_str = ", ".join(str(phone) for phone in self.phones)
        contact_str = f"{self.name}: [{phone_str}]"
        if self.birthday:
            contact_str += f" (Birthday: {self.birthday})"
        return contact_str

    def birthday_info(self):
        if self.birthday:
            return (
                f"{self.birthday}, Days to birthday: {self.birthday.days_to_birthday()}"
            )
        return ""


class AddressBook(UserDict):
    def __init__(self, *args, page_size=5, **kwargs):
        self.page_size = page_size
        super().__init__(*args, **kwargs)

    def add_record(self, record: Record):
        self.data[str(record.name)] = record
        return f"Contact {record.name} added"

    def del_record(self, name):
        if name in self.data:
            del self.data[name]
            return f"Contact {name} deleted"
        return f"Contact {name} does not exist in the phonebook"

    def load_address_book(self):
        path = input(
            'Input path for address book (Default path is "addressbook.pkl"): '
        )
        if not path:
            path = "addressbook.pkl"
        try:
            with open(path, "r+b") as file:
                try:
                    self.data = pickle.load(file)
                except EOFError:
                    print(f"File '{path}' is empty. Creating an empty address book.")
                    self.data = AddressBook()
        except FileNotFoundError:
            print(f"File '{path}' not found. Creating an empty address book.")
            self.data = AddressBook()
        return self

    def save_address_book(self, path=None):
        if not path:
            path = input('Input path for saving (Default path is "addressbook.pkl"): ')
        if not path:
            path = "addressbook.pkl"
        with open(path, "wb") as file:
            pickle.dump(self.data, file)

    def del_record(self, name):
        if name in self.data:
            del self.data[name]
        return f"Contact {name} does not exist in the phonebook"

    def values(self):
        return iter(self.data.values())

    def iterator(self):
        total_records = len(self.data)
        current_page = 0
        while current_page < total_records:
            yield itertools.islice(
                self.values(), current_page, current_page + self.page_size
            )
            current_page += self.page_size

    def __iter__(self):
        return iter(self.data.values())

    def __str__(self):
        return "\n".join(str(record) for record in self.data)
