# Toolsmith

## Toolsmith Analysis: 60-Minute Transit Proposal Workflow

Looking at these transcripts, Patricia needs a proposal that proves you understand her data fragmentation nightmare, political landmines, and sustainability requirements. Here's the practical tool mapping:

### **Core Tech Stack**

**Primary Engine**: OpenAI API (GPT-4) with custom prompts
- **Why**: Best context retention across 3 long transcripts, excellent at extracting client-specific language
- **Integration**: Trivial - direct API calls
- **Solo maintainable**: Yes, basic Python scripting

**Document Assembly**: Google Docs API + Python
- **Why**: Patricia expects professional formatting, collaborative review with David
- **Alternative considered**: Notion API, but transit agencies are usually Google/Office shops
- **Integration**: Moderate - template management, formatting control
- **Solo maintainable**: Yes with templates

### **Phase-by-Phase Tool Mapping**

**Phase 1 (Context Extraction): Claude/GPT-4 API + Custom Prompts**
- Tool: Direct API calls with conversation-specific prompts
- Why: Need to catch political nuances like "heated public meeting" and technical details like "Trapeze contract"
- Complexity: Trivial - structured prompts return JSON
- Human checkpoint: Review extracted pain points for accuracy

**Phase 2 (Solution Mapping): GPT-4 + Transit Industry Knowledge Base**
- Tool: RAG implementation using Pinecone API for transit case studies
- Why: Patricia specifically asked for "similar-sized agencies" examples
- Complexity: Moderate - vector embeddings for case study matching
- Alternative: Simple JSON file of case studies (simpler for v1)

**Phase 3 (Credibility): Airtable API for Case Study Database**
- Tool: Airtable base with transit projects, filtered by agency size/scope
- Why: Need to quickly pull "three agencies in Ontario, 50-100 bus range" examples
- Complexity: Trivial - basic API queries
- Solo maintainable: Yes, visual interface for adding cases

**Phase 4 (Assembly): Google Docs API + Jinja2 Templates**
- Tool: Python script populating Google Docs templates
- Why: Patricia needs to "review with David" - collaborative editing essential
- Complexity: Moderate - template management, variable substitution
- Alternative: Pandoc for PDF generation (but loses collaboration)

**Phase 5 (QC): Grammarly API + Human Review**
- Tool: Automated grammar/tone checking before human review
- Why: Public sector expects polished documents
- Complexity: Trivial - API call for text improvement
- Solo maintainable: Yes

### **Critical Human Judgment Tools**

**Political Risk Assessment**: Custom scoring rubric in spreadsheet
- Manual process: Review transcript for political sensitivity markers
- Tools: Simple checklist in Google Sheets
- Why: AI misses subtext like Patricia's defensive position on Route 7

**Technical Calibration**: Skills assessment matrix
- Manual process: Map client technical statements to realistic complexity levels
- Tools: Decision tree in Notion or simple flowchart
- Why: David's "basic Python" needs human interpretation

### **V1 Minimum Viable Stack (Today)**

1. **OpenAI API** ($20/month) - core content generation
2. **Google Docs API** (free) - document assembly and collaboration  
3. **Python + Jinja2** (free) - template processing
4. **Google Sheets** (free) - case study database and QC checklists
5. **Zapier** ($20/month) - connect APIs without heavy coding

**Total monthly cost**: ~$40
**Setup time**: 2-3 days for basic templates and prompts
**Maintenance**: Solo manageable with basic Python skills

### **Integration Complexity Assessment**

**Trivial** (< 1 hour setup):
- OpenAI API calls for content generation
- Google Docs API for document creation
- Simple prompt engineering

**Moderate** (1-2 days setup):
- Template system with variable substitution  
- Case study database with filtering
- Quality control workflows

**Complex** (avoid for v1):
- Full RAG implementation for case studies
- Advanced NLP for political sentiment analysis
- Custom CRM integration

### **Solo Founder Sustainability**

**Maintainable solo**:
- Prompt libraries in text files
- Google Docs templates
- Simple Python scripts
- Airtable/Sheets databases

**Requires ongoing support**:
- Complex prompt chaining
- Advanced API error handling
- Real-time collaboration features

### **Why This Stack Over Alternatives**

**Chose Google Docs API over Notion**: Transit agencies are conservative, Google integration is safer bet

**Chose Airtable over custom database**: Visual interface for case study management, API access for automation

**Chose OpenAI over Claude for main engine**: Better at maintaining context across long transcripts, more reliable for structured output

**Chose Zapier over pure Python**: Faster setup for API connections, visual workflow for non-technical maintenance

This stack gets Patricia her tailored proposal in 60 minutes while proving you understand her technical constraints, political dynamics, and sustainability requirements. The tools match her organization's likely tech comfort zone and your need to maintain this solo.