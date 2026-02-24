"""
Generate the one-page Challenge 2 response PDF.
Visual flowcharts, color-coded boxes, arrows - not a boring list.
"""

import os
from fpdf import FPDF


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


def generate(github_url="https://github.com/YOUR_USERNAME/workflow-architect"):
    pdf = ResponsePDF()
    pdf.add_page()
    pdf.set_margins(18, 14, 18)
    pdf.set_y(14)

    W = pdf.w - pdf.l_margin - pdf.r_margin

    # ════════════════════════════════════════════════════════
    # TITLE
    # ════════════════════════════════════════════════════════
    pdf.set_font("Helvetica", "B", 13.5)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 7, "Challenge 2: Automate My Workflow", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 8.5)
    pdf.set_text_color(*C_MUTED)
    pdf.cell(0, 4, "I didn't just design a workflow. I built an AI system that designs the workflow for you.",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # ════════════════════════════════════════════════════════
    # INTRO (compact)
    # ════════════════════════════════════════════════════════
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_TEXT)
    pdf.multi_cell(0, 4.3,
        "Anyone with Claude can sketch a transcript-to-proposal pipeline. The harder question: "
        "how do you know it's the right one? Where should a human be involved? What tools actually "
        "hold up under a 60-minute deadline? So instead of guessing, I built a multi-agent AI planner "
        "- four specialized agents that deliberate to design the optimal workflow. Then I ran it."
    )
    pdf.ln(3)

    # ════════════════════════════════════════════════════════
    # AGENT DELIBERATION FLOW (horizontal pills with arrows)
    # ════════════════════════════════════════════════════════
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 5, "The Multi-Agent Deliberation", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    agent_y = pdf.get_y()
    agents = [
        ("Researcher", (59, 130, 246), (255, 255, 255)),
        ("Architect v1", (16, 163, 127), (255, 255, 255)),
        ("Critical Eye", (239, 108, 0), (255, 255, 255)),
        ("Toolsmith", (139, 92, 246), (255, 255, 255)),
        ("Architect v2", (16, 163, 127), (255, 255, 255)),
        ("Final Review", (239, 108, 0), (255, 255, 255)),
    ]

    pill_w = 24
    pill_h = 6.5
    gap = 5.5
    total_w = len(agents) * pill_w + (len(agents) - 1) * gap
    start_x = pdf.l_margin + (W - total_w) / 2

    for i, (label, fill, text) in enumerate(agents):
        x = start_x + i * (pill_w + gap)
        pdf.agent_pill(x, agent_y, pill_w, pill_h, label, fill, text)
        if i < len(agents) - 1:
            pdf.arrow_right(x + pill_w + 0.5, x + pill_w + gap - 0.5, agent_y + pill_h / 2)

    pdf.set_y(agent_y + pill_h + 2)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(*C_MUTED)
    pdf.cell(0, 3.5, "Each agent receives all prior outputs. The Architect revised significantly after feedback.",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # ════════════════════════════════════════════════════════
    # WORKFLOW FLOWCHART (two rows of 4 boxes, connected)
    # ════════════════════════════════════════════════════════
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 5, "What They Designed: The 55-Minute Proposal Workflow", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    steps = [
        # (name, time, type, short_desc)
        ("Transcript\nExtraction", "5 min", "auto", "Claude pulls quotes,\npain points, signals"),
        ("Strategic\nFraming", "5 min", "human", "What's the real need?\nPolitical landmines?"),
        ("Structure\nGeneration", "6 min", "auto", "Proposal skeleton from\nstrategy + data"),
        ("Content\nSprint", "18 min", "hybrid", "Human: exec summary\nAI: methodology draft"),
        ("Scope Reality\nCheck", "3 min", "human", "Can we deliver this?\nPromises vs. reality"),
        ("Polish &\nCompliance", "8 min", "auto", "Terminology, pricing,\nformat checks"),
        ("Final\nReview", "5 min", "human", "Does it sound like\nsomeone who was there?"),
        ("Package\n& Send", "5 min", "auto", "PDF, email draft,\ncalendar invite"),
    ]

    type_styles = {
        "auto":   (C_BG_AUTO,   C_AUTO,   C_AUTO),
        "human":  (C_BG_HUMAN,  C_HUMAN,  C_HUMAN),
        "hybrid": (C_BG_HYBRID, C_HYBRID, C_HYBRID),
    }

    box_w = 38
    box_h = 28
    h_gap = 4.5
    v_gap = 8
    row1_y = pdf.get_y()
    row1_start_x = pdf.l_margin + (W - (4 * box_w + 3 * h_gap)) / 2

    box_positions = []

    for row in range(2):
        for col in range(4):
            idx = row * 4 + col
            s_name, s_time, s_type, s_desc = steps[idx]
            bg, border, text_c = type_styles[s_type]

            x = row1_start_x + col * (box_w + h_gap)
            y = row1_y + row * (box_h + v_gap)

            box_positions.append((x, y, box_w, box_h))

            # Draw box
            pdf.rounded_box(x, y, box_w, box_h, 3, bg, border)

            # Step number + type badge
            badge_text = s_type.upper()
            pdf.set_font("Helvetica", "B", 6)
            pdf.set_text_color(*text_c)
            pdf.set_xy(x + 2, y + 1.5)
            pdf.cell(box_w - 4, 3, badge_text, align="R")

            # Step number
            pdf.set_font("Helvetica", "B", 7)
            pdf.set_text_color(*text_c)
            pdf.set_xy(x + 2, y + 1.5)
            pdf.cell(10, 3, str(idx + 1))

            # Step name
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(30, 30, 30)
            pdf.set_xy(x + 2, y + 5.5)
            pdf.multi_cell(box_w - 4, 3.8, s_name, align="C")

            # Time
            pdf.set_font("Helvetica", "B", 7)
            pdf.set_text_color(*text_c)
            pdf.set_xy(x + 2, y + 14)
            pdf.cell(box_w - 4, 3, s_time, align="C")

            # Description
            pdf.set_font("Helvetica", "", 6.5)
            pdf.set_text_color(*C_MUTED)
            pdf.set_xy(x + 2, y + 18)
            pdf.multi_cell(box_w - 4, 3, s_desc, align="C")

    # Draw arrows between boxes
    for i in range(7):
        x1, y1, w1, h1 = box_positions[i]
        x2, y2, w2, h2 = box_positions[i + 1]

        if i == 3:
            # Row wrap: from box 4 (end of row 1) down to box 5 (start of row 2)
            # Arrow goes from bottom of box 4 to top of box 5
            mid_x_end = x1 + w1 / 2
            mid_x_start = x2 + w2 / 2
            pdf.arrow_bend(mid_x_end, y1 + h1, mid_x_start, y2)
        else:
            # Horizontal arrow
            arrow_y = y1 + h1 / 2
            pdf.arrow_right(x1 + w1 + 0.5, x2 - 0.5, arrow_y)

    pdf.set_y(row1_y + 2 * box_h + v_gap + 3)

    # ── Legend ──
    legend_y = pdf.get_y()
    legend_x = pdf.l_margin + W / 2 - 45
    items = [
        ("AUTO", C_AUTO, C_BG_AUTO),
        ("HUMAN", C_HUMAN, C_BG_HUMAN),
        ("HYBRID", C_HYBRID, C_BG_HYBRID),
    ]
    for i, (label, border_c, bg_c) in enumerate(items):
        lx = legend_x + i * 30
        pdf.set_fill_color(*bg_c)
        pdf.set_draw_color(*border_c)
        pdf.set_line_width(0.4)
        pdf.rect(lx, legend_y, 6, 4, style="DF", round_corners=True, corner_radius=1)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(*C_MUTED)
        pdf.set_xy(lx + 7, legend_y)
        pdf.cell(20, 4, label)

    pdf.set_y(legend_y + 7)

    # ════════════════════════════════════════════════════════
    # KEY INSIGHT
    # ════════════════════════════════════════════════════════
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 5, "The Interesting Part", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_TEXT)
    pdf.multi_cell(0, 4.3,
        "The Critical Eye agent kept stripping automation out. The Architect's first draft was almost "
        "fully automated. By v2, three steps had become human. Its argument: in transit consulting, "
        "misreading political subtext or overpromising scope doesn't just lose a deal - it damages "
        "the relationship permanently. The 13 minutes of human judgment aren't a bottleneck. "
        "They're the reason the proposal wins."
    )
    pdf.ln(3)

    # ════════════════════════════════════════════════════════
    # FOOTER: tools + link
    # ════════════════════════════════════════════════════════
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(*C_MUTED)
    pdf.cell(22, 4, "Tools used:", new_x="END", new_y="TOP")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.cell(0, 4, "  Claude API (multi-agent system)  |  GitHub Copilot  |  Python + Streamlit",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.cell(22, 4, "Prototype:", new_x="END", new_y="TOP")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(50, 100, 180)
    pdf.cell(0, 4, github_url, link=github_url)

    # ── Output ──
    output_path = os.path.join(os.path.dirname(__file__), "challenge_2_response.pdf")
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")
    return output_path


if __name__ == "__main__":
    generate()
