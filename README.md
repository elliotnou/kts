# Workflow Architect

**A multi-agent AI planner that designs optimal workflows through structured deliberation.**

Built as a response to Challenge 2 of the KTS AI Operations Specialist application — instead of just describing a transcript-to-proposal workflow, I built an AI system that *designs* the optimal workflow through multi-agent reasoning.

## What It Does

Four specialized AI agents deliberate to answer the question: *"How do you turn 3 call transcripts into a tailored transit consulting proposal in under 60 minutes?"*

| Agent | Role |
|-------|------|
| **Researcher** | Investigates what makes transit proposals win — structure, tone, failure modes |
| **Architect** | Designs the step-by-step workflow given the 60-minute constraint |
| **Critical Eye** | Reviews every automated step — where does a wrong AI call cascade into a disaster? |
| **Toolsmith** | Maps real tools (Claude, Granola, Zapier, Google Docs) to each step |

### The Deliberation Loop

```
Researcher → Architect v1 → Critical Eye → Toolsmith → Architect v2 (revised) → Critical Eye final pass
```

The agents don't just run independently — each one receives the outputs of previous agents and responds to them. The Architect's plan changed significantly after the Critical Eye challenged it and the Toolsmith flagged fragile integrations.

## The Output

The system produced a **55-minute, 8-step workflow** with 3 critical human judgment checkpoints. The most interesting finding: the Critical Eye agent kept stripping automation *out*. It argued that in transit consulting, misreading political subtext or overpromising scope doesn't just lose a deal — it damages the relationship permanently.

The full deliberation outputs are in [`output/`](output/).

## Quick Start

```bash
# Clone and set up
git clone https://github.com/YOUR_USERNAME/workflow-architect.git
cd workflow-architect
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Set your Anthropic API key
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# Run the multi-agent deliberation (CLI)
python orchestrator.py

# Or launch the Streamlit UI
streamlit run app.py
```

## Project Structure

```
workflow_architect/
├── orchestrator.py      # Multi-agent system — agent prompts, runner, deliberation loop
├── app.py               # Streamlit UI — visualizes agent reasoning in real-time
├── generate_pdf.py      # Generates the one-page PDF submission
├── requirements.txt
├── .env                 # Your API key (gitignored)
└── output/              # Agent outputs from the latest run
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
- **GitHub Copilot** — assisted in building the prototype
- **fpdf2** — PDF generation for the one-page submission
