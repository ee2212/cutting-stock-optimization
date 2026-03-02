# -*- coding: utf-8 -*-
"""
Генератор разнообразных тестовых наборов для задачи раскроя.
Создаёт наборы с разными размерами листов и типами деталей,
имитирующие реальные производственные задачи (металл, мебель, стекло, пластик),
а также специальные сложные конфигурации для проверки алгоритмов.
"""

import json
import random
import os


# ----------------------------------------------------------------------
# Базовые генераторы
# ----------------------------------------------------------------------

def generate_random_uniform(num_parts, min_size, max_size, W, H, seed=None):
    """Случайные прямоугольники с равномерным распределением размеров."""
    if seed is not None:
        random.seed(seed)
    items = []
    for _ in range(num_parts):
        w = random.randint(min_size, min(max_size, W))
        h = random.randint(min_size, min(max_size, H))
        items.append({'w': w, 'h': h})
    return items


def generate_mixed_sizes(num_parts, large_ratio, large_min, large_max,
                         small_min, small_max, W, H, seed=None):
    """
    Набор с заданной долей крупных деталей и остальными мелкими.
    large_ratio – доля крупных (0..1).
    large_min, large_max – диапазон для крупных.
    small_min, small_max – для мелких.
    """
    if seed is not None:
        random.seed(seed)
    items = []
    n_large = int(num_parts * large_ratio)
    n_small = num_parts - n_large

    for _ in range(n_large):
        w = random.randint(large_min, min(large_max, W))
        h = random.randint(large_min, min(large_max, H))
        items.append({'w': w, 'h': h})

    for _ in range(n_small):
        w = random.randint(small_min, min(small_max, W))
        h = random.randint(small_min, min(small_max, H))
        items.append({'w': w, 'h': h})

    random.shuffle(items)
    return items


def generate_strip_set(num_parts, strip_ratio, strip_width_range, strip_height_range,
                       other_min, other_max, W, H, seed=None):
    """
    Набор с длинными полосами (узкие и длинные) и остальными прямоугольниками.
    strip_ratio – доля полос.
    strip_width_range – (min, max) для ширины полос (узкая).
    strip_height_range – (min, max) для высоты полос (длинная).
    other_min, other_max – диапазон для остальных деталей.
    """
    if seed is not None:
        random.seed(seed)
    items = []
    n_strips = int(num_parts * strip_ratio)
    n_other = num_parts - n_strips

    for _ in range(n_strips):
        if random.random() < 0.5:
            # горизонтальная полоса (широкая, низкая)
            w_min, w_max = strip_width_range
            h_min, h_max = strip_height_range
            # Проверяем, что min <= max
            w = random.randint(w_min, min(w_max, W))
            h = random.randint(h_min, min(h_max, H))
        else:
            # вертикальная полоса (узкая, высокая)
            w_min, w_max = strip_height_range
            h_min, h_max = strip_width_range
            w = random.randint(w_min, min(w_max, W))
            h = random.randint(h_min, min(h_max, H))
        items.append({'w': w, 'h': h})

    for _ in range(n_other):
        w = random.randint(other_min, min(other_max, W))
        h = random.randint(other_min, min(other_max, H))
        items.append({'w': w, 'h': h})

    random.shuffle(items)
    return items


# ----------------------------------------------------------------------
# Отраслевые генераторы (размеры в миллиметрах, но можно масштабировать)
# ----------------------------------------------------------------------

def generate_metal_set(seed=None):
    """Металлообработка: лист 1500x3000, детали от 50 до 1200 мм."""
    W, H = 1500, 3000
    num_parts = random.randint(20, 35)
    # 10–20% крупных, остальные средние и мелкие
    return generate_mixed_sizes(
        num_parts=num_parts,
        large_ratio=0.15,
        large_min=500, large_max=1200,
        small_min=50, small_max=400,
        W=W, H=H, seed=seed
    ), W, H


def generate_furniture_set(seed=None):
    """Мебельное производство: ЛДСП 2440x1220, детали от 100 до 1000 мм."""
    W, H = 2440, 1220
    num_parts = random.randint(25, 40)
    # мебель часто содержит много одинаковых или близких по размеру деталей
    items = []
    base_sizes = [(800, 400), (600, 300), (500, 500), (400, 200), (300, 150)]
    for _ in range(num_parts):
        base = random.choice(base_sizes)
        w = base[0] + random.randint(-50, 50)
        h = base[1] + random.randint(-50, 50)
        w = max(50, min(w, W))
        h = max(50, min(h, H))
        items.append({'w': w, 'h': h})
    random.shuffle(items)
    return items, W, H


