# Toolsmith

# Tool Mapping for 60-Minute Transit Proposal Workflow

## Recommended Tech Stack

**Core Foundation (Already in Use):**
- **Claude API** (transcript processing, content generation)
- **Granola** (call recording/transcription source)
- **Zapier** (workflow automation)

**Additional Tools Needed:**
- **Google Docs** (collaborative editing)
- **Pandoc** (document formatting)
- **Python script** (data processing glue)

## Step-by-Step Tool Mapping

### Steps 1-2: Automated Processing (13 minutes total)
**Tools:** Claude API + Python + Zapier
- **Why:** Claude excels at structured data extraction from unstructured text
- **Integration:** Zapier webhook triggers Python script that sends transcripts to Claude API
- **Complexity:** Moderate (requires Python setup for API calls)
- **Solo maintainable:** Yes, basic API integration

### Step 3: Strategic Framing (4 minutes, Human)
**Tools:** Google Docs template
- **Why:** Need human brain, simple document suffices
- **Integration:** Trivial
- **Solo maintainable:** Obviously yes

### Step 4: Proposal Structure Generation (7 minutes)
**Tools:** Claude API + Google Docs API
- **Why:** Claude can populate templates with extracted data points
- **Integration:** Moderate (Google Docs API setup)
- **Solo maintainable:** Yes, after initial setup

### Steps 5-6: Content Generation + Compliance Check (23 minutes)
**Tools:** Claude API + Grammarly + Google Docs
- **Why:** Claude for drafting, human editing in familiar environment
- **Integration:** Trivial (manual handoff to Docs)
- **Solo maintainable:** Yes

### Step 7: Final Review (5 minutes, Human)
**Tools:** Google Docs print preview
- **Why:** Human eyeballs on formatted document
- **Integration:** Trivial
- **Solo maintainable:** Yes

### Step 8: Delivery Prep (3 minutes)
**Tools:** Pandoc + Gmail/Calendly APIs
- **Why:** Pandoc converts Docs to PDF reliably; APIs automate follow-up
- **Integration:** Moderate (API setup)
- **Solo maintainable:** Yes

## V1 Minimum Viable Stack

**Start with this TODAY:**
1. **Granola → Claude (manual)** for transcript processing
2. **Google Docs** for all document work
3. **Manual handoffs** between steps
4. **Pandoc** for final PDF conversion

This gets you 80% of the value with zero complex integrations.

## Integration Risks & Alternatives

**Biggest fragility:** The automated research step (Step 2) is overengineered. Web scraping transit agency sites is brittle and slow. **Skip this initially** - rely on your existing knowledge of the client.

**Alternative for pricing generation:** Simple Google Sheets calculator with client inputs beats AI pricing complexity.

**Reliability priority:** Manual Claude API calls via web interface are more reliable than automated API chains for mission-critical 60-minute turnaround.

## Bottom Line

Your workflow is ambitious but achievable. Start with manual handoffs between Granola, Claude, and Google Docs. Add automation incrementally where you feel pain, not where it seems clever. The human judgment checkpoints are correctly placed - don't automate those away.