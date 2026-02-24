"""
Workflow Architect: A Multi-Agent AI Planner
=============================================
Four specialized AI agents collaborate to design the optimal
transcript-to-proposal workflow for a transit consulting firm.

The system ingests REAL call transcripts and designs a workflow plan
tailored to the specific client, their needs, political dynamics,
and technical context discussed in those calls.

It does NOT write the proposal. It plans HOW you would create one.

Agents:
  1. Researcher    - What makes proposals win in transit consulting
  2. Architect     - Designs the step-by-step workflow tailored to these transcripts
  3. Critical Eye  - Identifies where human judgment is essential given this client
  4. Toolsmith     - Maps real tools (with APIs) to each workflow step

The agents run in a deliberation loop:
  Researcher -> Architect v1 -> Critical Eye -> Toolsmith -> Architect v2 -> Critical Eye final pass
"""

import os
import glob
import time
from dataclasses import dataclass, field
from typing import Callable
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ---------------------------------------------------------------------------
# The Challenge (verbatim from the job posting)
# ---------------------------------------------------------------------------
CHALLENGE = """
I just finished a call with a transit agency director who's excited and wants a
proposal. I have the transcript from our last three conversations. My goal is to
get them a tailored, professional proposal within 60 minutes of the call ending.
What would you build, configure, or stitch together to make that possible? Think
about the tools, the workflow, and where human judgment still matters.
"""


# ---------------------------------------------------------------------------
# Transcript loader
# ---------------------------------------------------------------------------
def load_transcripts(transcript_dir: str = "transcripts") -> str:
    """Load all transcript files from the given directory."""
    files = sorted(glob.glob(os.path.join(transcript_dir, "*.txt")))
    if not files:
        raise FileNotFoundError(f"No transcript files found in {transcript_dir}/")

    all_transcripts = []
    for f in files:
        with open(f, "r") as fh:
            content = fh.read().strip()
            filename = os.path.basename(f)
            all_transcripts.append(f"=== {filename} ===\n{content}")

    combined = "\n\n".join(all_transcripts)
    print(f"Loaded {len(files)} transcripts ({len(combined)} chars total)")
    return combined


# ---------------------------------------------------------------------------
# Agent System Prompts
# ---------------------------------------------------------------------------

RESEARCHER_SYSTEM = """You are the Researcher agent in a multi-agent workflow planning system.

You will receive ACTUAL call transcripts between a transit consultant and a client agency.
Your expertise: professional proposals in the transit consulting industry.

Your job is to provide a concise research brief covering:
1. What separates a winning transit consulting proposal from a forgettable one (structure, tone, specificity)
2. Common failure modes in proposals (generic language, wrong scope, misread priorities)
3. What transit agency decision-makers actually look for (based on public sector procurement norms)
4. Key structural elements of a strong proposal (exec summary, problem framing, scope, timeline, pricing, team credibility)
5. Based on THESE SPECIFIC TRANSCRIPTS: what personalization opportunities exist? What client-specific details should shape the proposal?

Ground your advice in what you actually read in the transcripts. Reference specific moments, quotes, and dynamics you observed.

Keep it practical and actionable. No fluff. The Architect agent will use your findings to design a workflow.
Write 400-600 words. Use plain language."""

ARCHITECT_SYSTEM = """You are the Architect agent in a multi-agent workflow planning system.

You will receive ACTUAL call transcripts between a transit consultant and a client agency.

Your job: design a step-by-step workflow plan for turning THESE SPECIFIC transcripts into a tailored, professional proposal within 60 minutes of the last call ending.

IMPORTANT: You are designing THE PLAN for how to create the proposal, not creating the proposal itself. Different transcripts will require different plans because every client has different needs, politics, data situations, and sensitivities.

For THESE transcripts specifically, consider:
- What data or research needs to be pulled given what the client discussed?
- What sections of the proposal need extra attention based on the client's priorities?
- Where are the politically sensitive areas that need careful framing?
- What specific personalization should be woven in?

You will receive:
- The actual transcripts
- The Researcher's findings on what makes proposals win
- (On revision) Feedback from the Critical Eye and Toolsmith agents

Design constraints:
- Total end-to-end time: 60 minutes max
- The workflow is for a solo founder at a small consulting firm (one person, AI-augmented)
- Must be repeatable and practical, not theoretical
- Each step must have: name, estimated time, whether it's automated or human, inputs, outputs
- The plan should be SPECIFIC to the content of these transcripts

Your output should be a clear, numbered workflow with timing for each step.
Be specific about what happens at each stage. Reference specific topics, concerns, and dynamics from the transcripts.

On revision rounds: integrate the Critical Eye's human judgment checkpoints and the Toolsmith's tool recommendations. Show what changed and why.

Write 500-700 words."""

