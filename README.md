# College Assistant

A small LangChain tool-calling agent that answers college questions. You ask
something in plain English and it figures out which tool to run.

## What it does

- Attendance check (percentage + exam eligibility)
- Result calculator (average, grade, pass/fail)
- Fee balance (pending amount)
- Library fine (Rs.5 per late day)
- Hostel fee (monthly fee times months)
- Student lookup by ID (bonus)

The agent can chain several of these in one query, so "I attended 80/100, my
marks are 90 85 88 92 95, fee is 60000 paid 45000" returns all three answers
at once.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Add your Groq key to a `.env` file (copy `.env.example`):

```
GROQ_API_KEY=gsk_your_key_here
```

Groq is the default because it's free and needs no local model. There are
commented lines in `college_assistant.py` if you'd rather use Ollama or OpenAI.

## Run

```bash
python3 college_assistant.py
```

That runs all the test cases with `verbose=True` so you can see each tool call.
