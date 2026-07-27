# Natural Language Database Query Tool

A small portfolio project demonstrating a two-way LLM pipeline: natural language → SQL → results → natural language.

This is a quick demonstration of not just prompting Claude, but showcasing how to validate Claude output against a deterministic schema. This way we can work with databases where accuracy and trust are paramount.

For production and future development, this query tool can be extended to local LLM models or gated online LLM models.

## What it does

1. You ask a question in plain English (e.g. "which clients have overdue invoices over 1000 euros?")
2. Claude translates the question into a SQL query against a mock accounting database
3. The query runs against a local SQLite database
4. Claude translates the raw SQL results back into a plain-language answer
5. The UI shows all three layers: question, SQL, and answer. 
6. The result can be verified, not just trusted blindly.
## Project structure

- `setup_database.py` — creates and seeds the SQLite database (Step 1)
- `engine.py` — the core NL→SQL→NL pipeline logic (Step 2)
- `app.py` — Streamlit interface (Step 3)

## Notes:

- The tool deliberately shows the generated SQL alongside the answer. So we purposefully let a human verify the query is actually correct before trusting the answer.
- We constrain the SQL generation to a known schema so it doesn't hallucinate tables or columns that don't exist
- We split the request into two separate calls with different jobs (generation vs. summarization) rather than one messy prompt trying to do both
- We test a handful of edge-case questions (ambiguous wording, questions
  with no matching data, multi-table joins) and document any cases where
  the generated SQL was wrong.
- For a real deployment handling actual client financial data, a
  local or EU-hosted model would likely be the more compliance-appropriate
  choice given data residency expectations in Finnish/EU accounting
  contexts. This version uses Claude for reliability during prototyping.