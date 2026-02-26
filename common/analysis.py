"""
Анализ остатков материала.
"""

def analyze_leftovers(sheets, items, W, H):
    """
    Анализирует полезные остатки на каждом листе после упаковки.

    Параметры:
    - sheets: список листов, каждый лист — список кортежей (x, y, w, h)
    - items: исходный список деталей (для определения минимального размера)
    - W, H: размеры листа

    Возвращает словарь с информацией:
    - total_leftover_area: общая площадь пустого пространства
    - usable_leftover_area: площадь, пригодная для самой маленькой детали
    - num_usable_regions: количество полезных областей
    - sheet_details: список по листам с деталями
    - utilization_rate: процент использования материала
    """
    # Минимальные габариты детали (с учётом возможного поворота)
    min_w = min(item['w'] for item in items)
    min_h = min(item['h'] for item in items)

    total_leftover_area = 0
    usable_leftover_area = 0
    num_usable_regions = 0
    sheet_details = []

    for sheet_idx, sheet in enumerate(sheets):
        # Собираем все значимые координаты (границы деталей и листа)
        x_coords = [0] + sorted(set([x for (x, y, w, h) in sheet] + [x + w for (x, y, w, h) in sheet])) + [W]
        y_coords = [0] + sorted(set([y for (x, y, w, h) in sheet] + [y + h for (x, y, w, h) in sheet])) + [H]

        sheet_leftover = 0
        sheet_usable = 0
        sheet_regions = 0

        # Перебираем все ячейки, образованные соседними координатами
        for i in range(len(x_coords)-1):
            for j in range(len(y_coords)-1):
                x1, x2 = x_coords[i], x_coords[i+1]
                y1, y2 = y_coords[j], y_coords[j+1]

                # Проверяем, не занята ли ячейка какой-либо деталью
                occupied = False
                for (px, py, pw, ph) in sheet:
                    if not (x2 <= px or x1 >= px + pw or y2 <= py or y1 >= py + ph):
                        occupied = True
                        break

                if not occupied:
                    area = (x2 - x1) * (y2 - y1)
                    sheet_leftover += area
                    width = x2 - x1
                    height = y2 - y1
                    # Проверяем, можно ли разместить самую маленькую деталь (с поворотом)
                    if (width >= min_w and height >= min_h) or (width >= min_h and height >= min_w):
                        sheet_usable += area
                        sheet_regions += 1

        total_leftover_area += sheet_leftover
        usable_leftover_area += sheet_usable
        num_usable_regions += sheet_regions

        sheet_details.append({
            'sheet_index': sheet_idx,
            'num_parts': len(sheet),
            'leftover_area': sheet_leftover,
            'usable_area': sheet_usable,
            'usable_regions': sheet_regions
        })

    total_area = len(sheets) * W * H
    utilization = (total_area - total_leftover_area) / total_area * 100 if total_area > 0 else 0

    return {
        'total_leftover_area': total_leftover_area,
        'usable_leftover_area': usable_leftover_area,
        'num_usable_regions': num_usable_regions,
        'sheet_details': sheet_details,
        'utilization_rate': utilization
    }