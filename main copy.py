# main.py
import csv
from datetime import datetime
from common.data import load_test_sets, load_generated_sets, load_sa_generated_sets, load_sa_generated_directional_sets
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
    directional_sets = load_sa_generated_directional_sets()
    all_sets = directional_sets + generated_sets2 # или generated_sets2 + manual_sets + generated_sets

    filtered_sets = [s for s in all_sets if len(s["детали"]) <= max_parts]
    skipped = len(all_sets) - len(filtered_sets)

    headers = [
        "Набор", "Дет", "WxH",
        "FFD л", "FFD ост (пл)", "FFD ост (шт)", "FFD %",
        "SA ср", "SA л", "SA ост (пл)", "SA ост (шт)", "SA %",
        "Улучш%", "Δ лист", "Тип", "Выгода ост% (при равных листах)"
    ]

    print("\n" + "=" * 200)
    print(f"Загружено наборов: всего {len(all_sets)}, обрабатывается {len(filtered_sets)} (пропущено {skipped} из-за лимита {max_parts} деталей)")
    print("=" * 200)
    print(f"{headers[0]:<25} {headers[1]:<4} {headers[2]:<10} "
          f"{headers[3]:<4} {headers[4]:<8} {headers[5]:<8} {headers[6]:<5} "
          f"{headers[7]:<6} {headers[8]:<4} {headers[9]:<8} {headers[10]:<8} {headers[11]:<5} "
          f"{headers[12]:<6} {headers[13]:<6} {headers[14]:<18} {headers[15]:<20}")
    print("=" * 200)

    table_rows = []

    for ts in filtered_sets:
        name = ts["название"]
        items = ts["детали"]
        W = ts["лист_ширина"]
        H = ts["лист_высота"]
        n = len(items)
        sheet_area = W * H

        # ----- FFD -----
        sheets_ffd = ffd(items, W, H, allow_rotation=False)  # FALSE ROTATION
        cost_ffd = len(sheets_ffd)
        stats_ffd = analyze_leftovers(sheets_ffd, items, W, H)
        usable_ffd = stats_ffd['usable_leftover_area']
        count_ffd = stats_ffd['num_usable_regions']  # правильный ключ
        util_ffd = stats_ffd['utilization_rate']

        # ----- SA с адаптивными параметрами -----
        n_runs = 5

        if sa_fast_mode:
            # Быстрые параметры
            if n > 30:
                sa_params = {
                    'initial_temp': 150.0,
                    'cooling_rate': 0.98,
                    'min_temp': 2.0,
                    'iterations_per_temp': 150,
                    'max_no_improve': 40,
                }
            elif n >= 20:
                sa_params = {
                    'initial_temp': 100.0,
                    'cooling_rate': 0.96,
                    'min_temp': 1.0,
                    'iterations_per_temp': 100,
                    'max_no_improve': 50,
                }
            else:
                sa_params = {
                    'initial_temp': 80.0,
                    'cooling_rate': 0.94,
                    'min_temp': 5.0,
                    'iterations_per_temp': 50,
                    'max_no_improve': 20,
                }
        else:
            # Оригинальные (более точные) параметры
            if n > 30:
                sa_params = {
                    'initial_temp': 200.0,
                    'cooling_rate': 0.97,
                    'min_temp': 2.0,
                    'iterations_per_temp': 250,
                    'max_no_improve': 80,
                }
            elif n >= 20:
                sa_params = {
                    'initial_temp': 150.0,
                    'cooling_rate': 0.95,
                    'min_temp': 1.0,
                    'iterations_per_temp': 200,
                    'max_no_improve': 100,
                }
            else:
                sa_params = {
                    'initial_temp': 100.0,
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
                items=items, W=W, H=H, allow_rotation=False,
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
            count_sa = stats_sa['num_usable_regions']
            util_sa = stats_sa['utilization_rate']
        else:
            usable_sa = 0
            count_sa = 0
            util_sa = 0.0

        sa_avg = sum(sa_costs) / n_runs
        sa_best = sa_best_cost
        improvement = (cost_ffd - sa_best) / cost_ffd * 100 if cost_ffd > 0 else 0
        delta_sheets = cost_ffd - sa_best

        # Определяем тип улучшения
        if delta_sheets > 0:
            improvement_type = "Экономия листов"
            advantage_at_equal = "-"
        elif delta_sheets == 0:
            if usable_sa > usable_ffd:
                improvement_type = "Улучшение заполнения"
            elif usable_sa < usable_ffd:
                improvement_type = "Ухудшение заполнения"
            else:
                improvement_type = "Без изменений"
            if usable_ffd != 0:
                advantage_at_equal = f"{(usable_sa - usable_ffd) / usable_ffd * 100:.2f}%"
            else:
                advantage_at_equal = "0.0%"
        else:  # delta_sheets < 0 (SA хуже по листам)
            improvement_type = "Хуже (больше листов)"
            advantage_at_equal = "-"

        # Вывод в терминал
        print(f"{name[:25]:<25} {n:<4} {W}x{H:<10} "
              f"{cost_ffd:<4} {usable_ffd:<8.0f} {count_ffd:<8} {util_ffd:<5.1f} "
              f"{sa_avg:<6.2f} {sa_best:<4} {usable_sa:<8.0f} {count_sa:<8} {util_sa:<5.1f} "
              f"{improvement:<6.1f} {delta_sheets:6.0f} {improvement_type:<18} {advantage_at_equal:<20}")

        # Подготовка строки для сохранения
        table_rows.append([
            name[:30],
            n,
            f"{W}x{H}",
            cost_ffd,
            f"{usable_ffd:.0f}",
            count_ffd,
            f"{util_ffd:.1f}",
            f"{sa_avg:.2f}",
            sa_best,
            f"{usable_sa:.0f}",
            count_sa,
            f"{util_sa:.1f}",
            f"{improvement:.1f}",
            f"{delta_sheets:d}",
            improvement_type,
            advantage_at_equal
        ])

    print("=" * 200)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_table_csv(table_rows, headers, f"results_{timestamp}.csv")
    save_table_markdown(table_rows, headers, f"results_{timestamp}.md")

if __name__ == "__main__":
    run_comparison(max_parts=200, sa_fast_mode=True)