# main.py
import csv
from datetime import datetime
from common.data import load_test_sets, load_generated_sets, load_sa_generated_sets
from common.analysis import analyze_leftovers
from common.packing import pack_sequence
from FFD import ffd
from SA import simulated_annealing

def save_table_markdown(rows, headers, filename="results.md"):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("|" + "|".join(["---"] * len(headers)) + "|\n")
        for row in rows:
            f.write("| " + " | ".join(str(cell) for cell in row) + " |\n")
    print(f"Таблица сохранена в {filename}")

def save_table_csv(rows, headers, filename="results.csv"):
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Таблица сохранена в {filename}")

def run_comparison(max_parts=100, sa_fast_mode=True):
    manual_sets = load_test_sets()
    generated_sets = load_generated_sets()
    generated_sets2 = load_sa_generated_sets()
    all_sets =  generated_sets2 # + manual_sets + generated_sets

    filtered_sets = [s for s in all_sets if len(s["детали"]) <= max_parts]
    skipped = len(all_sets) - len(filtered_sets)

    headers = [
        "Набор", "Дет", "WxH",
        "FFD л", "FFD ост", "FFD %",
        "SA ср", "SA л", "SA ост", "SA %",
        "Улучш%", "Δ лист", "Выгода SA по ост %"
    ]

    print("\n" + "=" * 160)
    print(f"Загружено наборов: всего {len(all_sets)}, обрабатывается {len(filtered_sets)} (пропущено {skipped} из-за лимита {max_parts} деталей)")
    print("=" * 160)
    print(f"{headers[0]:<25} {headers[1]:<4} {headers[2]:<10} "
          f"{headers[3]:<4} {headers[4]:<6} {headers[5]:<5} "
          f"{headers[6]:<6} {headers[7]:<4} {headers[8]:<6} {headers[9]:<5} "
          f"{headers[10]:<6} {headers[11]:<6} {headers[12]:<12}")
    print("=" * 160)

    table_rows = []
    advantage_values = []  # для сбора значений последнего столбца

    for ts in filtered_sets:
        name = ts["название"]
        items = ts["детали"]
        W = ts["лист_ширина"]
        H = ts["лист_высота"]
        n = len(items)
        sheet_area = W * H

        # ----- FFD -----
        sheets_ffd = ffd(items, W, H, allow_rotation=True)
        cost_ffd = len(sheets_ffd)
        stats_ffd = analyze_leftovers(sheets_ffd, items, W, H)
        usable_ffd = stats_ffd['usable_leftover_area']
        util_ffd = stats_ffd['utilization_rate']

        # ----- SA с адаптивными параметрами -----
        n_runs = 9
        
        if n > 30:
            sa_params = {
                'initial_temp': 150.0,
                'cooling_rate': 0.97,
                'min_temp': 2.0,
                'iterations_per_temp': 250,
                'max_no_improve': 80,
            }
        elif n >= 20:
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
                **sa_params, verbose=False
            )
            sa_costs.append(cost)
            if cost < sa_best_cost:
                sa_best_cost = cost
                sa_best_seq = seq
                sa_best_rot = rot

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

        # Разница в листах (положительно, если SA меньше листов)
        delta_sheets = cost_ffd - sa_best

        # Приводим к одинаковому числу листов (максимальному)
        max_sheets = max(cost_ffd, sa_best)
        usable_ffd_adj = usable_ffd + (max_sheets - cost_ffd) * sheet_area
        usable_sa_adj = usable_sa + (max_sheets - sa_best) * sheet_area

        # Выгода SA: положительна, если у SA больше полезных остатков (лучше)
        if usable_ffd_adj != 0:
            advantage_percent = ((usable_sa_adj - usable_ffd_adj) / usable_ffd_adj) * 100
        else:
            advantage_percent = 0.0

        # Добавляем значение в список для среднего
        advantage_values.append(advantage_percent)

        # Вывод в терминал
        print(f"{name[:25]:<25} {n:<4} {W}x{H:<10} "
              f"{cost_ffd:<4} {usable_ffd:<6.0f} {util_ffd:<5.1f} "
              f"{sa_avg:<6.2f} {sa_best:<4} {usable_sa:<6.0f} {util_sa:<5.1f} "
              f"{improvement:<6.1f} {delta_sheets:6.0f} {advantage_percent:12.2f}")

        # Подготовка строки для сохранения
        table_rows.append([
            name[:30],
            n,
            f"{W}x{H}",
            cost_ffd,
            f"{usable_ffd:.0f}",
            f"{util_ffd:.1f}",
            f"{sa_avg:.2f}",
            sa_best,
            f"{usable_sa:.0f}",
            f"{util_sa:.1f}",
            f"{improvement:.1f}",
            f"{delta_sheets:d}",
            f"{advantage_percent:.2f}%"
        ])

    print("=" * 160)

    # Расчёт среднего по последнему столбцу
    if advantage_values:
        avg_advantage = sum(advantage_values) / len(advantage_values)
        print(f"\nСредняя выгода по полезным остаткам (по {len(advantage_values)} наборам): {avg_advantage:.2f}%")
    else:
        print("\nНет данных для расчёта средней выгоды по остаткам.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_table_csv(table_rows, headers, f"results_{timestamp}.csv")
    save_table_markdown(table_rows, headers, f"results_{timestamp}.md")

if __name__ == "__main__":
    run_comparison(max_parts=100, sa_fast_mode=True)