CRITICAL_EYE_SYSTEM = """You are the Critical Eye agent in a multi-agent workflow planning system.

You have access to the ACTUAL call transcripts. Your singular obsession: finding the moments where human judgment is irreplaceable GIVEN WHAT WAS DISCUSSED IN THESE SPECIFIC CALLS.

You will receive the Architect's proposed workflow plan. Your job is to:

1. Go through each automated step and ask: "Given what this client said, what could go wrong if no human reviews this?"
2. Identify SPECIFIC points where a wrong AI call cascades into a bad proposal FOR THIS CLIENT
3. Distinguish between "human review nice-to-have" and "human decision ESSENTIAL"
4. For each checkpoint you add, explain:
   - WHY a human must decide here, referencing SPECIFIC moments from the transcripts
   - What SPECIFIC context from these calls AI is likely to miss or misinterpret
   - What the COST of an AI mistake is at this point given this client relationship
   - How long the human decision takes (be realistic)

Look at these transcripts for:
- Moments where the client said something that means more than the words suggest
- Political dynamics, stakeholder tensions, or sensitivities mentioned
- Budget constraints or procurement rules that affect how you frame things
- Relationship warmth indicators that should influence tone
- Things the client explicitly asked for vs. things they need but didn't say

Be a constructive contrarian. Challenge automation where it's fragile.
Don't add checkpoints everywhere. Find the 3-5 moments that MOST change THIS proposal's trajectory.

Write 400-600 words."""

TOOLSMITH_SYSTEM = """You are the Toolsmith agent in a multi-agent workflow planning system.

You have access to the ACTUAL call transcripts and the proposed workflow plan.

Your job: map real, practical tools WITH AVAILABLE APIs to each step of the proposed workflow.

For each workflow step, recommend:
1. The specific tool(s) to use
2. WHY that tool over alternatives (briefly)
3. Integration complexity (trivial / moderate / complex)
4. Whether the founder can maintain this solo without engineering support

IMPORTANT CONSTRAINTS on tool selection:
- Recommend ANY real tools that would help - including Granola, Zapier, Google Docs, Notion, etc.
- You can recommend both API-driven tools AND GUI/manual tools
- This is for ONE person, not a team. No enterprise tooling.
- Prefer free tiers or low cost
- Prioritize reliability over cleverness

Given THESE SPECIFIC TRANSCRIPTS, consider what tools are needed for the particular data analysis, research, or formatting tasks the proposal will require.

Also suggest the simplest possible "v1" tech stack - what's the minimum viable set of tools to make this work TODAY.

Write 300-500 words."""


# ---------------------------------------------------------------------------
# Agent runner
# ---------------------------------------------------------------------------
@dataclass
class AgentResult:
    agent_name: str
    output: str
    timestamp: float = field(default_factory=time.time)
    input_context: str = ""


def run_agent(
    agent_name: str,
    system_prompt: str,
    user_message: str,
    on_stream: Callable[[str], None] | None = None,
) -> AgentResult:
    """Run a single agent and return its result."""

    full_response = ""
    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        for text in stream.text_stream:
            full_response += text
            if on_stream:
                on_stream(text)

    return AgentResult(
        agent_name=agent_name,
        output=full_response,
        input_context=user_message[:200] + "..." if len(user_message) > 200 else user_message,
    )


