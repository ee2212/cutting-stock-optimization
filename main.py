# main.py
from common.data import load_test_sets, load_generated_sets
from common.analysis import analyze_leftovers
from common.packing import pack_sequence
from FFD import ffd
from SA import simulated_annealing

import json
with open("data/complex_sets.json", "r", encoding="utf-8") as f:
    complex_data = json.load(f)
    complex_sets = complex_data["наборы"]


def run_comparison(max_parts=100, sa_fast_mode=True):
    """
    Сравнение FFD и SA на всех доступных наборах.
    SA стартует с решения, полученного FFD (порядок по убыванию площади).
    """
    manual_sets = load_test_sets()
    generated_sets = load_generated_sets()
    
    all_sets = manual_sets + generated_sets + complex_sets

    # Фильтруем по количеству деталей
    filtered_sets = [s for s in all_sets if len(s["детали"]) <= max_parts]
    skipped = len(all_sets) - len(filtered_sets)

    print("\n" + "=" * 150)
    print(f"Загружено наборов: всего {len(all_sets)}, обрабатывается {len(filtered_sets)} (пропущено {skipped} из-за лимита {max_parts} деталей)")
    print("=" * 150)
    print(f"{'Набор':<25} {'Дет':<4} {'WxH':<10} "
          f"{'FFD л':<4} {'FFD ост':<6} {'FFD %':<5} "
          f"{'SA ср':<6} {'SA л':<4} {'SA ост':<6} {'SA %':<5} "
          f"{'Улучш%':<6} {'Разн ост':<12}")
    print("=" * 150)

    for ts in filtered_sets:
        name = ts["название"]
        items = ts["детали"]
        W = ts["лист_ширина"]
        H = ts["лист_высота"]
        n = len(items)

        # ----- FFD -----
        sheets_ffd = ffd(items, W, H, allow_rotation=True)
        cost_ffd = len(sheets_ffd)
        stats_ffd = analyze_leftovers(sheets_ffd, items, W, H)
        usable_ffd = stats_ffd['usable_leftover_area']
        util_ffd = stats_ffd['utilization_rate']

        # ----- Получаем начальное решение от FFD -----
        # Порядок укладки FFD: сортировка по убыванию площади
        ffd_order = sorted(range(n), key=lambda i: items[i]['w'] * items[i]['h'], reverse=True)
        initial_solution = (ffd_order, None)

        # ----- SA с адаптивными параметрами -----
        n_runs = 5
        if n > 30:
            sa_params = {
                'initial_temp': 200.0,
                'cooling_rate': 0.99,
                'min_temp': 0.1,
                'iterations_per_temp': 500,
                'max_no_improve': 200,
            }
        elif n > 20:
            sa_params = {
                'initial_temp': 100.0,
                'cooling_rate': 0.95,
                'min_temp': 1.0,
                'iterations_per_temp': 200,
                'max_no_improve': 100,
            }
        else:
            sa_params = {
                'initial_temp': 80.0,
                'cooling_rate': 0.9,
                'min_temp': 5.0,
                'iterations_per_temp': 100,
                'max_no_improve': 50,
            }

        sa_costs = []
        sa_best_seq = sa_best_rot = None
        sa_best_cost = float('inf')
        for run in range(n_runs):
            seq, rot, cost = simulated_annealing(
                items=items, W=W, H=H, allow_rotation=True,
                **sa_params, verbose=False,
                initial_solution=initial_solution   # передаём решение от FFD
            )
            sa_costs.append(cost)
            if cost < sa_best_cost:
                sa_best_cost = cost
                sa_best_seq = seq
                sa_best_rot = rot

        # Получаем sheets и статистику для лучшего решения SA
        if sa_best_seq is not None:
            sa_best_sheets, _ = pack_sequence(sa_best_seq, items, W, H, rotations=sa_best_rot)
            stats_sa = analyze_leftovers(sa_best_sheets, items, W, H)
            usable_sa = stats_sa['usable_leftover_area']
            util_sa = stats_sa['utilization_rate']
        else:
            usable_sa = 0
            util_sa = 0.0

        sa_avg = sum(sa_costs) / n_runs
        sa_best = sa_best_cost
        improvement = (cost_ffd - sa_best) / cost_ffd * 100 if cost_ffd > 0 else 0

        # Разница полезных остатков (SA - FFD)
        diff_usable = usable_sa - usable_ffd
        rel_diff = (diff_usable / usable_ffd * 100) if usable_ffd > 0 else 0.0

        print(f"{name[:25]:<25} {n:<4} {W}x{H:<10} "
              f"{cost_ffd:<4} {usable_ffd:<6.0f} {util_ffd:<5.1f} "
              f"{sa_avg:<6.2f} {sa_best:<4} {usable_sa:<6.0f} {util_sa:<5.1f} "
              f"{improvement:<6.1f} {diff_usable:<+6.0f} ({rel_diff:<+5.1f}%)")

    print("=" * 150)

if __name__ == "__main__":
    run_comparison(max_parts=100, sa_fast_mode=True)