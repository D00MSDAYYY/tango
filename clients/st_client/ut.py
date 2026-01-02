cache = {}

def get_or_create(key, default={}):  # Убрал self, так как это не метод класса
    if key not in cache:
        cache[key] = default  # ПРОБЛЕМА: все ключи получают одну и ту же ссылку!
    return cache[key]

# Тест, демонстрирующий проблему
obj1 = get_or_create("user1")  # Использует дефолтный {}
obj1["name"] = "Alice"

obj2 = get_or_create("user2")  # Снова использует тот же дефолтный {}
print(obj2)  # {'name': 'Alice'}  # Данные смешались!

print("cache:", cache)
# Вывод: {'user1': {'name': 'Alice'}, 'user2': {'name': 'Alice'}}