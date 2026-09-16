import csv
import sqlite3
from datetime import datetime
from assistant import is_secret_leaked, reply_text
from system_prompt import SYSTEM_PROMPT_BASELINE, SYSTEM_PROMPT_HARDENED


connection = sqlite3.connect('soc_assist.db')
cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS theComparisons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attack_id INTEGER,
    category TEXT,
    prompt TEXT,
    response TEXT,
    run_label TEXT,
    passed TEXT,
    timestamp TEXT
)
''')

RUN_LABEL = "hardened"
ACTIVE_PROMPT = SYSTEM_PROMPT_BASELINE if RUN_LABEL == "baseline" else SYSTEM_PROMPT_HARDENED
...
with open('attacks.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        attack_id = int(row['id'])
        category = row['category']
        prompt = row['prompt']

        raw_response = reply_text(prompt, ACTIVE_PROMPT)
        
        response_text = raw_response

        leaked = is_secret_leaked(response_text)
        passed = 'NO' if leaked else 'YES'

        timestamp = datetime.now().isoformat()

        cursor.execute('''
            INSERT INTO theComparisons (attack_id, category, prompt, response, run_label, passed, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (attack_id, category, prompt, response_text, RUN_LABEL, passed, timestamp))
        
        connection.commit()
        
        print(f"Attack ID: {attack_id}, Category: {category}, Passed: {passed}")

connection.close()
