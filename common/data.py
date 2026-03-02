# -*- coding: utf-8 -*-
"""
Тестовые наборы данных для задачи раскроя.
"""

import json
import os

# ----------------------------
# Встроенные тестовые наборы
# ----------------------------

# Набор A: 10 одинаковых квадратов 5x5
set_A = [{'w': 5, 'h': 5}] * 10

# Набор Б: смесь размеров (10 деталей)
set_B = [
    {'w': 10, 'h': 5},
    {'w': 8, 'h': 6},
    {'w': 7, 'h': 7},
    {'w': 9, 'h': 4},
    {'w': 5, 'h': 5},
    {'w': 4, 'h': 6},
    {'w': 6, 'h': 4},
    {'w': 3, 'h': 8},
    {'w': 5, 'h': 3},
    {'w': 4, 'h': 4},
]

# Набор В: крупные детали (6 штук)
set_C = [
    {'w': 15, 'h': 8},
    {'w': 12, 'h': 10},
    {'w': 10, 'h': 10},
    {'w': 8, 'h': 15},
    {'w': 7, 'h': 12},
    {'w': 9, 'h': 9},
]

# Дополнительные наборы можно добавить по желанию

# Словарь всех наборов для удобного доступа по имени
ALL_SETS = {
    "set_A (10x5x5)": set_A,
    "set_B (смесь)": set_B,
    "set_C (крупные)": set_C,
}

# ----------------------------
# Загрузка из JSON-файла
# ----------------------------

def load_test_sets(filename="data/test_sets.json"):
    """
    Загружает тестовые наборы из JSON-файла.
    Возвращает список словарей с ключами: название, лист_ширина, лист_высота, детали.
    """
    if not os.path.exists(filename):
        # Если файл не найден, возвращаем встроенные наборы в том же формате
        print(f"Файл {filename} не найден. Используются встроенные наборы.")
        return [
            {
                "название": name,
                "лист_ширина": 20,
                "лист_высота": 20,
                "детали": items
            }
            for name, items in ALL_SETS.items()
        ]

    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data["наборы"]

# Функция для загрузки сгенерированных наборов (добавим, если нужно)
def load_generated_sets(filename="data/generated_sets.json"):
    """
    Загружает сгенерированные наборы из JSON-файла.
    Возвращает список словарей в формате, аналогичном load_test_sets.
    """
    if not os.path.exists(filename):
        print(f"Файл {filename} не найден. Возвращается пустой список.")
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("наборы", [])


def load_sa_generated_sets(filename="data/diverse_sets_strips1.json"):
    """
    Загружает сгенерированные наборы из JSON-файла.
    Возвращает список словарей в формате, аналогичном load_test_sets.
    """
    if not os.path.exists(filename):
        print(f"Файл {filename} не найден. Возвращается пустой список.")
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("наборы", [])