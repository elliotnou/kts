# Workflow Architect

**A multi-agent AI system that reads call transcripts and designs a custom proposal-creation workflow.**

Built for Challenge 2 of the KTS AI Operations Specialist application. Instead of manually designing a transcript-to-proposal workflow, I built an AI system that ingests real call transcripts and plans the workflow for you. Different transcripts produce different plans.

## What It Does

Four AI agents read your call transcripts and collaboratively design a step-by-step plan for turning those conversations into a winning proposal. The plan includes what to automate, where human judgment is needed, and which tools to use at each step.

| Agent | Role |
|-------|------|
| **Researcher** | Reads transcripts, identifies what this client cares about, combines with proposal best practices |
| **Architect** | Designs a step-by-step workflow tailored to the topics and sensitivities in these calls |
| **Critical Eye** | Reviews the plan — where would a wrong AI call cause a disaster with THIS client? |
| **Toolsmith** | Maps practical tools to each step — Claude API, Granola, Google Docs, Zapier, etc. |

### The Deliberation Loop

```
Researcher -> Architect v1 -> Critical Eye -> Toolsmith -> Architect v2 (revised) -> Critical Eye final pass
```

Each agent receives all prior outputs. The Architect's plan changes significantly after feedback.

## Using Your Own Transcripts

To generate a workflow plan for your own client:

1. **Add your transcript files** to the `transcripts/` folder (any `.txt` files)
2. **Delete or move** the example files (prefixed with `example_`)
3. **Run the system** — it will read your transcripts and generate a tailored plan

The included `example_*.txt` files are mock transcripts for a fictional transit agency (Lakeview Regional Transit Authority) used for testing.

## Quick Start

```bash
# Clone and set up
git clone https://github.com/elliotnou/kts.git
cd kts
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Set your Anthropic API key
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# Run the multi-agent deliberation (CLI)
python orchestrator.py

# Generate the workflow PDF (reads from output/)
python generate_pdf.py

# Or launch the Streamlit UI
streamlit run app.py
```

## Project Structure

```
workflow_architect/
├── orchestrator.py        # Multi-agent system: prompts, runner, deliberation loop
├── app.py                 # Streamlit UI: watch agents deliberate in real-time
├── generate_pdf.py        # Reads agent outputs, uses Claude to extract steps, renders flowchart PDF
├── requirements.txt
├── .env                   # Your API key (gitignored)
├── transcripts/           # Put your call transcripts here (.txt files)
│   ├── example_call_1_intro.txt
│   ├── example_call_2_technical.txt
│   └── example_call_3_scope.txt
└── output/                # Agent outputs from the latest run
    ├── 1_researcher.md
    ├── 2_architect.md
    ├── 3_critical_eye.md
    ├── 4_toolsmith.md
    ├── 5_architect_revised.md
    ├── 6_critical_eye_final.md
    └── full_deliberation.md
```

## Tools Used

- **Claude API** (Anthropic) — powers all four agents via `claude-sonnet-4-20250514`
- **Python** — orchestration and PDF generation
- **Streamlit** — interactive UI for watching agents deliberate
- **fpdf2** — PDF generation with color-coded flowchart
- **GitHub Copilot** — assisted in building the prototype
