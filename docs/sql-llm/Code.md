---
sidebar_label: Code
---

# The Code

1. First, let's build a mock financial database. This creates `accounting.db` with 8 mock clients and 40-70 mock invoices with a realistic mix of paid, unpaid, and overdue statuses.

<details>

<summary>Show setup.py</summary>

```
"""
Step 1: Database setup
Creates a small SQLite accounting database with realistic mock data.
Run this once to generate accounting.db
"""

import sqlite3
from datetime import date, timedelta
import random

DB_PATH = "accounting.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS clients (
    client_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    industry TEXT
);

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    issue_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    status TEXT NOT NULL, -- 'paid', 'unpaid', 'overdue'
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY,
    invoice_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    payment_date TEXT NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
);
"""

CLIENT_NAMES = [
    ("Nordic Property Services Oy", "Real Estate"),
    ("Helsinki Web Solutions", "Tech"),
    ("Baltic Logistics Group", "Logistics"),
    ("Green Valley Catering", "Food Service"),
    ("Suomi Rakennus Oy", "Construction"),
    ("Arctic Design Studio", "Design"),
    ("Lahti Manufacturing", "Manufacturing"),
    ("Turku Retail Partners", "Retail"),
]


def build_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(SCHEMA)

    # Clear existing data for a clean rebuild
    cur.execute("DELETE FROM payments")
    cur.execute("DELETE FROM invoices")
    cur.execute("DELETE FROM clients")

    # Insert clients
    for i, (name, industry) in enumerate(CLIENT_NAMES, start=1):
        cur.execute(
            "INSERT INTO clients (client_id, name, industry) VALUES (?, ?, ?)",
            (i, name, industry),
        )

    # Insert invoices with realistic spread of paid / unpaid / overdue
    today = date.today()
    invoice_id = 1
    for client_id in range(1, len(CLIENT_NAMES) + 1):
        for _ in range(random.randint(4, 9)):
            issue_date = today - timedelta(days=random.randint(10, 180))
            due_date = issue_date + timedelta(days=30)
            amount = round(random.uniform(200, 8000), 2)

            if due_date >= today:
                status = "unpaid"
            else:
                # some overdue invoices, some paid late, some paid on time
                status = random.choice(["paid", "paid", "overdue", "overdue", "unpaid"])

            cur.execute(
                """INSERT INTO invoices
                   (invoice_id, client_id, amount, issue_date, due_date, status)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (invoice_id, client_id, amount, issue_date.isoformat(),
                 due_date.isoformat(), status),
            )

            if status == "paid":
                payment_date = due_date - timedelta(days=random.randint(-5, 10))
                cur.execute(
                    """INSERT INTO payments (invoice_id, amount, payment_date)
                       VALUES (?, ?, ?)""",
                    (invoice_id, amount, payment_date.isoformat()),
                )

            invoice_id += 1

    conn.commit()
    conn.close()
    print(f"Database built: {DB_PATH}")
    print(f"{len(CLIENT_NAMES)} clients, {invoice_id - 1} invoices generated.")


if __name__ == "__main__":
    build_database()

```
</details>

2. Then we run the app with streamlit. This calls engine.py with the core pipeline logic.

<details>

<summary>Show app.py</summary>

```
"""
Step 3: Interface
A minimal Streamlit app that shows all three layers of the pipeline:
  - the natural language question
  - the generated SQL (for transparency / validation)
  - the plain language answer

Run with: streamlit run app.py
"""

import streamlit as st
from engine import ask

st.set_page_config(page_title="NL to SQL Accounting Assistant", layout="centered")

st.title("Natural Language Accounting Query Tool")
st.caption(
    "Ask a question in plain English. The tool generates SQL, runs it, "
    "and explains the result back in plain language."
)

example_questions = [
    "Which clients have overdue invoices over 1000 euros?",
    "What is the total unpaid amount per client?",
    "Which client has paid the most invoices on time?",
    "How many invoices are overdue this month?",
]

with st.expander("Example questions"):
    for q in example_questions:
        st.write(f"- {q}")

question = st.text_input("Your question:")

if st.button("Ask") and question:
    with st.spinner("Generating SQL and querying database..."):
        result = ask(question)

    st.subheader("Answer")
    st.write(result["answer"])

    st.subheader("Generated SQL")
    st.code(result["sql"], language="sql")

    if "rows" in result:
        st.subheader("Raw results")
        st.dataframe(result["rows"])

    if "error" in result:
        st.error(f"Query error: {result['error']}")


```
</details>

3. App runs the engine

<details>

<summary>Show engine.py</summary>

```
"""
Step 2: Core engine
Two Claude calls:
  1. Natural language question -> SQL query (constrained to known schema)
  2. SQL query + results -> natural language answer

Requires: pip install anthropic --break-system-packages
Set your API key as an environment variable: ANTHROPIC_API_KEY
"""

import sqlite3
import json
import os
from anthropic import Anthropic

DB_PATH = "accounting.db"
MODEL = "claude-sonnet-4-6"  # adjust to whichever model string you have access to

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SCHEMA_DESCRIPTION = """
You have access to a SQLite accounting database with this schema:

clients(client_id INTEGER PRIMARY KEY, name TEXT, industry TEXT)
invoices(invoice_id INTEGER PRIMARY KEY, client_id INTEGER, amount REAL,
         issue_date TEXT, due_date TEXT, status TEXT)  -- status: 'paid','unpaid','overdue'
payments(payment_id INTEGER PRIMARY KEY, invoice_id INTEGER, amount REAL, payment_date TEXT)

Dates are stored as ISO strings (YYYY-MM-DD). Today's date will be provided if relevant.
"""


def generate_sql(question: str, today: str) -> str:
    """Step A: Translate a natural language question into a SQL query."""
    prompt = f"""{SCHEMA_DESCRIPTION}

Today's date is {today}.

Write a single SQLite query that answers this question:
"{question}"

Rules:
- Output ONLY the raw SQL query, no explanation, no markdown formatting, no backticks.
- Use standard SQLite syntax.
- Prefer explicit column names over SELECT *.
"""
    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    sql = response.content[0].text.strip()
    # Strip accidental markdown fences if the model adds them anyway
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql


def run_query(sql: str):
    """Step B: Execute the generated SQL against the local database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def summarize_results(question: str, sql: str, rows: list) -> str:
    """Step C: Translate raw SQL results back into a plain-language answer."""
    prompt = f"""A user asked: "{question}"

This SQL query was run:
{sql}

It returned these results (JSON):
{json.dumps(rows, indent=2, default=str)}

Write a short, clear, plain-language answer to the user's question based on
these results. Use concrete numbers. If the result set is empty, say so
plainly. Do not mention SQL or databases in your answer — write as if
speaking to a non-technical accountant.
"""
    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def ask(question: str, today: str = None):
    """Full pipeline: question -> SQL -> results -> plain language answer."""
    from datetime import date
    today = today or date.today().isoformat()

    sql = generate_sql(question, today)

    try:
        rows = run_query(sql)
    except Exception as e:
        return {
            "question": question,
            "sql": sql,
            "error": str(e),
            "answer": f"The generated query failed to run: {e}",
        }

    answer = summarize_results(question, sql, rows)

    return {
        "question": question,
        "sql": sql,
        "rows": rows,
        "answer": answer,
    }


if __name__ == "__main__":
    # Quick manual test
    result = ask("Which clients have overdue invoices over 1000 euros?")
    print("SQL generated:\n", result["sql"])
    print("\nAnswer:\n", result["answer"])

```
</details>