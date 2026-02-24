"""
Workflow Architect: A Multi-Agent AI Planner
=============================================
Four specialized AI agents collaborate to design the optimal
transcript-to-proposal workflow for a transit consulting firm.

Agents:
  1. Researcher    - What makes proposals win in transit consulting
  2. Architect     - Designs the step-by-step workflow
  3. Critical Eye  - Identifies where human judgment is essential
  4. Toolsmith     - Maps real tools to each workflow step

The agents run in a deliberation loop:
  Researcher -> Architect v1 -> Critical Eye -> Toolsmith -> Architect v2 (revised) -> Critical Eye final pass
"""

import os
import json
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
# Agent System Prompts
# ---------------------------------------------------------------------------

RESEARCHER_SYSTEM = """You are the Researcher agent in a multi-agent workflow planning system.

Your expertise: professional proposals in the transit consulting industry.

Your job is to provide a concise research brief covering:
1. What separates a winning transit consulting proposal from a forgettable one (structure, tone, specificity)
2. Common failure modes in proposals (generic language, wrong scope, misread priorities)
3. What transit agency decision-makers actually look for (based on public sector procurement norms)
4. Key structural elements of a strong proposal (exec summary, problem framing, scope, timeline, pricing, team credibility)
5. How personalization and client-specific insight dramatically increase win rates

Keep it practical and actionable. No fluff. The Architect agent will use your findings to design a workflow.
Write 400-600 words. Use plain language."""

ARCHITECT_SYSTEM = """You are the Architect agent in a multi-agent workflow planning system.

Your job: design a step-by-step workflow that takes 1-3 call transcripts and produces a tailored, professional transit consulting proposal within 60 minutes of the last call ending.

You will receive:
- The Researcher's findings on what makes proposals win
- (On revision) Feedback from the Critical Eye and Toolsmith agents

Design constraints:
- Total end-to-end time: 60 minutes max
- The workflow is for a solo founder at a small consulting firm (one person, AI-augmented)
- Must be repeatable and practical, not theoretical
- Each step must have: name, estimated time, whether it's automated or human, inputs, outputs

Your output should be a clear, numbered workflow with timing for each step.
Be specific about what happens at each stage. Not "analyze transcript" but exactly what gets extracted and why.

On revision rounds: integrate the Critical Eye's human judgment checkpoints and the Toolsmith's tool recommendations. Show what changed and why.

Write 500-700 words."""

CRITICAL_EYE_SYSTEM = """You are the Critical Eye agent in a multi-agent workflow planning system.

Your singular obsession: finding the moments where human judgment is irreplaceable.

You will receive the Architect's proposed workflow. Your job is to:

1. Go through each automated step and ask: "What could go wrong if no human sees this?"
2. Identify SPECIFIC points where a wrong AI call cascades into a bad proposal
3. Distinguish between "human review nice-to-have" and "human decision ESSENTIAL"
4. For each checkpoint you add, explain:
   - WHY a human must decide here (not just "review")
   - What SPECIFIC context AI is likely to miss
   - What the COST of an AI mistake is at this point
   - How long the human decision takes (be realistic - seconds? minutes?)

Focus areas where human judgment is most critical:
- Reading between the lines of what a client said vs. meant
- Scoping decisions (what to include AND what to deliberately exclude)
- Tone calibration based on relationship warmth
- Political dynamics within the agency
- Knowing when a "quick win" proposal beats a comprehensive one
- The unspoken need the client hasn't articulated

Be a constructive contrarian. Challenge automation where it's fragile.
Don't add checkpoints everywhere - that defeats the purpose. Find the 3-5 moments that MOST change the proposal's trajectory.

Write 400-600 words."""

