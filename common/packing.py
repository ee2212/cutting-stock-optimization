"""
Базовые функции для укладки прямоугольников на лист.
"""

def can_place(placed, x, y, w, h, W, H):
    """
    Проверяет, можно ли разместить прямоугольник (w, h) с координатами
    левого нижнего угла (x, y) на листе W x H, не пересекаясь с уже
    размещёнными деталями (placed).

    placed: список кортежей (px, py, pw, ph)
    """
    if x < 0 or y < 0 or x + w > W or y + h > H:
        return False
    for (px, py, pw, ph) in placed:
        if not (x + w <= px or x >= px + pw or y + h <= py or y >= py + ph):
            return False
    return True


def bottom_left(placed, w, h, W, H):
    """
    Находит самую нижнюю (минимальный y) и среди них самую левую (минимальный x)
    позицию для прямоугольника (w, h) на листе с уже размещёнными деталями.
    Возвращает (x, y) или None, если места нет.

    Поиск выполняется перебором всех возможных позиций, которые образуются
    правыми и верхними гранями уже размещённых деталей, а также границами листа.
    """
    # Множество потенциальных x-координат: 0 и правые границы деталей
    xs = [0]
    for (px, py, pw, ph) in placed:
        xs.append(px + pw)
    xs = sorted(set(xs))
    xs = [x for x in xs if x + w <= W]

    # Множество потенциальных y-координат: 0 и верхние границы деталей
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


def pack_sequence(sequence, items, W, H, rotations=None):
    """
    Упаковывает детали в заданном порядке sequence с использованием bottom_left.

    Параметры:
    - sequence: список индексов деталей (порядок укладки)
    - items: исходный список деталей [{'w': w, 'h': h}, ...]
    - W, H: размеры листа
    - rotations: список флагов поворота (0/1) той же длины, что и sequence.
                 Если None, поворот не применяется (каждая деталь пробуется в обеих ориентациях).

    Возвращает:
    - sheets: список листов, каждый лист — список кортежей (x, y, w, h)
    - n_sheets: количество использованных листов
    """
    sheets = []
    for idx in sequence:
        item = items[idx]
        w, h = item['w'], item['h']

        # Если заданы явные повороты, применяем их до укладки
        if rotations is not None:
            if rotations[idx] == 1:
                w, h = h, w
            # В этом режиме мы не пробуем альтернативную ориентацию
            orientations = [(w, h)]
        else:
            # Иначе пробуем обе ориентации (прямую и повёрнутую)
            orientations = [(w, h), (h, w)] if w != h else [(w, h)]

        placed = False
        # Пробуем разместить на существующих листах
        for sheet in sheets:
            for (pw, ph) in orientations:
                pos = bottom_left(sheet, pw, ph, W, H)
                if pos is not None:
                    sheet.append((pos[0], pos[1], pw, ph))
                    placed = True
                    break
            if placed:
                break

        if not placed:
            # Не удалось разместить на существующих листах — создаём новый
            new_sheet = []
            for (pw, ph) in orientations:
                if pw <= W and ph <= H:
                    new_sheet.append((0, 0, pw, ph))
                    sheets.append(new_sheet)
                    placed = True
                    break
            if not placed:
                # Деталь не помещается даже одна (не должно случаться при корректных данных)
                print(f"Ошибка: деталь {item} не помещается на листе {W}x{H}.")
                return None, float('inf')

    return sheets, len(sheets)