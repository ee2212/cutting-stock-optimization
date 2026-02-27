# SA.py
"""
Имитация отжига (Simulated Annealing) для задачи двумерного раскроя.
Модифицирована для приёма начального решения (например, от FFD) с возможностью None-поворотов.
"""

import random
import math
from copy import deepcopy
from common.packing import pack_sequence

# ====================== Вспомогательные геометрические функции ======================
def can_place(placed, x, y, w, h, W, H):
    if x < 0 or y < 0 or x + w > W or y + h > H:
        return False
    for (px, py, pw, ph) in placed:
        if not (x + w <= px or x >= px + pw or y + h <= py or y >= py + ph):
            return False
    return True

def bottom_left(placed, w, h, W, H):
    xs = [0]
    for (px, py, pw, ph) in placed:
        xs.append(px + pw)
    xs = sorted(set(xs))
    xs = [x for x in xs if x + w <= W]

    ys = [0]
    for (px, py, pw, ph) in placed:
        ys.append(py + ph)
    ys = sorted(set(ys))

    best_x, best_y = None, None
    for y in ys:
        for x in xs:
            if can_place(placed, x, y, w, h, W, H):
                if best_y is None or y < best_y or (y == best_y and x < best_x):
                    best_y = y
                    best_x = x
    if best_x is not None:
        return (best_x, best_y)
    return None

# ====================== Генерация соседнего решения ======================
def generate_neighbor(sequence, rotations=None, prob_swap=0.7, allow_rotation=True):
    new_seq = sequence[:]
    new_rot = rotations[:] if rotations is not None else None

    if random.random() < prob_swap:
        i, j = random.sample(range(len(new_seq)), 2)
        new_seq[i], new_seq[j] = new_seq[j], new_seq[i]
        if new_rot is not None:
            new_rot[i], new_rot[j] = new_rot[j], new_rot[i]
    else:
        if allow_rotation and new_rot is not None:
            i = random.randrange(len(new_rot))
            new_rot[i] = 1 - new_rot[i]
    return new_seq, new_rot

# ====================== Основная функция имитации отжига ======================
def simulated_annealing(items, W, H, allow_rotation=True,
                        initial_temp=100.0, cooling_rate=0.95,
                        min_temp=1.0, iterations_per_temp=100,
                        max_no_improve=50, verbose=True,
                        return_sheets=False,
                        initial_solution=None):   # новый параметр
    """
    Запускает имитацию отжига.
    Если initial_solution передан (кортеж (seq, rot)), использует его как начальное.
    rot может быть None (автоматический выбор поворота) или списком.
    Иначе генерирует случайное.
    """
    n = len(items)
    if initial_solution is not None:
        current_seq, current_rot = initial_solution
        if len(current_seq) != n:
            raise ValueError("Initial sequence length does not match number of items")
        # Не меняем current_rot, оставляем как есть (может быть None)
    else:
        current_seq = list(range(n))
        random.shuffle(current_seq)
        current_rot = [random.randint(0, 1) for _ in range(n)] if allow_rotation else None

    # Функция стоимости (количество листов)
    def cost(seq, rot):
        _, n_sheets = pack_sequence(seq, items, W, H, rotations=rot)
        return n_sheets

    current_cost = cost(current_seq, current_rot)
    best_seq = current_seq[:]
    best_rot = deepcopy(current_rot) if current_rot else None
    best_cost = current_cost

    temp = initial_temp
    no_improve = 0

    if verbose:
        print("Начало имитации отжига")
        print(f"Начальная температура: {temp}, коэффициент охлаждения: {cooling_rate}")
        print(f"Начальное решение: {current_cost} листов")

    while temp > min_temp and no_improve < max_no_improve:
        for _ in range(iterations_per_temp):
            new_seq, new_rot = generate_neighbor(current_seq, current_rot, allow_rotation=allow_rotation)
            new_cost = cost(new_seq, new_rot)
            delta = new_cost - current_cost

            if delta < 0 or random.random() < math.exp(-delta / temp):
                current_seq, current_rot = new_seq, new_rot
                current_cost = new_cost
                if current_cost < best_cost:
                    best_seq = current_seq[:]
                    best_rot = deepcopy(current_rot) if current_rot else None
                    best_cost = current_cost
                    no_improve = 0
                else:
                    no_improve += 1
            else:
                no_improve += 1

        temp *= cooling_rate
        if verbose and no_improve % (iterations_per_temp * 5) == 0:
            print(f"Температура: {temp:.2f}, текущая стоимость: {current_cost}, лучшая: {best_cost}")

    if verbose:
        print("Завершено.")
        print(f"Лучшее решение: {best_cost} листов")

    if return_sheets:
        best_sheets, _ = pack_sequence(best_seq, items, W, H, rotations=best_rot)
        return best_seq, best_rot, best_cost, best_sheets
    else:
        return best_seq, best_rot, best_cost

# ====================== Визуализация ======================
def draw_sheets_from_sequence(seq, rot, items, W, H, title="SA упаковка"):
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    sheets, _ = pack_sequence(seq, items, W, H, rotations=rot)
    if sheets is None:
        return

    n = len(sheets)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 5))
    if n == 1:
        axes = [axes]

    for idx, sheet in enumerate(sheets):
        ax = axes[idx]
        ax.set_xlim(0, W)
        ax.set_ylim(0, H)
        ax.set_aspect('equal')
        ax.set_title(f"Лист {idx + 1}")
        ax.set_xlabel("x")
        ax.set_ylabel("y")

        for (x, y, w, h) in sheet:
            rect = patches.Rectangle((x, y), w, h, linewidth=2, edgecolor='green', facecolor='lightgreen')
            ax.add_patch(rect)
            ax.text(x + w / 2, y + h / 2, f"{w}x{h}", ha='center', va='center', fontsize=8)

    plt.suptitle(title)
    plt.tight_layout()
    plt.show()

# ====================== Тестовый запуск ======================
if __name__ == "__main__":
    test_items = [{'w': 5, 'h': 5}] * 3
    best_seq, best_rot, best_cost = simulated_annealing(
        items=test_items, W=20, H=20, allow_rotation=True,
        initial_temp=100, cooling_rate=0.95, min_temp=1,
        iterations_per_temp=100, max_no_improve=50,
        verbose=True, return_sheets=False
    )
    print("Лучшая стоимость:", best_cost)
    draw_sheets_from_sequence(best_seq, best_rot, test_items, 20, 20)