def generate_glass_set(seed=None):
    """Стекольная промышленность: лист 3210x2000, детали от 200 до 1500 мм."""
    W, H = 3210, 2000
    num_parts = random.randint(15, 30)
    return generate_mixed_sizes(
        num_parts=num_parts,
        large_ratio=0.2,
        large_min=800, large_max=1500,
        small_min=200, small_max=700,
        W=W, H=H, seed=seed
    ), W, H


def generate_plastic_set(seed=None):
    """Пластик: лист 2000x4000, детали от 100 до 1500 мм, много длинных полос."""
    W, H = 2000, 4000
    num_parts = random.randint(30, 50)
    return generate_strip_set(
        num_parts=num_parts,
        strip_ratio=0.3,
        strip_width_range=(100, 300),
        strip_height_range=(1000, 3500),
        other_min=200, other_max=800,
        W=W, H=H, seed=seed
    ), W, H


def generate_composite_set(seed=None):
    """Сложный композитный набор: крупный лист, смесь всего."""
    W, H = 2500, 1800
    num_parts = random.randint(40, 60)
    # комбинация нескольких подходов
    items = []
    # несколько крупных
    for _ in range(random.randint(3, 6)):
        w = random.randint(1000, 2000)
        h = random.randint(500, 1200)
        items.append({'w': w, 'h': h})
    # несколько полос
    for _ in range(random.randint(5, 10)):
        if random.random() < 0.5:
            w = random.randint(200, 400)
            h = random.randint(1000, 1600)
        else:
            w = random.randint(1000, 1600)
            h = random.randint(200, 400)
        items.append({'w': w, 'h': h})
    # много мелких
    for _ in range(random.randint(20, 30)):
        w = random.randint(50, 300)
        h = random.randint(50, 300)
        items.append({'w': w, 'h': h})
    random.shuffle(items)
    return items, W, H


# ----------------------------------------------------------------------
# Основная функция генерации разнообразных наборов
# ----------------------------------------------------------------------
def generate_diverse_sets(num_sets=50, seed_start=1000):
    """
    Генерирует список разнообразных наборов.
    num_sets – общее количество наборов.
    seed_start – начальное значение для генератора, каждый набор получит свой seed.
    """
    random.seed(seed_start)
    sets = []
    generators = [
        generate_strip_set
    ]

    for i in range(num_sets):
        # Выбираем случайный генератор
        gen = random.choice(generators)
        seed = seed_start + i

        if gen in (generate_metal_set, generate_furniture_set,
                   generate_glass_set, generate_plastic_set,
                   generate_composite_set):
            # отраслевые генераторы возвращают (items, W, H)
            items, W, H = gen(seed=seed)
            type_name = gen.__name__.replace('generate_', '').replace('_set', '')
            name = f"{type_name}_{i+1:02d}"
        else:
            # универсальные генераторы требуют дополнительных параметров
            # зададим их случайным образом
            W = random.choice([1500, 2000, 2440, 2500, 3000, 3210, 4000])
            H = random.choice([1000, 1220, 1500, 2000, 2500, 3000, 4000, 6000])
            num_parts = random.randint(20, 60)

            if gen == generate_strip_set:
                strip_ratio = random.uniform(0.2, 0.4)
                
                # Генерируем диапазоны с проверкой, чтобы min < max
                strip_width_min = random.randint(30, 100)
                strip_width_max = random.randint(strip_width_min + 50, 300)  # гарантируем strip_width_min < strip_width_max
                strip_width_range = (strip_width_min, strip_width_max)
                
                strip_height_min = random.randint(800, 1200)
                # Убеждаемся, что максимальная высота не превышает H
                strip_height_max = min(random.randint(strip_height_min + 200, 4000), H)
                strip_height_range = (strip_height_min, strip_height_max)
                
                other_min = random.randint(50, 200)
                other_max = random.randint(other_min + 50, 600)
                
                items = generate_strip_set(
                    num_parts=num_parts,
                    strip_ratio=strip_ratio,
                    strip_width_range=strip_width_range,
                    strip_height_range=strip_height_range,
                    other_min=other_min, other_max=other_max,
                    W=W, H=H, seed=seed
                )
                type_name = "strip"
            else:
                continue

            name = f"{type_name}_{i+1:02d}"

        # Убедимся, что все детали помещаются (при необходимости можно отсеять, но генераторы должны гарантировать)
        # Добавляем набор в список
        sets.append({
            "название": name,
            "лист_ширина": W,
            "лист_высота": H,
            "детали": items
        })

    return sets
