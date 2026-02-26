"""
Визуализация результатов упаковки.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from .packing import pack_sequence


def draw_sheets(sheets, W, H, title="Упаковка"):
    """
    Рисует все листы с деталями (принимает готовый sheets).
    """
    n = len(sheets)
    if n == 0:
        print("Нет листов для отображения.")
        return

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
            rect = patches.Rectangle((x, y), w, h, linewidth=2,
                                     edgecolor='blue', facecolor='lightblue')
            ax.add_patch(rect)
            ax.text(x + w / 2, y + h / 2, f"{w}x{h}",
                    ha='center', va='center', fontsize=8)

    plt.suptitle(title)
    plt.tight_layout()
    plt.show()


def draw_sheets_from_sequence(seq, rot, items, W, H, title="Упаковка"):
    """
    Строит упаковку по последовательности и поворотам и рисует листы.
    """
    sheets, _ = pack_sequence(seq, items, W, H, rotations=rot)
    if sheets is None:
        return
    draw_sheets(sheets, W, H, title)