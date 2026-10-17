from primitive_db.decorators import confirm_action, handle_db_errors, log_time
from primitive_db.utils import load_table_data

ALLOWED_TYPES = {"int", "str", "bool"}


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создает новую таблицу в метаданных."""
    if table_name in metadata:
        raise KeyError(table_name)

    # Валидация типов данных
    for col_name, col_type in columns.items():
        if col_type not in ALLOWED_TYPES:
            raise ValueError(
                f"Недопустимый тип данных '{col_type}' для столбца '{col_name}'. "
                "Разрешенные типы: int, str, bool."
            )

    # Формируем структуру новой таблицы
    new_table_columns = {}

    # Приводим к нижнему регистру для проверки на наличие id/ID
    user_column_names = {col.lower() for col in columns.keys()}

    if "id" not in user_column_names:
        new_table_columns["id"] = "int"

    new_table_columns.update(columns)

    metadata[table_name] = {"columns": new_table_columns, "rows": []}

    print(f"Успех: Таблица '{table_name}' успешно создана.")
    return metadata


@confirm_action("удаление таблицы")
@handle_db_errors
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        raise KeyError(table_name)

    del metadata[table_name]
    print(f"Успех: Таблица '{table_name}' успешно удалена.")
    return metadata


@log_time
@handle_db_errors
def insert(metadata, table_name, values):
    """Добавляет новую запись в таблицу."""
    if table_name not in metadata:
        raise KeyError(table_name)

    columns_schema = metadata[table_name]["columns"]
    user_columns = [col for col in columns_schema.keys() if col.lower() != "id"]

    if len(values) != len(user_columns):
        raise ValueError(
            f"Ожидалось {len(user_columns)} значений, получено {len(values)}."
        )

    table_data = load_table_data(table_name)

    new_row = {}
    type_mapping = {"int": int, "str": str, "bool": bool}

    for col_name, val in zip(user_columns, values):
        expected_type_str = columns_schema[col_name]

        if expected_type_str == "bool":
            if isinstance(val, str):
                if val.lower() in ("true", "1"):
                    actual_val = True
                elif val.lower() in ("false", "0"):
                    actual_val = False
                else:
                    raise ValueError(
                        f"Не удалось привести '{val}' к типу bool "
                        f"для столбца '{col_name}'."
                    )
            else:
                actual_val = bool(val)
        else:
            actual_val = type_mapping[expected_type_str](val)

        new_row[col_name] = actual_val

    # Генерация ID
    existing_ids = [row["id"] for row in table_data if "id" in row]
    new_id = max(existing_ids) + 1 if existing_ids else 1

    final_row = {"id": new_id}
    final_row.update(new_row)

    table_data.append(final_row)
    return table_data


@log_time
@handle_db_errors
def select(table_data, where_clause=None):
    """Выбирает и фильтрует данные из таблицы."""
    if not where_clause:
        return table_data

    filtered_data = []
    for row in table_data:
        match = True
        for key, value in where_clause.items():
            if row.get(key) != value:
                match = False
                break
        if match:
            filtered_data.append(row)

    return filtered_data


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет данные в таблице по условию."""
    updated_count = 0
    for row in table_data:
        match = True
        for key, value in where_clause.items():
            if row.get(key) != value:
                match = False
                break

        if match:
            for set_key, set_value in set_clause.items():
                if set_key in row and set_key != "id":
                    row[set_key] = set_value
            updated_count += 1

    print(f"Успешно обновлено записей: {updated_count}.")
    return table_data


@confirm_action("удаление записи")
@handle_db_errors
def delete(table_data, where_clause):
    """Удаляет записи из таблицы по условию."""
    initial_count = len(table_data)

    new_table_data = []
    for row in table_data:
        match = True
        for key, value in where_clause.items():
            if row.get(key) != value:
                match = False
                break
        if not match:
            new_table_data.append(row)

    deleted_count = initial_count - len(new_table_data)
    print(f"Успешно удалено записей: {deleted_count}.")
    return new_table_data
