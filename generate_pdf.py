"""
Generate the Challenge 2 workflow PDF.
Reads the architect's output dynamically and uses Claude to extract
structured steps, then renders a compact left-to-right flowchart.
"""

import os
import json
from fpdf import FPDF
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# ── Colors ──
C_AUTO   = (59, 130, 246)    # blue
C_HUMAN  = (239, 108, 0)     # warm orange
C_HYBRID = (16, 163, 127)    # teal
C_BG_AUTO   = (235, 243, 254)
C_BG_HUMAN  = (255, 241, 229)
C_BG_HYBRID = (230, 250, 245)
C_ARROW  = (160, 170, 180)
C_TEXT   = (35, 35, 35)
C_MUTED  = (110, 115, 125)


class ResponsePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=False)

    # ── Drawing helpers ──

    def rounded_box(self, x, y, w, h, r, fill_rgb, border_rgb):
        """Draw a rounded rectangle with fill and border."""
        self.set_fill_color(*fill_rgb)
        self.set_draw_color(*border_rgb)
        self.set_line_width(0.5)
        self.rect(x, y, w, h, style="DF", round_corners=True, corner_radius=r)

    def arrow_down(self, x, y1, y2):
        """Draw a small downward arrow from y1 to y2 at x."""
        self.set_draw_color(*C_ARROW)
        self.set_line_width(0.4)
        self.line(x, y1, x, y2)
        # arrowhead
        self.set_fill_color(*C_ARROW)
        self.polygon(
            [(x - 1.5, y2 - 2), (x + 1.5, y2 - 2), (x, y2)],
            style="F",
        )

    def arrow_right(self, x1, x2, y):
        """Draw a horizontal arrow from x1 to x2 at y."""
        self.set_draw_color(*C_ARROW)
        self.set_line_width(0.4)
        self.line(x1, y, x2, y)
        self.set_fill_color(*C_ARROW)
        self.polygon(
            [(x2 - 2, y - 1.5), (x2 - 2, y + 1.5), (x2, y)],
            style="F",
        )

    def arrow_bend(self, x_start, y_start, x_end, y_end):
        """Draw an L-shaped arrow: right then down (for row wrap)."""
        self.set_draw_color(*C_ARROW)
        self.set_line_width(0.4)
        # go down from start, then left to end
        mid_y = y_start + (y_end - y_start) * 0.5
        self.line(x_start, y_start, x_start, mid_y)
        self.line(x_start, mid_y, x_end, mid_y)
        self.line(x_end, mid_y, x_end, y_end)
        self.set_fill_color(*C_ARROW)
        self.polygon(
            [(x_end - 1.5, y_end - 2), (x_end + 1.5, y_end - 2), (x_end, y_end)],
            style="F",
        )

    def agent_pill(self, x, y, w, h, label, fill_rgb, text_rgb):
        """Draw a small pill/chip for agent names."""
        self.set_fill_color(*fill_rgb)
        self.set_draw_color(*fill_rgb)
        self.set_line_width(0.3)
        self.rect(x, y, w, h, style="DF", round_corners=True, corner_radius=h / 2)
        self.set_font("Helvetica", "B", 7)
        self.set_text_color(*text_rgb)
        self.set_xy(x, y)
        self.cell(w, h, label, align="C")


def extract_steps_from_output(output_dir="output"):
    """Read the revised architect output and ask Claude to extract structured steps."""
    architect_path = os.path.join(output_dir, "5_architect_revised.md")
    toolsmith_path = os.path.join(output_dir, "4_toolsmith.md")

    architect_text = open(architect_path).read()
    toolsmith_text = open(toolsmith_path).read()

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"""Extract the workflow steps from this architect plan and toolsmith analysis into structured JSON.

ARCHITECT PLAN:
{architect_text}

TOOLSMITH ANALYSIS:
{toolsmith_text}

Return ONLY valid JSON (no markdown fencing) with this exact structure:
{{
  "steps": [
    {{
      "name": "short name (max 16 chars)",
      "desc": "what happens (max 50 chars)",
      "tools": "tool(s) used (max 30 chars)",
      "type": "auto" or "human" or "hybrid",
      "time": "X min"
    }}
  ]
}}

Rules:
- Extract 8-12 steps maximum, combining small steps if needed
- Use plain ASCII only (no em dashes, smart quotes, or special characters)
- Keep names very short - they go in small boxes
- "type" must be exactly "auto", "human", or "hybrid"
- Order steps chronologically as in the plan"""
        }]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(raw)["steps"]


