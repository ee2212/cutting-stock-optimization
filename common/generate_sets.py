"""
Генератор случайных тестовых наборов для задачи раскроя.
Наборы сохраняются в JSON-файл для последующего использования.
"""

import json
import random
import os


def generate_random_set(num_parts, min_size=2, max_size=15, W=20, H=20, seed=None):
    """
    Генерирует случайный набор прямоугольных деталей.
    Гарантирует, что каждая деталь помещается на лист (ширина и высота <= W, H).
    """
    if seed is not None:
        random.seed(seed)
    items = []
    for _ in range(num_parts):
        w = random.randint(min_size, min(max_size, W))
        h = random.randint(min_size, min(max_size, H))
        items.append({'w': w, 'h': h})
    return items


def generate_test_sets(config, filename="data/generated_sets.json"):
    """
    Генерирует несколько тестовых наборов согласно конфигурации и сохраняет в JSON.

    Параметры config (словарь):
        - num_sets: количество наборов
        - base_name: базовое имя для наборов (к нему будет добавляться индекс)
        - num_parts_list: список количества деталей для каждого набора (длина = num_sets)
        - min_size, max_size: диапазон размеров сторон
        - W, H: размеры листа (по умолчанию 20x20)
        - seeds: список seed'ов для воспроизводимости (опционально, длина = num_sets)
        - description: общее описание (опционально)
    """
    num_sets = config['num_sets']
    base_name = config.get('base_name', 'generated_set')
    num_parts_list = config['num_parts_list']
    min_size = config.get('min_size', 2)
    max_size = config.get('max_size', 15)
    W = config.get('W', 20)
    H = config.get('H', 20)
    seeds = config.get('seeds', [None] * num_sets)
    description = config.get('description', '')

    # Проверки
    assert len(num_parts_list) == num_sets, "num_parts_list должен иметь длину num_sets"
    assert len(seeds) == num_sets, "seeds должен иметь длину num_sets"

    sets = []
    for i in range(num_sets):
        name = f"{base_name}_{i+1}" if num_sets > 1 else base_name
        items = generate_random_set(
            num_parts=num_parts_list[i],
            min_size=min_size,
            max_size=max_size,
            W=W, H=H,
            seed=seeds[i]
        )
        sets.append({
            "название": name,
            "лист_ширина": W,
            "лист_высота": H,
            "детали": items,
            "параметры_генерации": {
                "seed": seeds[i],
                "num_parts": num_parts_list[i],
                "min_size": min_size,
                "max_size": max_size
            }
        })

    # Создаём директорию, если её нет
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Сохраняем в файл
    output = {
        "описание": description,
        "наборы": sets
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ Сгенерировано {num_sets} наборов, сохранено в {filename}")
    return sets


# ---------------------- Пример использования ----------------------
if __name__ == "__main__":
    # Пример конфигурации: 5 наборов с разным количеством деталей
    config_example = {
        'num_sets': 5,
        'base_name': 'random_set',
        'num_parts_list': [20, 30, 40, 50, 60],
        'min_size': 3,
        'max_size': 12,
        'W': 20,
        'H': 20,
        'seeds': [42, 123, 456, 789, 101112],  # фиксированные seed'ы для воспроизводимости
        'description': 'Наборы для тестирования алгоритмов раскроя (сгенерированы 2026)'
    }
    generate_test_sets(config_example, filename="data/generated_sets.json")