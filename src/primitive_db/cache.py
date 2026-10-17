def create_cacher():
    """
    Создает и возвращает функцию кэширования.
    Словарь `cache_store` сохраняется в замыкании возвращаемой функции.
    """
    cache_store = {}

    def cache_result(key, value_func):
        """
        Проверяет наличие ключа в кэше. Если ключ есть — возвращает значение.
        Если нет — вычисляет его с помощью value_func, кэширует и возвращает.
        """
        if key in cache_store:
            print(f"[КЭШ] Результат для запроса '{key}' взят из кэша.")
            return cache_store[key]

        print(f"[КЭШ] Запрос '{key}' не найден в кэше. Вычисляем значения...")
        # Вызываем функцию получения данных
        result = value_func()

        # Сохраняем результат в кэш
        cache_store[key] = result
        return result

    return cache_result
