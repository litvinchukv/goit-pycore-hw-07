from collections import UserDict
import re
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not re.match(r'^\d{10}$', value):
            raise ValueError("Phone number must be 10 digits")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

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
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value.date()

                # Get the birthday for this year
                birthday_this_year = birthday.replace(year=today.year)

                # If the birthday has already passed this year, use the next year's birthday
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                # Check if the birthday is within the next 7 days
                if 0 <= (birthday_this_year - today).days <= 7:
                    # Check if the birthday falls on the weekend
                    if birthday_this_year.weekday() in [5, 6]:
                        # Calculate congratulation date as the next Monday
                        days_to_monday = 7 - birthday_this_year.weekday()
                        congratulation_date = birthday_this_year + timedelta(days=days_to_monday)
                    else:
                        congratulation_date = birthday_this_year

                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": congratulation_date.strftime("%Y.%m.%d")
                    })

        return upcoming_birthdays

if __name__ == "__main__":
    book = AddressBook()
    
    # Create and add John record
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")
    john_record.add_birthday("05.08.1985")
    book.add_record(john_record)

    # Create and add Jane record
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    jane_record.add_birthday("01.08.1990")
    book.add_record(jane_record)

    # Print all records
    for name, record in book.items():
        print(record)

    # Edit phone for John
    john = book.find("John")
    john.edit_phone("1234567890", "1112223333")
    print(john)

    # Find and print phone for John
    found_phone = john.find_phone("5555555555")
    print(f"{john.name}: {found_phone}")

    # Delete Jane's record
    book.delete("Jane")
    
    # Print all records after deletion
    for name, record in book.items():
        print(record)

    # Print upcoming birthdays
    upcoming_birthdays = book.get_upcoming_birthdays()
    for record in upcoming_birthdays:
        print(f"Upcoming birthday: {record}")