TOOLSMITH_SYSTEM = """You are the Toolsmith agent in a multi-agent workflow planning system.

Your job: map real, practical tools to each step of the proposed workflow.

You will receive the Architect's workflow and the Critical Eye's human judgment checkpoints.

For each workflow step, recommend:
1. The specific tool(s) to use (from real products: Claude/Anthropic API, Granola, Zapier, Google Docs, Notion, Otter.ai, Fireflies, Streamlit, Python, Pandoc, etc.)
2. WHY that tool over alternatives (briefly)
3. Integration complexity (trivial / moderate / complex)
4. Whether the founder can maintain this solo without engineering support

Key constraints:
- This is for ONE person, not a team. No enterprise tooling.
- Prefer tools that integrate with each other
- Prefer tools with free tiers or low cost
- The founder already uses: Claude, Granola, Zapier
- Prioritize reliability over cleverness
- Flag any step where tooling is weak or fragile

Also suggest the simplest possible "v1" tech stack - what's the minimum viable set of tools to make this work TODAY, not after a month of setup.

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
    
    # Stream the response
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
def run_deliberation(on_stream: Callable[[str, str], None] | None = None):
    """
    Run the full 6-step deliberation:
      1. Researcher
      2. Architect v1
      3. Critical Eye
      4. Toolsmith
      5. Architect v2 (revised)
      6. Critical Eye final pass
    
    on_stream(agent_name, text_chunk) is called for each streamed token.
    Returns list of AgentResult objects.
    """
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
        f"Here is the challenge we're designing a workflow for:\n\n{CHALLENGE}\n\nProvide your research brief on what makes transit consulting proposals win.",
        make_streamer("Researcher"),
    )
    results.append(researcher)
    print(f"  -> Researcher done ({len(researcher.output)} chars)")

    # --- Step 2: Architect v1 ---
    print("\n[2/6] Architect agent starting (v1)...")
    architect_v1 = run_agent(
        "Architect",
        ARCHITECT_SYSTEM,
        f"CHALLENGE:\n{CHALLENGE}\n\nRESEARCHER'S FINDINGS:\n{researcher.output}\n\nDesign the workflow.",
        make_streamer("Architect"),
    )
    results.append(architect_v1)
    print(f"  -> Architect v1 done ({len(architect_v1.output)} chars)")

    # --- Step 3: Critical Eye ---
    print("\n[3/6] Critical Eye agent starting...")
    critical_eye = run_agent(
        "Critical Eye",
        CRITICAL_EYE_SYSTEM,
        f"CHALLENGE:\n{CHALLENGE}\n\nPROPOSED WORKFLOW:\n{architect_v1.output}\n\nIdentify the critical human judgment checkpoints.",
        make_streamer("Critical Eye"),
    )
    results.append(critical_eye)
    print(f"  -> Critical Eye done ({len(critical_eye.output)} chars)")

    # --- Step 4: Toolsmith ---
    print("\n[4/6] Toolsmith agent starting...")
    toolsmith = run_agent(
        "Toolsmith",
        TOOLSMITH_SYSTEM,
        f"CHALLENGE:\n{CHALLENGE}\n\nWORKFLOW:\n{architect_v1.output}\n\nHUMAN JUDGMENT CHECKPOINTS:\n{critical_eye.output}\n\nMap tools to each step.",
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
            f"YOUR ORIGINAL WORKFLOW:\n{architect_v1.output}\n\n"
            f"CRITICAL EYE FEEDBACK:\n{critical_eye.output}\n\n"
            f"TOOLSMITH RECOMMENDATIONS:\n{toolsmith.output}\n\n"
            "Revise your workflow incorporating this feedback. Show what changed and why. "
            "This is the final workflow - make it concrete, timed, and actionable."
        ),
        make_streamer("Architect (Revised)"),
    )
    results.append(architect_v2)
    print(f"  -> Architect v2 done ({len(architect_v2.output)} chars)")

    # --- Step 6: Critical Eye final pass ---
    print("\n[6/6] Critical Eye final pass...")
    critical_final = run_agent(
        "Critical Eye (Final)",
        CRITICAL_EYE_SYSTEM + "\n\nThis is your FINAL pass. The workflow has been revised based on your earlier feedback. Confirm the human judgment checkpoints are well-placed, flag anything still missing, and give a brief final assessment of the workflow's readiness. Be concise.",
        (
            f"CHALLENGE:\n{CHALLENGE}\n\n"
            f"REVISED WORKFLOW:\n{architect_v2.output}\n\n"
            "Final review: Are the human judgment checkpoints sufficient? Is anything still automated that shouldn't be?"
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
