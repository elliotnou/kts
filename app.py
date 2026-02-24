"""
Workflow Architect - Streamlit UI
==================================
Visual interface showing the multi-agent deliberation in real-time.
Each agent's reasoning streams through its own panel.
Includes Mermaid flowcharts for the deliberation loop and designed workflow.
"""

import streamlit as st
import time
import os
from orchestrator import run_deliberation, save_results, CHALLENGE

st.set_page_config(
    page_title="Workflow Architect",
    page_icon="🏗️",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    
    .agent-card {
        background: #1a1d23;
        border: 1px solid #2d3139;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    
    .agent-header {
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid;
    }
    
    .researcher { color: #60a5fa; border-color: #60a5fa; }
    .architect { color: #34d399; border-color: #34d399; }
    .critical-eye { color: #f87171; border-color: #f87171; }
    .toolsmith { color: #fbbf24; border-color: #fbbf24; }
    .architect-revised { color: #a78bfa; border-color: #a78bfa; }
    .critical-final { color: #fb923c; border-color: #fb923c; }
    
    .agent-status {
        font-size: 12px;
        color: #6b7280;
        margin-bottom: 8px;
    }
    
    .challenge-box {
        background: #1e293b;
        border-left: 4px solid #60a5fa;
        padding: 16px 20px;
        border-radius: 0 8px 8px 0;
        margin: 16px 0;
        font-style: italic;
        color: #94a3b8;
    }
    
    div[data-testid="stExpander"] {
        background: #1a1d23;
        border: 1px solid #2d3139;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("# 🏗️ Workflow Architect")
st.markdown("##### A multi-agent AI planner that designs optimal workflows through structured deliberation")

st.markdown(f"""
<div class="challenge-box">
    <strong>The Challenge:</strong> {CHALLENGE.strip()}
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Agent Deliberation Flow (Mermaid)
# ---------------------------------------------------------------------------
st.markdown("#### Agent Deliberation Flow")
st.markdown("""
```mermaid
graph LR
    R["🔍 Researcher"]:::blue --> A1["🏗️ Architect v1"]:::green
    A1 --> CE["👁️ Critical Eye"]:::orange
    CE --> T["🔧 Toolsmith"]:::purple
    T --> A2["🏗️ Architect v2"]:::green
    A2 --> CF["👁️ Final Review"]:::orange

    classDef blue fill:#1e3a5f,stroke:#60a5fa,color:#60a5fa
    classDef green fill:#0f3d2e,stroke:#34d399,color:#34d399
    classDef orange fill:#3d2008,stroke:#f97316,color:#f97316
    classDef purple fill:#2d1b69,stroke:#a78bfa,color:#a78bfa
```
""")

st.divider()

# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------
if "results" not in st.session_state:
    st.session_state.results = None
if "running" not in st.session_state:
    st.session_state.running = False
if "agent_outputs" not in st.session_state:
    st.session_state.agent_outputs = {}

# Agent metadata
AGENTS = [
    ("Researcher", "researcher", "Investigates what makes transit proposals win"),
    ("Architect", "architect", "Designs the step-by-step workflow (v1)"),
    ("Critical Eye", "critical-eye", "Identifies essential human judgment points"),
    ("Toolsmith", "toolsmith", "Maps real tools to each workflow step"),
    ("Architect (Revised)", "architect-revised", "Revises workflow with all feedback"),
    ("Critical Eye (Final)", "critical-final", "Final validation of human checkpoints"),
]

# ---------------------------------------------------------------------------
# Run button
# ---------------------------------------------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("▶  Run Multi-Agent Deliberation", use_container_width=True, type="primary", disabled=st.session_state.running):
        st.session_state.running = True
        st.session_state.agent_outputs = {}
        st.session_state.results = None
        st.rerun()

# ---------------------------------------------------------------------------
# Display previously loaded results (from output/ directory)
# ---------------------------------------------------------------------------
def load_existing_results():
    """Load pre-generated results from output/ directory."""
    output_dir = "output"
    if not os.path.exists(output_dir):
        return None
    
    agent_files = [
        ("Researcher", "1_researcher.md"),
        ("Architect", "2_architect.md"),
        ("Critical Eye", "3_critical_eye.md"),
        ("Toolsmith", "4_toolsmith.md"),
        ("Architect (Revised)", "5_architect_revised.md"),
        ("Critical Eye (Final)", "6_critical_eye_final.md"),
    ]
    
    outputs = {}
    for name, filename in agent_files:
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                content = f.read()
                # Remove the markdown header line
                lines = content.split("\n")
                if lines and lines[0].startswith("# "):
                    content = "\n".join(lines[2:])  # skip header + blank line
                outputs[name] = content
    
    return outputs if outputs else None


# ---------------------------------------------------------------------------
# Run or display
# ---------------------------------------------------------------------------
if st.session_state.running:
    # Create placeholders for each agent
    placeholders = {}
    status_placeholders = {}
    
    for agent_name, css_class, description in AGENTS:
        st.markdown(f'<div class="agent-header {css_class}">{agent_name}</div>', unsafe_allow_html=True)
        st.caption(description)
        status_placeholders[agent_name] = st.empty()
        placeholders[agent_name] = st.empty()
        st.divider()
    
    # Set all to waiting
    for agent_name, _, _ in AGENTS:
        status_placeholders[agent_name].markdown("⏳ *Waiting...*")
    
    # Stream callback
    current_agent = {"name": None}
    current_text = {"buffer": ""}
    
    def on_stream(agent_name, text_chunk):
        if agent_name != current_agent["name"]:
            # New agent starting
            if current_agent["name"]:
                # Mark previous as done
                status_placeholders[current_agent["name"]].markdown("✅ *Complete*")
            current_agent["name"] = agent_name
            current_text["buffer"] = ""
            status_placeholders[agent_name].markdown("🔄 *Thinking...*")
        
        current_text["buffer"] += text_chunk
        placeholders[agent_name].markdown(current_text["buffer"])
    
    # Run deliberation
    try:
        results = run_deliberation(on_stream=on_stream)
        
        # Mark final agent done
        if current_agent["name"]:
            status_placeholders[current_agent["name"]].markdown("✅ *Complete*")
        
        # Save results
        save_results(results)
        st.session_state.results = {r.agent_name: r.output for r in results}
        st.session_state.running = False
        
        st.success("Deliberation complete! Results saved to output/ directory.")
        st.balloons()
        
    except Exception as e:
        st.error(f"Error during deliberation: {str(e)}")
        st.session_state.running = False

else:
    # Show existing results if available
    existing = st.session_state.results or load_existing_results()
    
    if existing:
        # ── Designed Workflow Flowchart ──
        st.markdown("### 🗺️ The Designed Workflow")
        st.caption("Color-coded: 🔵 Automated  |  🟠 Human Judgment  |  🟢 Hybrid")
        
        st.markdown("""
```mermaid
graph TD
    S1["1 · Transcript Extraction<br/><i>5 min · Auto</i><br/>Claude pulls quotes, pain points,<br/>budget signals, stakeholder dynamics"]:::auto
    S2["2 · Strategic Framing<br/><i>5 min · HUMAN</i><br/>What's the real priority?<br/>What political landmines?"]:::human
    S3["3 · Structure Generation<br/><i>6 min · Auto</i><br/>Proposal skeleton from<br/>strategy + extracted data"]:::auto
    S4["4 · Content Sprint<br/><i>18 min · Hybrid</i><br/>Human writes exec summary<br/>AI drafts methodology"]:::hybrid
    S5["5 · Scope Reality Check<br/><i>3 min · HUMAN</i><br/>Can we deliver this?<br/>Promises vs. reality"]:::human
    S6["6 · Polish & Compliance<br/><i>8 min · Auto</i><br/>Terminology, pricing,<br/>format checks"]:::auto
    S7["7 · Final Review<br/><i>5 min · HUMAN</i><br/>Does it sound like someone<br/>who was on those calls?"]:::human
    S8["8 · Package & Send<br/><i>5 min · Auto</i><br/>PDF, email draft,<br/>calendar invite"]:::auto

    S1 --> S2
    S2 --> S3
    S3 --> S4
    S4 --> S5
    S5 --> S6
    S6 --> S7
    S7 --> S8

    classDef auto fill:#1e3a5f,stroke:#3b82f6,color:#93c5fd
    classDef human fill:#451a03,stroke:#f97316,color:#fdba74
    classDef hybrid fill:#052e16,stroke:#10b981,color:#6ee7b7
```
""")
        
        st.divider()
        
        # ── Agent Reasoning Panels ──
        st.markdown("### 📋 Agent Reasoning")
        st.caption("Each agent's full output from the deliberation session. Click to expand.")
        st.markdown("")
        
        for agent_name, css_class, description in AGENTS:
            if agent_name in existing:
                with st.expander(f"**{agent_name}** — {description}", expanded=(agent_name == "Architect (Revised)")):
                    st.markdown(existing[agent_name])
        
        st.divider()
        st.markdown("### 📊 Deliberation Summary")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Agents", "4 specialized")
        with col2:
            st.metric("Deliberation Rounds", "6 stages")
        with col3:
            total_chars = sum(len(v) for v in existing.values())
            st.metric("Total Reasoning", f"{total_chars:,} chars")
    
    else:
        st.info("Click **Run Multi-Agent Deliberation** to start the planning session. Each agent will reason through the challenge and collaborate to design the optimal workflow.")
        
        st.markdown("### How It Works")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **🔍 Researcher**  
            Investigates what makes transit consulting proposals win — structure, tone, common failures, and what decision-makers actually look for.
            
            **🏗️ Architect**  
            Takes the research and designs a concrete step-by-step workflow with timing, inputs, outputs, and human/AI designation for each step.
            """)
        with col2:
            st.markdown("""
            **👁️ Critical Eye**  
            Reviews every automated step and asks: "Where would a wrong AI call cascade into a disaster?" Adds human judgment checkpoints with specific rationale.
            
            **🔧 Toolsmith**  
            Maps real tools (Claude, Granola, Zapier, Google Docs) to each step, prioritizing reliability and solo-maintainability over cleverness.
            """)
