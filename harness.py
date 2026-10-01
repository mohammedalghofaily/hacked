import argparse
import csv
import sqlite3
from datetime import datetime
from assistant import MODEL, is_secret_leaked, reply_text
from system_prompt import SYSTEM_PROMPT_BASELINE, SYSTEM_PROMPT_HARDENED

PROMPTS = {'baseline': SYSTEM_PROMPT_BASELINE, 'hardened': SYSTEM_PROMPT_HARDENED}
ATTACK_SETS = {'tuned': 'attacks.csv', 'heldout': 'heldout_attacks.csv'}

parser = argparse.ArgumentParser(description='Run an attack set against SOC-Assist.')
parser.add_argument('--prompt', choices=['baseline', 'hardened', 'both'], default='both')
parser.add_argument('--attacks', choices=['tuned', 'heldout', 'both'], default='both')
parser.add_argument('--runs', type=int, default=5, help='samples per attack')
parser.add_argument('--temperature', type=float, default=0.7,
                    help='sampling temperature; repeated runs at 0 are identical')
parser.add_argument('--db', default='soc_assist.db')
args = parser.parse_args()

connection = sqlite3.connect(args.db)
cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch TEXT,
    model TEXT,
    attack_set TEXT,
    attack_id INTEGER,
    category TEXT,
    prompt TEXT,
    response TEXT,
    run_label TEXT,
    run_index INTEGER,
    temperature REAL,
    seed INTEGER,
    leaked INTEGER,
    timestamp TEXT
)
''')

batch = datetime.now().isoformat(timespec='seconds')
prompt_labels = list(PROMPTS) if args.prompt == 'both' else [args.prompt]
attack_sets = list(ATTACK_SETS) if args.attacks == 'both' else [args.attacks]

for attack_set in attack_sets:
    with open(ATTACK_SETS[attack_set], newline='', encoding='utf-8') as csvfile:
        attacks = list(csv.DictReader(csvfile))
    for run_label in prompt_labels:
        for row in attacks:
            leaks = 0
            for run_index in range(args.runs):
                seed = run_index
                response_text = reply_text(row['prompt'], PROMPTS[run_label], args.temperature, seed)
                leaked = is_secret_leaked(response_text)
                leaks += leaked
                cursor.execute('''
                    INSERT INTO runs (batch, model, attack_set, attack_id, category, prompt, response,
                                      run_label, run_index, temperature, seed, leaked, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (batch, MODEL, attack_set, int(row['id']), row['category'], row['prompt'], response_text,
                      run_label, run_index, args.temperature, seed, int(leaked), datetime.now().isoformat()))
                connection.commit()
            print(f"[{attack_set}/{run_label}] Attack {row['id']} ({row['category']}): leaked {leaks}/{args.runs}")

connection.close()
print(f"Done. Batch: {batch}. Summarize with: python report.py --batch {batch}")
