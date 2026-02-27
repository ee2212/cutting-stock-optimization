# generate_complex_sets.py
import json
import os
import random

def save_sets_to_file(sets, filename="data/complex_sets.json"):
    """Сохраняет список наборов в JSON-файл."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({"наборы": sets}, f, ensure_ascii=False, indent=2)
    print(f"Сохранено {len(sets)} наборов в {filename}")

# -------------------- Базовые генераторы --------------------

def generate_random_set(num_parts, min_size=2, max_size=15, W=20, H=20, seed=None):
    """Случайный набор прямоугольников."""
    if seed is not None:
        random.seed(seed)
    items = []
    for _ in range(num_parts):
        w = random.randint(min_size, min(max_size, W))
        h = random.randint(min_size, min(max_size, H))
        items.append({'w': w, 'h': h})
    return items

def generate_large_small_set(num_parts, large_ratio=0.2, W=20, H=20, seed=None):
    """
    Набор, где часть деталей крупные, остальные мелкие.
    large_ratio – доля крупных деталей.
    """
    if seed is not None:
        random.seed(seed)
    items = []
    num_large = int(num_parts * large_ratio)
    num_small = num_parts - num_large
    for _ in range(num_large):
        w = random.randint(12, W)
        h = random.randint(12, H)
        items.append({'w': w, 'h': h})
    for _ in range(num_small):
        w = random.randint(2, 5)
        h = random.randint(2, 5)
        items.append({'w': w, 'h': h})
    random.shuffle(items)
    return items

def generate_strip_set(num_parts, strip_ratio=0.3, W=20, H=20, seed=None):
    """
    Набор, содержащий вытянутые полосы (узкие и длинные).
    strip_ratio – доля полос.
    """
    if seed is not None:
        random.seed(seed)
    items = []
    num_strips = int(num_parts * strip_ratio)
    num_others = num_parts - num_strips
    for _ in range(num_strips):
        if random.random() < 0.5:
            w = random.randint(1, 3)
            h = random.randint(10, H)
        else:
            w = random.randint(10, W)
            h = random.randint(1, 3)
        items.append({'w': w, 'h': h})
    for _ in range(num_others):
        w = random.randint(4, 10)
        h = random.randint(4, 10)
        items.append({'w': w, 'h': h})
    random.shuffle(items)
    return items

def generate_rotation_constrained_set(num_parts, allowed_rotations=None, W=20, H=20, seed=None):
    """
    Набор с ограниченными поворотами. allowed_rotations – список допустимых углов (0, 90, 180...),
    но для простоты мы просто добавляем флаг, но в данных это не отражается.
    Здесь просто генерируем случайные детали, но с пометкой в названии.
    """
    if seed is not None:
        random.seed(seed)
    items = []
    for _ in range(num_parts):
        w = random.randint(2, W)
        h = random.randint(2, H)
        items.append({'w': w, 'h': h})
    return items

def generate_hard_set(num_parts, W=20, H=20, seed=None):
    """
    Комбинированный сложный набор: несколько крупных, много мелких, несколько полос.
    """
    if seed is not None:
        random.seed(seed)
    items = []
    # Крупные
    num_large = max(1, int(num_parts * 0.15))
    for _ in range(num_large):
        w = random.randint(15, W)
        h = random.randint(12, H)
        items.append({'w': w, 'h': h})
    # Полосы
    num_strips = max(1, int(num_parts * 0.2))
    for _ in range(num_strips):
        if random.random() < 0.5:
            w = random.randint(1, 3)
            h = random.randint(10, H)
        else:
            w = random.randint(10, W)
            h = random.randint(1, 3)
        items.append({'w': w, 'h': h})
    # Остальные – случайные средние и мелкие
    num_rest = num_parts - num_large - num_strips
    for _ in range(num_rest):
        w = random.randint(2, 10)
        h = random.randint(2, 10)
        items.append({'w': w, 'h': h})
    random.shuffle(items)
    return items

# -------------------- Создание полного набора --------------------

def generate_all_complex_sets():
    """Генерирует несколько наборов разной сложности и возвращает список."""
    sets = []
    base_W, base_H = 20, 20

    # 1. Несколько случайных наборов разного размера
    for size in [20, 30, 40, 50]:
        items = generate_random_set(size, seed=size)
        sets.append({
            "название": f"random_{size}",
            "лист_ширина": base_W,
            "лист_высота": base_H,
            "детали": items
        })

    # 2. Наборы с крупными и мелкими деталями
    for size in [30, 50]:
        items = generate_large_small_set(size, large_ratio=0.2, seed=size+100)
        sets.append({
            "название": f"large_small_{size}",
            "лист_ширина": base_W,
            "лист_высота": base_H,
            "детали": items
        })

    # 3. Наборы с полосами
    for size in [30, 50]:
        items = generate_strip_set(size, strip_ratio=0.3, seed=size+200)
        sets.append({
            "название": f"strips_{size}",
            "лист_ширина": base_W,
            "лист_высота": base_H,
            "детали": items
        })

    # 4. Один сложный набор
    items = generate_hard_set(60, seed=999)
    sets.append({
        "название": "hard_60",
        "лист_ширина": base_W,
        "лист_высота": base_H,
        "детали": items
    })

    # 5. Набор с ограничением поворота (для информации, данные обычные, но название отражает)
    items = generate_rotation_constrained_set(40, seed=42)
    sets.append({
        "название": "rot_constrained_40",
        "лист_ширина": base_W,
        "лист_высота": base_H,
        "детали": items
    })

    return sets

if __name__ == "__main__":
    sets = generate_all_complex_sets()
    save_sets_to_file(sets, "data/complex_sets.json")
    print("Генерация завершена.")