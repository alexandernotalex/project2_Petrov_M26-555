ALLOWED_TYPES = {'int', 'str', 'bool'}

def create_table(metadata, table_name, columns):
    """
    Создает новую таблицу в метаданных.
    
    :param metadata: текущий словарь метаданных
    :param table_name: имя создаваемой таблицы (str)
    :param columns: список или словарь столбцов с их типами
    :return: обновленный словарь metadata или исходный в случае ошибки
    """
    if table_name in metadata:
        print(f"Ошибка: таблица '{table_name}' уже существует.")
        return metadata

    for col_name, col_type in columns.items():
        if col_type not in ALLOWED_TYPES:
            print(
              f"Ошибка: недопустимый тип данных '{col_type}' для столбца '{col_name}'.")
            print("Разрешенные типы: int, str, bool.")
            return metadata

    new_table_columns = {}
    
    user_column_names = {col.lower() for col in columns.keys()}
    if "id" not in user_column_names:
        new_table_columns["id"] = "int"
        
    new_table_columns.update(columns)
    metadata[table_name] = {
        "columns": new_table_columns,
        "rows": []
    }

    print(f"Таблица '{table_name}' успешно создана.")
    return metadata

def drop_table(metadata, table_name):
    """
    Удаляет таблицу из метаданных.
    
    :param metadata: текущий словарь метаданных
    :param table_name: имя удаляемой таблицы (str)
    :return: обновленный словарь metadata
    """
    if table_name not in metadata:
        print(f"Ошибка: Таблицы '{table_name}' не существует.")
        return metadata

    del metadata[table_name]

    print(f"Таблица '{table_name}' успешно удалена.")
    return metadata

def insert(metadata, table_name, values):
    """
    Добавляет новую запись в таблицу.
    
    :param metadata: текущий словарь метаданных СУБД
    :param table_name: имя таблицы (str)
    :param values: список значений для вставки [val1, val2, ...] без учета ID
    :return: обновленный список строк (table_data) таблицы, None в случае ошибки
    """
    # 1. Проверяем, существует ли таблица
    if table_name not in metadata:
        print(f"Ошибка: Таблицы '{table_name}' не существует.")
        return None

    # Получаем схему столбцов. Например: {"id": "int", "name": "str", "age": "int"}
    columns_schema = metadata[table_name]["columns"]
    
    # Столбцы, которые должен заполнить пользователь (все, кроме id)
    user_columns = [col for col in columns_schema.keys() if col.lower() != "id"]

    # 2. Проверяем количество переданных значений
    if len(values) != len(user_columns):
        print(f"Ошибка: Ожидалось {len(user_columns)} значений, получено {len(values)}.")
        return None

    # Загружаем текущие данные таблицы (строки). 
    # Так как мы вызываем эту функцию из engine, передадим управление загрузкой туда,
    # а здесь инициализируем пустой список, если функция вызовется изолированно.
    # Но для интеграции правильнее загрузить данные прямо перед вставкой.
    from primitive_db.utils import load_table_data
    table_data = load_table_data(table_name)

    # 3. Валидируем типы данных для каждого значения
    new_row = {}
    type_mapping = {"int": int, "str": str, "bool": bool}

    for col_name, val in zip(user_columns, values):
        expected_type_str = columns_schema[col_name]  # Например, "int"
        
        # Проверяем соответствие типа (пытаемся привести типы, если они пришли строками из консоли)
        try:
            if expected_type_str == "bool":
                # Надежная конвертация строки в bool
                if isinstance(val, str):
                    if val.lower() in ("true", "1"):
                        actual_val = True
                    elif val.lower() in ("false", "0"):
                        actual_val = False
                    else:
                        raise ValueError
                else:
                    actual_val = bool(val)
            else:
                actual_val = type_mapping[expected_type_str](val)
        except (ValueError, TypeError):
            print(f"Ошибка: Неверный тип данных для столбца '{col_name}'. Ожидался {expected_type_str}.")
            return None
        
        new_row[col_name] = actual_val

    # 4. Генерирует новый ID (max(IDs) + 1)
    existing_ids = [row["id"] for row in table_data if "id" in row]
    new_id = max(existing_ids) + 1 if existing_ids else 1

    # Собираем итоговую строку, ставя ID на первое место
    final_row = {"id": new_id}
    final_row.update(new_row)

    # 5. Добавляем запись и возвращаем измененные данные
    table_data.append(final_row)
    return table_data


def select(table_data, where_clause=None):
    """
    Выбирает и фильтрует данные из таблицы.
    """
    # Если where_clause не задан, возвращает все данные
    if not where_clause:
        return table_data

    filtered_data = []
    for row in table_data:
        # Проверяем, совпадает ли строка со всеми условиями фильтра
        match = True
        for key, value in where_clause.items():
            if row.get(key) != value:
                match = False
                break
        if match:
            filtered_data.append(row)
            
    return filtered_data


def update(table_data, set_clause, where_clause):
    """
    Обновляет данные в таблице по условию.
    """
    updated_count = 0
    for row in table_data:
        # Ищем записи, подходящие под where_clause
        match = True
        for key, value in where_clause.items():
            if row.get(key) != value:
                match = False
                break
        
        # Если нашли запись, обновляем её поля согласно set_clause
        if match:
            for set_key, set_value in set_clause.items():
                if set_key in row and set_key != "id":  # Запрещаем менять ID вручную
                    row[set_key] = set_value
            updated_count += 1

    print(f"Успешно обновлено записей: {updated_count}.")
    return table_data


def delete(table_data, where_clause):
    """
    Удаляет записи из таблицы по условию.
    """
    # Сохраняем только те записи, которые НЕ подходят под условия удаления
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
