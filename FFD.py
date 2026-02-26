"""
Алгоритм First Fit Decreasing (FFD) для двумерного раскроя.
"""

from common.packing import bottom_left
from common.visualization import draw_sheets
from common.analysis import analyze_leftovers
from common.data import ALL_SETS  # W, H определим локально


def try_place_on_sheet(sheet_items, new_item, W, H, allow_rotation=True):
    """
    Пытается добавить новую деталь на существующий лист.
    sheet_items: список кортежей (x, y, w, h)
    new_item: словарь {'w': w, 'h': h}
    """
    # Пробуем без поворота
    pos = bottom_left(sheet_items, new_item['w'], new_item['h'], W, H)
    if pos is not None:
        return sheet_items + [(pos[0], pos[1], new_item['w'], new_item['h'])]

    if allow_rotation:
        pos = bottom_left(sheet_items, new_item['h'], new_item['w'], W, H)
        if pos is not None:
            return sheet_items + [(pos[0], pos[1], new_item['h'], new_item['w'])]

    return None


def ffd(items, W, H, allow_rotation=True):
    """
    First Fit Decreasing для двумерного раскроя.

    items: список словарей [{'w': w1, 'h': h1}, ...]
    W, H: размеры листа
    allow_rotation: разрешён ли поворот на 90°

    Возвращает список листов, каждый лист — список кортежей (x, y, w, h)
    """
    # Сортировка по убыванию площади
    sorted_items = sorted(items, key=lambda d: d['w'] * d['h'], reverse=True)

    sheets = []  # список листов

    for item in sorted_items:
        placed = False
        # Пробуем разместить на существующих листах
        for i, sheet in enumerate(sheets):
            new_sheet = try_place_on_sheet(sheet, item, W, H, allow_rotation)
            if new_sheet is not None:
                sheets[i] = new_sheet
                placed = True
                break
        # Если не удалось, создаём новый лист
        if not placed:
            # Проверяем, помещается ли деталь вообще
            if item['w'] <= W and item['h'] <= H:
                sheets.append([(0, 0, item['w'], item['h'])])
            elif allow_rotation and item['h'] <= W and item['w'] <= H:
                sheets.append([(0, 0, item['h'], item['w'])])
            else:
                print(f"Предупреждение: деталь {item} не помещается на листе, пропущена.")
    return sheets


def print_sheets_info(sheets):
    """Выводит информацию о листах."""
    print(f"Всего использовано листов: {len(sheets)}")
    for i, sheet in enumerate(sheets):
        print(f"Лист {i + 1}: {len(sheet)} деталей")
        for (x, y, w, h) in sheet:
            print(f"   ({x}, {y}) {w} x {h}")


if __name__ == "__main__":
    # Выбери набор для тестирования
    test_set = ALL_SETS["set_C (крупные)"]
    test_name = "Набор C (крупные)"
    W, H = 20, 20

    print(f"\n=== {test_name} ===\n")
    sheets = ffd(test_set, W, H, allow_rotation=True)
    print_sheets_info(sheets)
    draw_sheets(sheets, W, H, f"FFD – {test_name}")

    stats = analyze_leftovers(sheets, test_set, W, H)
    print(f"\n--- Анализ остатков ---")
    print(f"Общая площадь остатков: {stats['total_leftover_area']}")
    print(f"Площадь полезных остатков: {stats['usable_leftover_area']}")
    print(f"Количество полезных областей: {stats['num_usable_regions']}")
    print(f"Коэффициент использования материала: {stats['utilization_rate']:.2f}%")