# def generate_diverse_sets(num_sets=50, seed_start=1000):
#     """
#     Генерирует список разнообразных наборов.
#     num_sets – общее количество наборов.
#     seed_start – начальное значение для генератора, каждый набор получит свой seed.
#     """
#     random.seed(seed_start)
#     sets = []
#     generators = [
#         # generate_random_uniform,
#         # generate_mixed_sizes,
#          generate_strip_set
#         # generate_metal_set,
#         # generate_furniture_set,
#         # generate_glass_set,
#         # generate_plastic_set
#         # generate_composite_set,
#     ]

#     for i in range(num_sets):
#         # Выбираем случайный генератор
#         gen = random.choice(generators)
#         seed = seed_start + i

#         if gen in (generate_metal_set, generate_furniture_set,
#                    generate_glass_set, generate_plastic_set,
#                    generate_composite_set):
#             # отраслевые генераторы возвращают (items, W, H)
#             items, W, H = gen(seed=seed)
#             type_name = gen.__name__.replace('generate_', '').replace('_set', '')
#             name = f"{type_name}_{i+1:02d}"
#         else:
#             # универсальные генераторы требуют дополнительных параметров
#             # зададим их случайным образом
#             W = random.choice([1500, 2000, 2440, 2500, 3000, 3210, 4000])
#             H = random.choice([1000, 1220, 1500, 2000, 2500, 3000, 4000, 6000])
#             num_parts = random.randint(20, 60)

#             if gen == generate_random_uniform:
#                 min_size = random.randint(50, 200)
#                 max_size = random.randint(500, 1500)
#                 items = generate_random_uniform(
#                     num_parts=num_parts,
#                     min_size=min_size, max_size=max_size,
#                     W=W, H=H, seed=seed
#                 )
#                 type_name = "uniform"
#             elif gen == generate_mixed_sizes:
#                 large_ratio = random.uniform(0.1, 0.3)
#                 large_min = random.randint(400, 800)
#                 large_max = random.randint(1000, 2000)
#                 small_min = random.randint(20, 100)
#                 small_max = random.randint(150, 400)
#                 items = generate_mixed_sizes(
#                     num_parts=num_parts,
#                     large_ratio=large_ratio,
#                     large_min=large_min, large_max=large_max,
#                     small_min=small_min, small_max=small_max,
#                     W=W, H=H, seed=seed
#                 )
#                 type_name = "mixed"
#             elif gen == generate_strip_set:
#                 strip_ratio = random.uniform(0.2, 0.4)
#                 strip_width_range = (random.randint(30, 100), random.randint(150, 300))
#                 strip_height_range = (random.randint(800, 1200), random.randint(2000, 4000))
#                 other_min = random.randint(50, 200)
#                 other_max = random.randint(300, 600)
#                 items = generate_strip_set(
#                     num_parts=num_parts,
#                     strip_ratio=strip_ratio,
#                     strip_width_range=strip_width_range,
#                     strip_height_range=strip_height_range,
#                     other_min=other_min, other_max=other_max,
#                     W=W, H=H, seed=seed
#                 )
#                 type_name = "strip"
#             else:
#                 continue

#             name = f"{type_name}_{f'3{i+1:02d}'}"

#         # Убедимся, что все детали помещаются (при необходимости можно отсеять, но генераторы должны гарантировать)
#         # Добавляем набор в список
#         sets.append({
#             "название": name,
#             "лист_ширина": W,
#             "лист_высота": H,
#             "детали": items
#         })

#     return sets


# ----------------------------------------------------------------------
# Сохранение в JSON
# ----------------------------------------------------------------------

def save_sets_to_file(sets, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({"наборы": sets}, f, ensure_ascii=False, indent=2)
    print(f"✅ Сохранено {len(sets)} наборов в {filename}")


# ----------------------------------------------------------------------
# Пример использования
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Генерируем 100 разнообразных наборов
    diverse_sets = generate_diverse_sets(num_sets=30, seed_start=2025)
    save_sets_to_file(diverse_sets, "data/diverse_sets_strips1.json")

    # Также можно сгенерировать отдельные файлы для каждого типа, если нужно
    # Но для общей работы достаточно одного большого файла.