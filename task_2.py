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

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Invalid number of arguments. Please check the command format."
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"
    return wrapper

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, book: AddressBook):
    name, = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    if record.birthday:
        return f"{name}'s birthday: {record.birthday}"
    else:
        return "Birthday not set."

@input_error
def birthdays(args, book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays."
    return "\n".join(f"{record['name']}: {record['congratulation_date']}" for record in upcoming_birthdays)

def parse_input(user_input):
    return user_input.strip().split()

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            if len(args) != 3:
                print("Invalid command format. Use: change [name] [old phone] [new phone].")
            else:
                name, old_phone, new_phone = args
                record = book.find(name)
                if record is None:
                    print("Contact not found.")
                else:
                    record.edit_phone(old_phone, new_phone)
                    print("Phone number updated.")

        elif command == "phone":
            if len(args) != 1:
                print("Invalid command format. Use: phone [name].")
            else:
                name, = args
                record = book.find(name)
                if record is None:
                    print("Contact not found.")
                else:
                    phones = "; ".join(p.value for p in record.phones)
                    print(f"{name}'s phones: {phones}")

        elif command == "all":
            if not book:
                print("No contacts in address book.")
            else:
                for name, record in book.items():
                    print(record)

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