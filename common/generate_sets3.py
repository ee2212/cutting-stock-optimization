# -*- coding: utf-8 -*-
"""
Генератор тестовых наборов для материалов с фиксированным направлением.
Детали нельзя поворачивать – учитывается текстура, ворс, рисунок и т.п.
"""

import json
import random
import os

# ----------------------------------------------------------------------
# Вспомогательные функции (аналогичны оригинальным, но с учётом ориентации)
# ----------------------------------------------------------------------

def generate_directional_items(num_parts, size_ranges, W, H, seed=None):
    """
    Генерирует детали с фиксированной ориентацией.
    size_ranges – список кортежей (min_w, max_w, min_h, max_h) для разных типов деталей.
    Каждая деталь получает rotatable=False.
    """
    if seed is not None:
        random.seed(seed)
    items = []
    for _ in range(num_parts):
        # Выбираем случайный диапазон из списка
        min_w, max_w, min_h, max_h = random.choice(size_ranges)
        w = random.randint(min_w, min(max_w, W))
        h = random.randint(min_h, min(max_h, H))
        items.append({
            'w': w,
            'h': h,
            'rotatable': False   # ключевое поле – запрет поворота
        })
    return items

def generate_mixed_directional(num_parts, large_ratio, large_ranges, small_ranges, W, H, seed=None):
    """
    Смесь крупных и мелких деталей с фиксированной ориентацией.
    large_ranges и small_ranges – списки диапазонов (min_w,max_w,min_h,max_h).
    """
    if seed is not None:
        random.seed(seed)
    items = []
    n_large = int(num_parts * large_ratio)
    n_small = num_parts - n_large

    for _ in range(n_large):
        min_w, max_w, min_h, max_h = random.choice(large_ranges)
        w = random.randint(min_w, min(max_w, W))
        h = random.randint(min_h, min(max_h, H))
        items.append({'w': w, 'h': h, 'rotatable': False})

    for _ in range(n_small):
        min_w, max_w, min_h, max_h = random.choice(small_ranges)
        w = random.randint(min_w, min(max_w, W))
        h = random.randint(min_h, min(max_h, H))
        items.append({'w': w, 'h': h, 'rotatable': False})

    random.shuffle(items)
    return items

# ----------------------------------------------------------------------
# Отраслевые генераторы для направленных материалов
# ----------------------------------------------------------------------

def generate_fabric_set(seed=None):
    """
    Ткань (рулонная): ширина рулона 1500 мм, длина нареза 1000–5000 мм.
    Детали – элементы кроя, направление основы обязательно.
    """
    W, H = 1500, 5000  # ширина рулона, максимальная длина отреза
    num_parts = random.randint(20, 40)
    # Типовые размеры деталей одежды/мебели (длина по основе, ширина по утку)
    ranges = [
        (300, 800, 400, 1200),   # полочка, спинка
        (200, 500, 300, 800),    # рукава, воротники
        (50, 200, 50, 300),      # мелкие детали
        (800, 1400, 100, 400),   # длинные полосы (по основе)
    ]
    items = generate_directional_items(num_parts, ranges, W, H, seed)
    return items, W, H

def generate_laminate_set(seed=None):
    """
    Ламинированные плиты (ДСП/МДФ) с рисунком: лист 2800x2070 мм.
    Направление рисунка строго задано (обычно вдоль длинной стороны).
    """
    W, H = 2800, 2070
    num_parts = random.randint(25, 45)
    # Мебельные детали с учётом направления текстуры
    ranges = [
        (500, 1200, 300, 800),    # столешницы, фасады
        (300, 600, 200, 500),     # полки, ящики
        (100, 300, 100, 300),     # царги, заглушки
        (1500, 2500, 100, 400),   # длинные раскладки (по длине листа)
    ]
    items = generate_directional_items(num_parts, ranges, W, H, seed)
    return items, W, H

def generate_vinyl_set(seed=None):
    """
    Виниловые покрытия (полы, обои): рулон 2000x20000 мм.
    Детали – полосы и фрагменты, рисунок требует стыковки по направлению.
    """
    W, H = 2000, 20000
    num_parts = random.randint(15, 30)
    # Преобладают длинные полосы (по длине рулона)
    ranges = [
        (500, 1900, 2000, 5000),   # крупные куски (по длине)
        (200, 800, 1000, 3000),    # средние
        (100, 300, 500, 1500),     # мелкие
    ]
    items = generate_directional_items(num_parts, ranges, W, H, seed)
    return items, W, H

