# Architect (Revised)

# 60-Minute Transit Proposal Workflow (Final Version v3.0)

## Major Revisions from V2
- **Removed automated research step** (too brittle for 60-minute deadline)
- **Added critical scope reality checkpoint** at Step 5.5
- **Streamlined final review** from 10 to 5 minutes
- **Simplified tech stack** to manual-friendly tools
- **Strengthened political complexity assessment** in strategic framing

## The Workflow

### Step 1: Transcript Data Extraction (5 minutes, Automated)
**Tool:** Claude API (manual web interface initially)
**Input:** 3 call transcripts pasted into Claude
**Output:** Structured extraction containing:
- Direct client quotes about pain points
- Budget signals and timeline constraints mentioned
- Stakeholder names and concerns raised
- Technical requirements with specificity levels
- Decision urgency indicators (board meetings, deadlines, political pressure)

*Claude prompt: "Extract transit consulting proposal data from these transcripts, focusing on client's exact language about problems and constraints."*

### Step 2: Strategic Framing Decision (5 minutes, Human)
**Tool:** Google Docs template
**Input:** Claude's extraction + your conversation memory
**Critical questions to answer:**
- What's their #1 priority based on emotional emphasis, not just word count?
- What political landmines did they hint at? (community groups, board dynamics, city council pressure)
- Which stakeholder is their biggest threat if we get this wrong?
- What timeline pressure is really driving this? (budget cycles, elections, compliance deadlines)

**Output:** 2-paragraph strategy memo defining real problem and political navigation approach.

*This is your highest-value 5 minutes. AI cannot read subtext about political complexity.*

### Step 3: Proposal Structure Generation (6 minutes, Automated)
**Tool:** Claude API + Google Docs template
**Input:** Strategy memo + transcript extraction
**Output:** Proposal skeleton with:
- Problem statement using their exact quotes
- Scope approach addressing their stated constraints
- Timeline draft accounting for their approval processes
- Pricing framework matching budget signals

*Claude creates first draft; human immediately reviews structure before content generation.*

### Step 4: Content Generation Sprint (18 minutes, Human + AI Hybrid)
**Tools:** Claude API + Google Docs collaborative editing
**Breakdown:**
- Minutes 1-6: Human writes executive summary (requires strategic synthesis)
- Minutes 7-12: AI drafts methodology sections using client data points
- Minutes 13-18: Human edits scope approach and adds conversational callbacks

*Key insight: Executive summary cannot be delegated to AI - it requires reading between lines.*

### Step 5.5: Scope Reality Check (3 minutes, Human) **NEW CRITICAL CHECKPOINT**
**Essential questions:**
- Can we actually deliver this scope in their timeline with our current team capacity?
- Are we promising outcomes we can't control? (ridership increases, stakeholder consensus)
- Does their "simple" request hide complexity they haven't considered?
- Will their 90-day timeline account for their own internal approval bottlenecks?

**Red flags:** Promising "increased ridership," "stakeholder alignment," or "board approval" as deliverables rather than inputs.

*Cost of skipping this: Winning a project that destroys your team or reputation.*

### Step 6: Compliance & Polish (8 minutes, Automated)
**Tool:** Claude API + Grammarly
**Input:** Draft proposal
**Automated checks:**
- Transit terminology consistency
- Client name/project details verified throughout
- Pricing calculations cross-checked
- Professional formatting applied

### Step 7: Final Strategic Review (5 minutes, Human) **STREAMLINED**
**Tool:** Google Docs print preview
**Speed-focused checklist:**
- Does executive summary match their actual top concern?
- Are we solving the problem they emphasized most emotionally?
- Do timeline and price feel proportional to scope?
- Quick scan for obvious errors or overpromising

*Skip the "read as client" exercise for 60-minute turnarounds. Trust your experience to catch fatal flaws quickly.*

### Step 8: Delivery Package (5 minutes, Automated)
**Tools:** Pandoc + Gmail
**Output:** 
- PDF formatted for professional submission
- Email draft referencing specific call moments
- Follow-up calendar scheduling
- Internal project setup checklist (if proposal wins)

## Simplified Tech Stack (V1 Implementation)

**Start immediately with:**
1. **Granola → Claude web interface** (manual paste for reliability)
2. **Google Docs** for all writing and collaboration
3. **Pandoc** for PDF conversion
4. **Manual handoffs** between steps (add automation later where you feel pain)

**Skip initially:** Web scraping, complex API chains, automated research. These add fragility without proportional value in a 60-minute workflow.

## Key Success Factors

**Human judgment preserved** at the two make-or-break moments:
- Step 2: Reading political subtext and real priorities
- Step 5.5: Assessing delivery reality against promises

**Speed enablers:** 
- Claude handles all data extraction and first-draft content
- Human focuses only on strategy and quality gates
- Parallel processing where possible (structure generation while reviewing strategy)

**Quality protection:** 
- Every proposal references specific conversation details
- Political complexity explicitly assessed
- Scope reality check prevents overcommitting

## Total Timing: 55 minutes
*5-minute buffer for unexpected complexity or technical delays*

This workflow transforms conversation insights into winning proposals by combining AI efficiency with human judgment at the exact moments that determine success or failure. The simplified tech stack ensures reliability under pressure, while the strategic checkpoints prevent the costly mistakes that destroy consulting relationships.