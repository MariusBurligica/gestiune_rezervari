import time
import statistics
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from App.db import run_select, run_execute

RUNS = 50
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
REPORT_FILE = OUTPUT_DIR / "performance_report.txt"
CHART_FILE = OUTPUT_DIR / "performance_chart.png"


TEST_QUERIES = [
    {
        "name": "Users by username",
        "sql": "SELECT * FROM users WHERE username = %s;",
        "params": ("admin",),
    },
    {
        "name": "Meniuri by nume",
        "sql": "SELECT * FROM meniuri WHERE nume_meniu = %s;",
        "params": ("Meniu Traditional Romanesc",),
    },
    {
        "name": "Rezervari by status",
        "sql": "SELECT * FROM rezervari WHERE status = %s;",
        "params": ("Confirmata",),
    }
]


INDEX_SQL = [
    "CREATE INDEX idx_users_username ON users(username);",
    "CREATE INDEX idx_meniuri_nume ON meniuri(nume_meniu);",
    "CREATE INDEX idx_rezervari_status ON rezervari(status);"
]


def benchmark_query(sql: str, params, runs: int):
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        run_select(sql, params)
        end = time.perf_counter()
        times.append((end - start) * 1000)
    return times


def summarize(times):
    avg = statistics.mean(times)
    mn = min(times)
    mx = max(times)
    std = statistics.stdev(times) if len(times) > 1 else 0.0
    return avg, mn, mx, std


def run_suite(label: str):
    results = {}
    for q in TEST_QUERIES:
        times = benchmark_query(q["sql"], q["params"], RUNS)
        avg, mn, mx, std = summarize(times)
        results[q["name"]] = {"avg": avg, "min": mn, "max": mx, "std": std}
        print(f"[{label}] {q['name']} -> avg {avg:.2f} ms")
    return results


def apply_indexes():
    for stmt in INDEX_SQL:
        try:
            run_execute(stmt)
        except Exception as e:

            print(f"Nota: {e}")


def pct_change(before, after):
    if before <= 0:
        return 0.0
    return ((before - after) / before) * 100.0


def generate_chart(before_results, after_results):
    """Generează un bar chart comparativ."""
    labels = list(before_results.keys())
    before_means = [before_results[name]["avg"] for name in labels]
    after_means = [after_results[name]["avg"] for name in labels]

    x = np.arange(len(labels))  # Locația etichetelor
    width = 0.35  # Lățimea barelor

    fig, ax = plt.subplots(figsize=(10, 6))

    rects1 = ax.bar(x - width / 2, before_means, width, label='Înainte de Index', color='#e74c3c')
    rects2 = ax.bar(x + width / 2, after_means, width, label='După Index', color='#2ecc71')

    # Adăugare texte și stilizare
    ax.set_ylabel('Timp mediu (ms)')
    ax.set_title('Impactul Indexării asupra Performanței Query-urilor')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Adăugăm etichete deasupra barelor pentru claritate
    ax.bar_label(rects1, padding=3, fmt='%.2f')
    ax.bar_label(rects2, padding=3, fmt='%.2f')

    fig.tight_layout()

    plt.savefig(CHART_FILE)
    print(f"Grafic salvat în: {CHART_FILE}")
    plt.show()


def main():
    lines = []
    lines.append("=== ANALIZA PERFORMANTA SQL (BEFORE vs AFTER) ===\n")
    lines.append(f"Rulari per query: {RUNS}\n")

    # --- BEFORE ---
    print("Rulăm testele inițiale...")
    before = run_suite("BEFORE")

    # --- APPLY INDEXES ---
    print("\nAplicăm indexurile...")
    apply_indexes()

    # --- AFTER ---
    print("\nRulăm testele după optimizare...")
    after = run_suite("AFTER")

    # Construire raport text
    for name, m in before.items():
        lines.append(f"Query: {name} (BEFORE) -> AVG: {m['avg']:.2f} ms")

    lines.append("-" * 30)

    for name, m in after.items():
        improvement = pct_change(before[name]["avg"], m["avg"])
        lines.append(f"Query: {name} (AFTER) -> AVG: {m['avg']:.2f} ms | Improvement: {improvement:.1f}%")

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nRaport text salvat în: {REPORT_FILE}")

    # --- GENERARE GRAFIC ---
    generate_chart(before, after)


if __name__ == "__main__":
    main()