def generate(github_url="https://github.com/elliotnou/kts"):
    # ── Extract steps dynamically from agent outputs ──
    print("Extracting steps from agent outputs via Claude...")
    steps = extract_steps_from_output()
    print(f"  Got {len(steps)} steps")

    pdf = ResponsePDF()
    pdf.add_page()
    pdf.set_margins(12, 10, 12)
    pdf.set_y(10)

    W = pdf.w - pdf.l_margin - pdf.r_margin

    # ── Title (compact) ──
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 5, "AI-Generated Proposal Workflow", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(*C_MUTED)
    pdf.cell(0, 3.5, "Dynamically planned by multi-agent system from call transcripts",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # ── Layout: left-to-right grid, ~65% of page ──
    type_styles = {
        "auto":   (C_BG_AUTO,   C_AUTO),
        "human":  (C_BG_HUMAN,  C_HUMAN),
        "hybrid": (C_BG_HYBRID, C_HYBRID),
    }

    cols = 4
    rows = (len(steps) + cols - 1) // cols
    h_gap = 3.5
    v_gap = 5
    box_w = (W - (cols - 1) * h_gap) / cols
    # Cap box height so flowchart stays in top ~65%
    max_flowchart_h = 297 * 0.55 - pdf.get_y()  # A4 = 297mm
    box_h = min(32, (max_flowchart_h - (rows - 1) * v_gap) / rows)

    start_y = pdf.get_y()
    box_positions = []

    for idx, step in enumerate(steps):
        row = idx // cols
        col = idx % cols

        s_type = step.get("type", "auto")
        if s_type not in type_styles:
            s_type = "auto"
        bg, border = type_styles[s_type]

        x = pdf.l_margin + col * (box_w + h_gap)
        y = start_y + row * (box_h + v_gap)
        box_positions.append((x, y, box_w, box_h))

        # Draw box
        pdf.rounded_box(x, y, box_w, box_h, 2.5, bg, border)

        # Step number (top-left)
        pdf.set_font("Helvetica", "B", 6.5)
        pdf.set_text_color(*border)
        pdf.set_xy(x + 1.5, y + 1)
        pdf.cell(6, 3, str(idx + 1))

        # Type + time badge (top-right)
        badge = f"{s_type.upper()} | {step.get('time', '')}"
        pdf.set_font("Helvetica", "B", 5)
        pdf.set_text_color(*border)
        pdf.set_xy(x + box_w - 22, y + 1)
        pdf.cell(20.5, 3, badge, align="R")

        # Step name
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(25, 25, 25)
        pdf.set_xy(x + 1.5, y + 5)
        pdf.multi_cell(box_w - 3, 3.2, step["name"], align="L")

        # Description
        pdf.set_font("Helvetica", "", 5.5)
        pdf.set_text_color(70, 70, 70)
        pdf.set_xy(x + 1.5, y + 12.5)
        pdf.multi_cell(box_w - 3, 2.8, step.get("desc", ""), align="L")

        # Tools (bottom)
        pdf.set_font("Helvetica", "I", 5)
        pdf.set_text_color(*border)
        pdf.set_xy(x + 1.5, y + box_h - 5)
        pdf.multi_cell(box_w - 3, 2.5, step.get("tools", ""), align="L")

    # ── Arrows between boxes ──
    for i in range(len(steps) - 1):
        x1, y1, w1, h1 = box_positions[i]
        x2, y2, w2, h2 = box_positions[i + 1]
        i_col = i % cols
        if i_col < cols - 1:
            pdf.arrow_right(x1 + w1 + 0.5, x2 - 0.5, y1 + h1 / 2)
        else:
            pdf.arrow_bend(x1 + w1 / 2, y1 + h1, x2 + w2 / 2, y2)

    # ── Legend ──
    last_row = (len(steps) - 1) // cols
    legend_y = start_y + (last_row + 1) * (box_h + v_gap) + 1
    items = [
        ("AI-AUTOMATED", C_AUTO, C_BG_AUTO),
        ("HUMAN JUDGMENT", C_HUMAN, C_BG_HUMAN),
        ("HYBRID", C_HYBRID, C_BG_HYBRID),
    ]
    for i, (label, border_c, bg_c) in enumerate(items):
        lx = pdf.l_margin + i * 32
        pdf.set_fill_color(*bg_c)
        pdf.set_draw_color(*border_c)
        pdf.set_line_width(0.4)
        pdf.rect(lx, legend_y, 4, 3, style="DF", round_corners=True, corner_radius=1)
        pdf.set_font("Helvetica", "", 5.5)
        pdf.set_text_color(*C_MUTED)
        pdf.set_xy(lx + 5, legend_y)
        pdf.cell(26, 3, label)

    # ── Output ──
    output_path = os.path.join(os.path.dirname(__file__), "challenge_2_response.pdf")
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")
    return output_path


if __name__ == "__main__":
    generate()
