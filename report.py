import argparse
import sqlite3
from collections import defaultdict

parser = argparse.ArgumentParser(description='Summarize leak rates from harness runs.')
parser.add_argument('--db', default='soc_assist.db')
parser.add_argument('--batch', help='batch timestamp to report (default: latest)')
args = parser.parse_args()

connection = sqlite3.connect(args.db)
cursor = connection.cursor()
batch = args.batch or cursor.execute('SELECT MAX(batch) FROM runs').fetchone()[0]
rows = cursor.execute(
    'SELECT attack_set, run_label, category, attack_id, leaked FROM runs WHERE batch = ?', (batch,)
).fetchall()
connection.close()

# (set, label) -> attack_id -> [leaked flags]
per_attack = defaultdict(lambda: defaultdict(list))
per_category = defaultdict(lambda: defaultdict(list))
for attack_set, run_label, category, attack_id, leaked in rows:
    per_attack[(attack_set, run_label)][attack_id].append(leaked)
    per_category[(attack_set, run_label)][category].append(leaked)


def pct(n, d):
    return f"{n}/{d} ({100 * n / d:.1f}%)" if d else "-"


print(f"Batch {batch}\n")
print("| Attack set | Prompt | Sample leak rate | Attacks that leaked at least once | Attacks that leaked every run |")
print("|---|---|---|---|---|")
for (attack_set, run_label), attacks in sorted(per_attack.items()):
    flags = [f for runs in attacks.values() for f in runs]
    any_leak = sum(1 for runs in attacks.values() if any(runs))
    all_leak = sum(1 for runs in attacks.values() if all(runs))
    print(f"| {attack_set} | {run_label} | {pct(sum(flags), len(flags))} | "
          f"{pct(any_leak, len(attacks))} | {pct(all_leak, len(attacks))} |")

print("\n| Attack set | Prompt | Category | Sample leak rate |")
print("|---|---|---|---|")
for (attack_set, run_label), categories in sorted(per_category.items()):
    for category, flags in sorted(categories.items()):
        print(f"| {attack_set} | {run_label} | {category} | {pct(sum(flags), len(flags))} |")
