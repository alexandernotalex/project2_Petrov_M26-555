from prompt import string
from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata
import shlex

DATABASE_FILE = "metadata.json"

def welcome():
    print("Первая попытка запустить проект!")
    print("\n***")
    
    while True:
        print("<command> exit - выйти из программы")
        print("<command> help - справочная информация")
        
        command = string("Введите команду: ")
        
        if command == "exit":
            break
        elif command == "help":
            continue 
        else:
            print("Неизвестная команда. Попробуйте еще раз.")

def print_help():
    """Prints the help message for the current mode."""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def parse_columns(args_list):
    """Вспомогательная функция для сборки словаря столбцов из аргументов командной строки.

    Ожидает аргументы в формате имя:тип (например, name:str age:int)
    """
    columns = {}
    for arg in args_list:
        if ":" not in arg:
            print(
                f"Предупреждение: Неверный формат аргумента '{arg}'. Используйте имя:тип."
            )
            continue
        col_name, col_type = arg.split(":", 1)
        columns[col_name] = col_type
    return columns


def run():
    """Главная функция с основным циклом программы."""
    print("--- Примитивная СУБД запущена ---")
    print("Доступные команды: create_table, drop_table, help, exit\n")

    while True:
        metadata = load_metadata(DATABASE_FILE)

        user_input = string("> ").strip()

        if not user_input:
            continue

        try:
            tokens = shlex.split(user_input)
        except ValueError as e:
            print(f"Ошибка синтаксиса ввода: {e}")
            continue

        command = tokens[0].lower()
        args = tokens[1:]

        match command:
            case "exit":
                print("Завершение работы программы")
                break

            case "help":
                print("\nСправка по командам:")
                print(
                    "  create_table [имя_таблицы] [столбец1:тип] [столбец2:тип] ..."
                )
                print("  drop_table [имя_таблицы]")
                print("  exit - Выйти из программы\n")

            case "create_table":
                if len(args) < 2:
                    print(
                        "Ошибка: Недостаточно аргументов." \
                        "Пример: create_table users name:str age:int"
                    )
                    continue

                table_name = args[0]
                columns_dict = parse_columns(args[1:])

                if not columns_dict:
                    print(
                        "Ошибка: Не удалось распознать ни одного столбца для создания таблицы."
                    )
                    continue

                metadata = create_table(metadata, table_name, columns_dict)
                save_metadata(DATABASE_FILE, metadata)

            case "drop_table":
                if len(args) < 1:
                    print("Ошибка: Укажите имя таблицы. Пример: drop_table users")
                    continue

                table_name = args[0]

                metadata = drop_table(metadata, table_name)
                save_metadata(DATABASE_FILE, metadata)

            case _:
                print(
                    f"Неизвестная команда '{command}'. Введите 'help' для справки."
                )