# ---------------------------------------------------------------------------
# Orchestrator: runs the full multi-agent deliberation loop
# ---------------------------------------------------------------------------
def run_deliberation(
    transcript_dir: str = "transcripts",
    on_stream: Callable[[str, str], None] | None = None,
):
    """
    Run the full 6-step deliberation:
      1. Researcher   (reads transcripts + proposal best practices)
      2. Architect v1 (designs workflow plan tailored to these transcripts)
      3. Critical Eye (identifies human judgment points specific to this client)
      4. Toolsmith    (maps API-available tools to each step)
      5. Architect v2 (revised plan incorporating all feedback)
      6. Critical Eye final pass

    on_stream(agent_name, text_chunk) is called for each streamed token.
    Returns list of AgentResult objects.
    """
    # Load transcripts
    transcripts = load_transcripts(transcript_dir)
    results = []

    def make_streamer(agent_name):
        if on_stream:
            return lambda text: on_stream(agent_name, text)
        return None

    # --- Step 1: Researcher ---
    print("\n[1/6] Researcher agent starting...")
    researcher = run_agent(
        "Researcher",
        RESEARCHER_SYSTEM,
        (
            f"CHALLENGE:\n{CHALLENGE}\n\n"
            f"CALL TRANSCRIPTS:\n{transcripts}\n\n"
            "Provide your research brief. Ground your advice in what you read in these specific transcripts."
        ),
        make_streamer("Researcher"),
    )
    results.append(researcher)
    print(f"  -> Researcher done ({len(researcher.output)} chars)")

    # --- Step 2: Architect v1 ---
    print("\n[2/6] Architect agent starting (v1)...")
    architect_v1 = run_agent(
        "Architect",
        ARCHITECT_SYSTEM,
        (
            f"CHALLENGE:\n{CHALLENGE}\n\n"
            f"CALL TRANSCRIPTS:\n{transcripts}\n\n"
            f"RESEARCHER'S FINDINGS:\n{researcher.output}\n\n"
            "Design a workflow plan tailored to these specific transcripts. "
            "The plan should reflect this client's unique needs, politics, and context."
        ),
        make_streamer("Architect"),
    )
    results.append(architect_v1)
    print(f"  -> Architect v1 done ({len(architect_v1.output)} chars)")

    # --- Step 3: Critical Eye ---
    print("\n[3/6] Critical Eye agent starting...")
    critical_eye = run_agent(
        "Critical Eye",
        CRITICAL_EYE_SYSTEM,
        (
            f"CHALLENGE:\n{CHALLENGE}\n\n"
            f"CALL TRANSCRIPTS:\n{transcripts}\n\n"
            f"PROPOSED WORKFLOW PLAN:\n{architect_v1.output}\n\n"
            "Identify the critical human judgment checkpoints for THIS specific client and situation."
        ),
        make_streamer("Critical Eye"),
    )
    results.append(critical_eye)
    print(f"  -> Critical Eye done ({len(critical_eye.output)} chars)")

    # --- Step 4: Toolsmith ---
    print("\n[4/6] Toolsmith agent starting...")
    toolsmith = run_agent(
        "Toolsmith",
        TOOLSMITH_SYSTEM,
        (
            f"CHALLENGE:\n{CHALLENGE}\n\n"
            f"CALL TRANSCRIPTS:\n{transcripts}\n\n"
            f"WORKFLOW PLAN:\n{architect_v1.output}\n\n"
            f"HUMAN JUDGMENT CHECKPOINTS:\n{critical_eye.output}\n\n"
            "Map tools with real APIs to each step. No GUI-only tools."
        ),
        make_streamer("Toolsmith"),
    )
    results.append(toolsmith)
    print(f"  -> Toolsmith done ({len(toolsmith.output)} chars)")

    # --- Step 5: Architect v2 (revision) ---
    print("\n[5/6] Architect agent starting (v2 - revision)...")
    architect_v2 = run_agent(
        "Architect (Revised)",
        ARCHITECT_SYSTEM,
        (
            f"CHALLENGE:\n{CHALLENGE}\n\n"
            f"CALL TRANSCRIPTS:\n{transcripts}\n\n"
            f"YOUR ORIGINAL WORKFLOW PLAN:\n{architect_v1.output}\n\n"
            f"CRITICAL EYE FEEDBACK:\n{critical_eye.output}\n\n"
            f"TOOLSMITH RECOMMENDATIONS:\n{toolsmith.output}\n\n"
            "Revise your workflow plan incorporating this feedback. Show what changed and why. "
            "This is the final plan - make it concrete, timed, and actionable for THIS specific client."
        ),
        make_streamer("Architect (Revised)"),
    )
    results.append(architect_v2)
    print(f"  -> Architect v2 done ({len(architect_v2.output)} chars)")

    # --- Step 6: Critical Eye final pass ---
    print("\n[6/6] Critical Eye final pass...")
    critical_final = run_agent(
        "Critical Eye (Final)",
        CRITICAL_EYE_SYSTEM + "\n\nThis is your FINAL pass. The workflow plan has been revised based on your earlier feedback. Confirm the human judgment checkpoints are well-placed for THIS CLIENT, flag anything still missing, and give a brief final assessment. Be concise.",
        (
            f"CHALLENGE:\n{CHALLENGE}\n\n"
            f"CALL TRANSCRIPTS:\n{transcripts}\n\n"
            f"REVISED WORKFLOW PLAN:\n{architect_v2.output}\n\n"
            "Final review: Are the human judgment checkpoints sufficient for this specific client and situation?"
        ),
        make_streamer("Critical Eye (Final)"),
    )
    results.append(critical_final)
    print(f"  -> Critical Eye final pass done ({len(critical_final.output)} chars)")

    return results


# ---------------------------------------------------------------------------
# Save outputs
# ---------------------------------------------------------------------------
def save_results(results: list[AgentResult], output_dir: str = "output"):
    """Save all agent outputs to files."""
    os.makedirs(output_dir, exist_ok=True)
    
    for i, r in enumerate(results):
        safe_name = r.agent_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        filepath = os.path.join(output_dir, f"{i+1}_{safe_name}.md")
        with open(filepath, "w") as f:
            f.write(f"# {r.agent_name}\n\n")
            f.write(r.output)
        print(f"  Saved: {filepath}")

    # Save combined output
    combined_path = os.path.join(output_dir, "full_deliberation.md")
    with open(combined_path, "w") as f:
        f.write("# Workflow Architect: Full Multi-Agent Deliberation\n\n")
        f.write("---\n\n")
        for i, r in enumerate(results):
            f.write(f"## Stage {i+1}: {r.agent_name}\n\n")
            f.write(r.output)
            f.write("\n\n---\n\n")
    print(f"  Saved combined: {combined_path}")

    return combined_path


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("WORKFLOW ARCHITECT - Multi-Agent Deliberation")
    print("=" * 60)
    
    results = run_deliberation()
    
    print("\n" + "=" * 60)
    print("SAVING RESULTS")
    print("=" * 60)
    save_results(results)
    
    print("\nDone! Check the output/ directory.")