def generate_paper_set(seed=None):
    """
    Бумага/картон с направлением волокон: лист 1000x1400 мм.
    Детали для полиграфии с фиксированной ориентацией (например, вдоль волокна для фальцовки).
    """
    W, H = 1000, 1400
    num_parts = random.randint(30, 60)
    ranges = [
        (200, 500, 300, 700),      # стандартные форматы
        (50, 150, 50, 200),        # этикетки
        (600, 950, 200, 400),      # обложки (длинная сторона вдоль волокна)
    ]
    items = generate_directional_items(num_parts, ranges, W, H, seed)
    return items, W, H

def generate_metal_directional_set(seed=None):
    """
    Металлопрокат с направлением прокатки: лист 1500x3000 мм.
    Важно для деталей, работающих на изгиб (направление волокна).
    """
    W, H = 1500, 3000
    num_parts = random.randint(20, 35)
    # Крупные детали вдоль проката, мелкие могут быть ориентированы произвольно, но поворот запрещён
    ranges = [
        (500, 1400, 200, 1000),    # длинномеры вдоль проката
        (200, 600, 200, 600),      # квадратные/прямоугольные
        (50, 200, 50, 200),        # мелкие
    ]
    items = generate_directional_items(num_parts, ranges, W, H, seed)
    return items, W, H

def generate_composite_directional_set(seed=None):
    """
    Композитные панели с направлением волокон: лист 2500x1800 мм.
    Смесь крупных, полос и мелких деталей с запретом поворота.
    """
    W, H = 2500, 1800
    num_parts = random.randint(40, 60)
    items = []
    # несколько крупных (ориентация важна)
    for _ in range(random.randint(3, 6)):
        w = random.randint(1000, 2000)
        h = random.randint(500, 1200)
        items.append({'w': w, 'h': h, 'rotatable': False})
    # несколько полос (ориентированных вдоль или поперёк, но поворот запрещён)
    for _ in range(random.randint(5, 10)):
        if random.random() < 0.5:
            w = random.randint(200, 400)
            h = random.randint(1000, 1600)
        else:
            w = random.randint(1000, 1600)
            h = random.randint(200, 400)
        items.append({'w': w, 'h': h, 'rotatable': False})
    # много мелких
    for _ in range(random.randint(20, 30)):
        w = random.randint(50, 300)
        h = random.randint(50, 300)
        items.append({'w': w, 'h': h, 'rotatable': False})
    random.shuffle(items)
    return items, W, H

# ----------------------------------------------------------------------
# Основная функция генерации наборов для направленных материалов
# ----------------------------------------------------------------------

def generate_directional_sets(num_sets=50, seed_start=3000):
    """
    Генерирует список наборов для материалов с фиксированным направлением.
    Каждый набор содержит детали с полем "rotatable": false.
    """
    random.seed(seed_start)
    sets = []
    generators = [
        generate_fabric_set,
        generate_laminate_set,
        generate_vinyl_set,
        generate_paper_set,
        generate_metal_directional_set,
        generate_composite_directional_set
    ]

    for i in range(num_sets):
        gen = random.choice(generators)
        seed = seed_start + i
        items, W, H = gen(seed=seed)
        type_name = gen.__name__.replace('generate_', '').replace('_set', '')
        name = f"{type_name}_{i+1:02d}"

        # Убедимся, что все детали помещаются (генераторы это гарантируют)
        sets.append({
            "название": name,
            "лист_ширина": W,
            "лист_высота": H,
            "детали": items
        })

    return sets

# ----------------------------------------------------------------------
# Сохранение в JSON
# ----------------------------------------------------------------------

def save_sets_to_file(sets, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({"наборы": sets}, f, ensure_ascii=False, indent=2)
    print(f"✅ Сохранено {len(sets)} наборов (с запретом поворота) в {filename}")

# ----------------------------------------------------------------------
# Пример использования
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Генерируем 30 наборов для направленных материалов
    directional_sets = generate_directional_sets(num_sets=100, seed_start=3000)
    save_sets_to_file(directional_sets, "data/directional_sets.json")