from ab_classes import (
    AddressBook,
    Name,
    Phone,
    Record,
    BirthdayError,
    DuplicatePhoneError,
)

address_book = AddressBook()


def help_command(*args):
    return """Це бот персонального телефонного довідника.
Команди які можна використовувати:
    "add", "+" Додає контакт та номер телефону та день народження якщо потрібно. Формат: add Name 1234567890 11-11-1999 
    "change", "зміни" Змінює телефон контакту. Формат: change Name 1234567890 0987654321
    "bye", "exit", "end", "вихід" Завершує роботу програми та зберігає довідник у файл. Формат: exit
    "show all", "покажи все" Виводить на єкран список всіх контактів їх телефонів та днів народження(якщо вказано). Формат: show all
    "del", "delete", "видали" Видаляє контакт з довідниа і всі його данні повністю(БЕЗ МОЖЛИВОСТІ ВІДНОВЛЕННЯ). Формат: del Name
    "get", "дай" Виводить данні контакту за запитом по імені. Формат: get Name
    "search", "find", "знайди" Шукає контакти в довіднику за ключовим запитом(мінімум 3 символи). Формат: find Nam / або: find 456"""


def input_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except KeyError:
            return "Enter user name"
        except ValueError as v:
            return v if v else "Give me name and phone please"
        except IndexError:
            return "Invalid command"
        except TypeError:
            return "Please provide the necessary parameters"
        except BirthdayError:
            return "Invalid birthday format. Please use the format 'day-month-year', e.g., '26-11-1978'."

    return wrapper


@input_error
def add_command(*args):
    name = Name(args[0])
    phone = Phone(args[1].strip().replace(" ", ""))

    if len(args) >= 3:
        birth = args[2]
    else:
        birth = None

    rec: Record = address_book.get(str(name))
    if rec:
        try:
            rec.add_phone(phone)
            return f"Phone {(str(phone))} added to contact {rec.name}"
        except DuplicatePhoneError as e:
            return str(e)

    rec = Record(name, phone, birth)
    return address_book.add_record(rec)


@input_error
def change_command(*args):
    name = Name(args[0])
    old_phone = Phone(args[1])
    new_phone = Phone(args[2])
    rec: Record = address_book.get(str(name))
    if rec:
        return rec.change_phone(old_phone, new_phone)
    return f"No contact {name} in address book"


def exit_command():
    address_book.save_address_book()
    return "Bye"


@input_error
def unknown_command(*args):
    return f"Unknown command: {args[0]}"


@input_error
def get_phone_command(*args):
    if len(args) != 1:
        return "Invalid arguments. Usage: get <contact_name>"

    contact_name = args[0]
    rec: Record = address_book.get(contact_name)
    if rec:
        if rec.birthday:
            return f"Phones for {contact_name}: {', '.join(str(phone) for phone in rec.phones)}: (Days to birthday: {rec.birthday.days_to_birthday()})"
        else:
            return f"Phones for {contact_name}: {', '.join(str(phone) for phone in rec.phones)}"
    else:
        return f"Contact {contact_name} not found in the address book"


@input_error
def find_command(*args):
    result = []
    search = args[0]
    if len(search) < 3:
        return "Invalid arguments. Usage: find <minimum 3 symbols>"
    for i in address_book:
        if search in str(i):
            result.append(str(i))
    if result:
        return "\n".join(result)
    else:
        return f"No matches found for {search}"


@input_error
def show_all_command(*args):
    if not address_book:
        return "Address book is empty"

    if not args:
        start_page = 1
        end_page = float("inf")
    elif len(args) == 1:
        start_page = int(args[0])
        end_page = start_page
    elif len(args) == 2:
        start_page = int(args[0])
        end_page = int(args[1])
    else:
        return "Invalid arguments. Usage: show all [start_page [end_page]]"

    all_contacts = ""
    for page, records in enumerate(address_book.iterator(), start=1):
        if start_page <= page <= end_page:
            all_contacts += f"Page {page}:\n"
            for record in records:
                contact_str = str(record)
                if record.birthday:
                    contact_str += f" (Days to birthday: {record.birthday.days_to_birthday()})"  # Birthday: {record.birthday},
                all_contacts += contact_str + "\n"
            all_contacts += "\n"

    return all_contacts


@input_error
def delete_command(*args):
    contact_name = str(args[0])
    if contact_name in address_book:
        confirmation = input(f"Are you sure delete {contact_name}: Yes/No :").lower()
        if confirmation == "yes":
            address_book.del_record(contact_name)
            return f"Contact {contact_name} deleted"

    else:
        return f"Contact {contact_name} not found in the address book"


COMMANDS = {
    add_command: ("add", "+"),
    change_command: ("change", "зміни"),
    exit_command: ("bye", "exit", "end", "вихід"),
    show_all_command: ("show all", "покажи все"),
    delete_command: ("del", "delete", "видали"),
    get_phone_command: ("get", "дай"),
    find_command: ("search", "find", "знайди"),
    help_command: ("help"),
}


def parser(text):
    for cmd, kwds in COMMANDS.items():
        for kwd in kwds:
            if text.lower().startswith(kwd):
                data = text[len(kwd) :].strip().split()
                return cmd, data
    return unknown_command, [text]


def main():
    address_book.load_address_book()
    print("'help' for more information")
    while True:
        user_input = input("Wait...>")

        cmd, data = parser(user_input)

        result = cmd(*data)
        print(result)

        if cmd == exit_command:
            break


if __name__ == "__main__":
    main()
