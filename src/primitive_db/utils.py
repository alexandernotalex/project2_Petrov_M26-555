import json
import os

DATA_DIR = "data"

def load_metadata(filepath):
    """Загружает данные из JSON-файла. 
    Если файл не найден, возвращает пустой словарь {}."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_metadata(filepath, data):
    """Сохраняет переданные данные в JSON-файл."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_table_data(table_name):
    """
    Загружает данные строк конкретной таблицы из файла data/<table_name>.json
    Если файл не найден, возвращает пустой список [].
    """
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_table_data(table_name, data):
    """
    Сохраняет переданные строки данных в файл data/<table_name>.json.
    Автоматически создает папку data/, если её нет.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
