import shlex

from prettytable import PrettyTable
from prompt import string

from primitive_db.constants import DATABASE_FILE
from primitive_db.core import create_table, delete, drop_table, insert, select, update
from primitive_db.decorators import create_cacher
from primitive_db.parser import parse_clause
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Prints the help message for the current mode."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("  create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print(
        "  list_tables                                  - показать список всех таблиц"
    )
    print("  drop_table <имя_таблицы>                     - удалить таблицу")
    print("  insert <имя_таблицы> <значение1> <значение2>..- добавить запись")
    print("  select <имя_таблицы> [условие]               - выбрать и показать записи")
    print("  update <имя_таблицы> set <кусок> where <кусок>- обновить записи")
    print("  delete <имя_таблицы> where <условие>         - удалить записи")
    print("\nОбщие команды:")
    print("  exit - выход из программы")
    print("  help - справочная информация\n")


def parse_columns(args_list):
    columns = {}
    for arg in args_list:
        if ":" not in arg:
            print(
                f"Предупреждение: Неверный формат аргумента '{arg}'. "
                "Используйте имя:тип."
            )
            continue
        col_name, col_type = arg.split(":", 1)
        columns[col_name] = col_type
    return columns


def display_with_prettytable(columns_schema, rows_data):
    """Красиво выводит строки данных в консоль в виде таблицы."""
    if not rows_data:
        print("Таблица пуста или нет записей, соответствующих условию.")
        return

    table = PrettyTable()
    table.field_names = list(columns_schema.keys())

    for row in rows_data:
        row_values = [row.get(col) for col in table.field_names]
        table.add_row(row_values)

    print(table)


def run():
    print("--- Примитивная СУБД запущена ---")
    print("Введите 'help' для просмотра всех доступных CRUD-команд.\n")

    db_cache = create_cacher()

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
                print("Завершение работы программы!")
                break

            case "help":
                print_help()

            case "list_tables":
                if not metadata:
                    print("В базе данных пока нет ни одной таблицы.")
                else:
                    print("\nСписок существующих таблиц:")
                    for table in metadata.keys():
                        print(f"  - {table}")
                    print()

            case "create_table":
                db_cache = create_cacher()
                if len(args) < 2:
                    print(
                        "Ошибка: Недостаточно аргументов. "
                        "Пример: create_table users name:str age:int"
                    )
                    continue
                table_name = args[0]
                columns_dict = parse_columns(args[1:])
                if not columns_dict:
                    print("Ошибка: Не удалось распознать ни одного столбца.")
                    continue
                metadata = create_table(metadata, table_name, columns_dict)
                save_metadata(DATABASE_FILE, metadata)

            case "drop_table":
                db_cache = create_cacher()
                if len(args) < 1:
                    print("Ошибка: Укажите имя таблицы. Пример: drop_table users")
                    continue
                table_name = args[0]
                metadata = drop_table(metadata, table_name)
                save_metadata(DATABASE_FILE, metadata)

            case "insert":
                db_cache = create_cacher()
                if len(args) < 2:
                    print("Ошибка: Пример использования: insert users Ivan 25 True")
                    continue
                table_name = args[0]
                values = args[1:]

                updated_data = insert(metadata, table_name, values)
                if updated_data is not None:
                    save_table_data(table_name, updated_data)
                    print(f"Успех: Запись успешно добавлена в таблицу '{table_name}'.")

            case "select":
                if len(args) < 1:
                    print("Ошибка: Укажите имя таблицы. Пример: select users")
                    continue
                table_name = args[0]
                if table_name not in metadata:
                    print(f"Ошибка: Таблицы '{table_name}' не существует.")
                    continue

                where_str = " ".join(args[1:])
                try:
                    where_clause = parse_clause(where_str) if where_str else None
                except ValueError as e:
                    print(f"Ошибка парсинга условий WHERE: {e}")
                    continue

                cache_key = f"{table_name}:{where_str if where_str else 'all'}"

                def get_data_func():
                    return select(load_table_data(table_name), where_clause)

                filtered_rows = db_cache(cache_key, get_data_func)

                display_with_prettytable(metadata[table_name]["columns"], filtered_rows)

            case "update":
                if len(args) < 4 or args[1].lower() != "set":
                    print(
                        "Ошибка: Пример использования: "
                        "update users set is_active = False where age = 25"
                    )
                    continue
                table_name = args[0]
                if table_name not in metadata:
                    print(f"Ошибка: Таблицы '{table_name}' не существует.")
                    continue

                full_str = " ".join(args[1:])
                if "where" not in full_str.lower():
                    print("Ошибка: Команда UPDATE требует обязательного условия WHERE.")
                    continue

                parts = full_str.lower().split("where", 1)
                set_str = parts[0].replace("set", "").strip()
                where_str = parts[1].strip()

                try:
                    set_clause = parse_clause(set_str)
                    where_clause = parse_clause(where_str)
                except ValueError as e:
                    print(f"Ошибка парсинга команды UPDATE: {e}")
                    continue

                table_data = load_table_data(table_name)
                updated_data = update(table_data, set_clause, where_clause)
                save_table_data(table_name, updated_data)

                db_cache = create_cacher()

            case "delete":
                if len(args) < 3 or args[1].lower() != "where":
                    print("Ошибка: Пример использования: delete users where age = 25")
                    continue
                table_name = args[0]
                if table_name not in metadata:
                    print(f"Ошибка: Таблицы '{table_name}' не существует.")
                    continue

                where_str = " ".join(args[2:])
                try:
                    where_clause = parse_clause(where_str)
                except ValueError as e:
                    print(f"Ошибка парсинга условий DELETE: {e}")
                    continue

                table_data = load_table_data(table_name)
                updated_data = delete(table_data, where_clause)
                save_table_data(table_name, updated_data)

                db_cache = create_cacher()

            case _:
                print(f"Неизвестная команда '{command}'. Введите 'help' для справки.")
