# Plan: Align AIA System with DTA Policy v2.0 (December 2025)

## Background & Research Summary

The Australian Government's **Policy for the Responsible Use of AI in Government v2.0** took effect 15 December 2025. It introduces mandatory requirements for all non-corporate Commonwealth entities, with compliance deadlines of **15 June 2026** (first requirements) and **15 December 2026** (full compliance). Existing use cases must be assessed by **30 April 2027**.

### Key Policy Changes Requiring System Updates

The current AIA system implements the older AIA v1.1 template (13 custom dimensions scored 0–5, total 0–65). The new DTA policy introduces:

1. **New 12-Section AI Impact Assessment Tool** — replaces the previous assessment approach with a structured tool aligned to Australia's 8 AI Ethics Principles
2. **Tiered Risk Assessment** — 3-level inherent risk (Low/Medium/High) replacing 4-level score-based categories
3. **Mandatory Register Fields** — specific fields agencies must capture per the DTA standard
4. **Accountable Official (AO) & Accountable Use Case Owner** — new accountability roles
5. **DTA Reporting** — register shared with DTA every 6 months; high-risk use cases reported to DTA
6. **In-Scope Criteria** — formal screening to determine if a use case falls under the policy
7. **Transparency Statement Standard** — aligned to the DTA Standard for AI Transparency Statements
8. **AI Procurement Guidance** — new procurement-specific requirements
9. **Mandatory Staff Training** tracking
10. **Ongoing Monitoring** — minimum 12-month review cycle with re-validation on material change

---

## Gap Analysis: Current System vs. Policy v2.0

| Area | Current State | Required State | Gap |
|------|--------------|----------------|-----|
| **Assessment Structure** | Custom 13 dimensions (0-5 scoring) | DTA 12-section tool (threshold + full assessment) | Major restructure needed |
| **Risk Levels** | 4 levels: Low/Medium/High/Severe (0-65 score) | 3 levels: Low/Medium/High (inherent risk rating) | Update risk model |
| **Register Fields** | system_name, agency, status, risk, scores | Must include: usage pattern, accountable use case owner (name+email), in-scope criteria met, inherent risk rating, residual risk rating, last assessment date | Add mandatory fields |
| **Accountability Roles** | assessor/reviewer/approver | + Accountable Official (AO), Accountable Use Case Owner | Add new roles |
| **In-Scope Screening** | None | Formal screening against Appendix C criteria | New feature needed |
| **DTA Reporting** | None | 6-monthly register export to DTA; high-risk notification | New feature needed |
| **Assessment Workflow** | Linear: Draft → Review → Approved | Tiered: Screening → Threshold (Sections 1-4) → Full Assessment (Sections 5-12) if medium/high | Restructure workflow |
| **Residual Risk** | Not captured | Must track residual risk after mitigations | Add field |
| **Usage Pattern** | Not captured | Required for register and transparency statements | Add field |
| **Procurement** | Basic method + ethical_reqs | Aligned to new AI Procurement Guidance | Enhance |
| **Monitoring** | Basic fields | 12-month minimum review; re-validate on material change; report to governing board/SES | Enhance |
| **Version** | AIA v1.1 | Policy v2.0 / Impact Assessment Tool | Update |

---

## Implementation Plan

### Phase 1: Core Data Model Updates (`aia_core.py`)

#### 1.1 Update Version & Constants
- Change `AIA_VERSION` from `"1.1"` to `"2.0"`
- Add new constants for the DTA's 12-section structure
- Update `RISK_CATEGORIES` from 4-level (Low/Medium/High/Severe) to 3-level (Low/Medium/High)
- Add `USAGE_PATTERNS` constant (e.g., "Decision support", "Direct public interaction", "Internal automation", "Content generation", etc.)
- Add `IN_SCOPE_CRITERIA` constant listing the Appendix C criteria

#### 1.2 Restructure Assessment Sections
Replace the 13-dimension scoring model with the DTA 12-section structure:

**Sections 1–4 (Threshold Assessment — always required):**
- Section 1: Basic Information (use case name, reference ID, AI technology type, usage pattern, roles, scope criteria)
- Section 2: Purpose and Expected Benefits (problem statement, non-AI alternatives, expected benefits, stakeholders)
- Section 3: Inherent Risk Assessment (risk ratings per AI Ethics Principle area using Low/Medium/High + likelihood/consequence)
- Section 4: Threshold Decision (approving officer endorsement if all Low; proceed to full assessment if any Medium/High)

**Sections 5–12 (Full Assessment — only if Medium/High inherent risk):**
- Section 5: Fairness
- Section 6: Reliability and Safety
- Section 7: Privacy and Security
- Section 8: Transparency and Explainability
- Section 9: Contestability
- Section 10: Human Oversight
- Section 11: Accountability
- Section 12: Summary, Mitigations, and Approval

#### 1.3 Add New Fields to AIA Class
```python
# New mandatory register fields
self.usage_pattern = ""                    # Required for register
self.in_scope_criteria = []                # Which Appendix C criteria were met
self.is_in_scope = None                    # True/False/None (not yet determined)
self.inherent_risk_rating = "Not Assessed" # Low/Medium/High
self.residual_risk_rating = "Not Assessed" # Low/Medium/High (post-mitigation)

# Accountability
self.accountable_official = {"name": "", "email": "", "role": ""}
self.accountable_use_case_owner = {"name": "", "email": ""}
self.assessing_officer = {"name": "", "email": "", "role": ""}
self.approving_officer = {"name": "", "email": "", "role": ""}

# Enhanced assessment data
self.ai_technology_type = ""               # e.g., "Machine Learning", "Generative AI", "Rule-based"
self.problem_statement = ""                # What problem the AI solves
self.non_ai_alternatives = ""              # Considered alternatives
self.expected_benefits = ""                # Documented benefits
self.stakeholders = []                     # Affected stakeholders list

# Inherent risk assessment (Section 3)
self.inherent_risks = {
    "fairness": {"rating": "", "likelihood": "", "consequence": "", "justification": ""},
    "reliability_safety": {"rating": "", "likelihood": "", "consequence": "", "justification": ""},
    "privacy_security": {"rating": "", "likelihood": "", "consequence": "", "justification": ""},
    "transparency_explainability": {"rating": "", "likelihood": "", "consequence": "", "justification": ""},
    "contestability": {"rating": "", "likelihood": "", "consequence": "", "justification": ""},
    "human_oversight": {"rating": "", "likelihood": "", "consequence": "", "justification": ""},
    "accountability": {"rating": "", "likelihood": "", "consequence": "", "justification": ""},
}

# Full assessment sections (5-12) - populated only if medium/high risk
self.full_assessment = {
    "fairness": {"assessment": "", "mitigations": ""},
    "reliability_safety": {"assessment": "", "mitigations": ""},
    "privacy_security": {"assessment": "", "mitigations": ""},
    "transparency_explainability": {"assessment": "", "mitigations": ""},
    "contestability": {"assessment": "", "mitigations": ""},
    "human_oversight": {"assessment": "", "mitigations": ""},
    "accountability": {"assessment": "", "mitigations": ""},
}

# Threshold decision
self.threshold_decision = {
    "requires_full_assessment": None,  # True/False
    "endorsed_by": "",
    "endorsement_date": "",
    "rationale": ""
}

# DTA reporting
self.dta_notified = False                  # For high-risk use cases
self.dta_notification_date = ""
self.last_assessment_date = ""             # When impact assessment was last updated
```

#### 1.4 Preserve Backwards Compatibility
- Keep the old 13-dimension data structure readable for migration
- Add a `policy_version` field to distinguish v1.1 and v2.0 assessments
- Add a migration method to map old dimension scores to new structure where possible

---

### Phase 2: Database Schema Updates (`db_manager.py`)

#### 2.1 Add New Columns
```sql
ALTER TABLE ai_systems ADD COLUMN usage_pattern TEXT DEFAULT '';
ALTER TABLE ai_systems ADD COLUMN inherent_risk_rating TEXT DEFAULT 'Not Assessed';
ALTER TABLE ai_systems ADD COLUMN residual_risk_rating TEXT DEFAULT 'Not Assessed';
ALTER TABLE ai_systems ADD COLUMN is_in_scope INTEGER DEFAULT NULL;
ALTER TABLE ai_systems ADD COLUMN accountable_owner_name TEXT DEFAULT '';
ALTER TABLE ai_systems ADD COLUMN accountable_owner_email TEXT DEFAULT '';
ALTER TABLE ai_systems ADD COLUMN policy_version TEXT DEFAULT '2.0';
ALTER TABLE ai_systems ADD COLUMN last_assessment_date TEXT DEFAULT '';
ALTER TABLE ai_systems ADD COLUMN dta_notified INTEGER DEFAULT 0;
```

#### 2.2 Add Migration Function
- Detect existing v1.1 records and add default values for new fields
- Map old `risk_category` (4-level) to new `inherent_risk_rating` (3-level): Severe → High

#### 2.3 Update CRUD Operations
- Update `add_system()` to accept new mandatory fields
- Update `get_system_list()` to include new columns
- Update `update_aia()` to persist new fields
- Add `get_dta_export()` function for 6-monthly DTA register sharing
- Add `get_high_risk_systems()` for DTA notification tracking
- Update `get_dashboard_data()` for new risk model

---

### Phase 3: UI Updates (`app.py`)

#### 3.1 New: In-Scope Screening View
- Add a screening step when registering a new AI use case
- Present the Appendix C in-scope criteria as a checklist
- Auto-determine if the use case is in scope
- If not in scope, record the screening result and stop (no full assessment needed)

#### 3.2 Restructure Assessment Editor
Replace the current multi-tab editor (Metadata, System Description, Impact Assessment, Scoring, Mitigation, Approval, Monitoring, Report) with the new 12-section structure:

**Tab layout:**
1. **Basic Info** (Section 1) — Use case name, reference ID, AI technology type, usage pattern, accountable owner, scope criteria
2. **Purpose & Benefits** (Section 2) — Problem statement, non-AI alternatives, expected benefits, stakeholder mapping
3. **Inherent Risk** (Section 3) — Risk ratings per principle area with likelihood × consequence matrix
4. **Threshold Decision** (Section 4) — Summary of inherent risks; endorsement for low-risk; gate to full assessment
5. **Full Assessment** (Sections 5–11, shown only if medium/high) — Tabbed sub-sections for each principle area
6. **Summary & Approval** (Section 12) — Mitigations summary, residual risk, approvals, monitoring plan
7. **Report** — Full generated report

#### 3.3 Update Dashboard
- Replace "Severe" risk category with updated 3-level model
- Add charts for: inherent vs residual risk, in-scope vs out-of-scope, DTA reporting status
- Add compliance timeline indicators (June 2026, December 2026 deadlines)
- Add "Accountable Official" overview

#### 3.4 Add DTA Export Feature
- Button to generate the register export in the format required by DTA
- Include all mandatory fields: usage pattern, accountable use case owner, in-scope criteria, inherent risk rating, residual risk rating, last assessment date
- Export as CSV/Excel for sharing

#### 3.5 Update Register View
- Add new columns: Usage Pattern, Inherent Risk, Residual Risk, Accountable Owner, In-Scope
- Add filter for in-scope status
- Add indicator for DTA notification status on high-risk items

#### 3.6 Add High-Risk DTA Notification Workflow
- When a use case is rated high inherent risk, prompt to notify DTA
- Track notification status and date
- Alert when an existing use case changes to/from high risk

---

### Phase 4: Role & Permission Updates (`auth_manager.py`)

#### 4.1 Add Accountability Roles
- Add "accountable_official" role/permission tier
- Add "use_case_owner" designation (can be assigned per use case, not just per user)
- Update permission matrix for new workflow (screening → threshold → full assessment → approval)

#### 4.2 Update Approval Workflow
- Low risk: Approving officer endorsement sufficient
- Medium risk: Should be governed through designated board or senior executive
- High risk: Must report to AO; must be governed through designated board or senior executive; must notify DTA

---

### Phase 5: Reporting & Compliance

#### 5.1 Update Report Generator
- Align generated report with DTA 12-section structure
- Include inherent and residual risk ratings
- Include accountability chain
- Include in-scope determination rationale

#### 5.2 Add Compliance Dashboard
- Track agency readiness against June/December 2026 milestones
- Show: systems screened, systems assessed, systems with accountable owners
- Highlight overdue reviews (>12 months since last assessment)
- Track DTA reporting schedule (next 6-monthly submission)

#### 5.3 Update Example Data (`populate_db.py`)
- Update example AIAs to use new v2.0 structure
- Include examples at each risk level (Low threshold-only, Medium full assessment, High with DTA notification)

---

## Implementation Priority

| Priority | Phase | Rationale |
|----------|-------|-----------|
| **P0 — Critical** | Phase 1 (Core Model) | Foundation for all other changes |
| **P0 — Critical** | Phase 2 (Database) | Required for data persistence |
| **P1 — High** | Phase 3.1–3.2 (Screening + Assessment Editor) | Core user workflow |
| **P1 — High** | Phase 3.5 (Register View) | Mandatory register fields |
| **P2 — Medium** | Phase 3.3–3.4 (Dashboard + DTA Export) | Reporting/compliance |
| **P2 — Medium** | Phase 4 (Roles) | Governance workflow |
| **P3 — Lower** | Phase 5 (Reports + Compliance Dashboard) | Polish and monitoring |

---

## Sources

- [Policy for the responsible use of AI in government v2.0](https://www.digital.gov.au/policy/ai/policy)
- [DTA AI Policy Update](https://www.dta.gov.au/articles/ai-policy-update-strengthening-responsible-use-across-government)
- [AI Impact Assessment Tool](https://www.digital.gov.au/ai/impact-assessment-tool)
- [AI Impact Assessment Tool: Introduction](https://www.digital.gov.au/ai/impact-assessment-tool/introduction)
- [Standard for Accountability](https://www.digital.gov.au/ai/ai-in-government-policy/accountability)
- [AI Use Case Impact Assessment Policy](https://www.digital.gov.au/ai/ai-in-government-policy/ai-use-case-impact-assessment)
- [Preparedness and Operations](https://www.digital.gov.au/ai/ai-in-government-policy/preparedness-and-operations)
- [Appendices: In-Scope Criteria & Definitions](https://www.digital.gov.au/ai/ai-in-government-policy/appendices)
- [Guidance for AI Adoption (NAIC)](https://www.industry.gov.au/publications/guidance-for-ai-adoption)
- [AI Register Template v1.0](https://www.industry.gov.au/sites/default/files/2025-10/ai_register_template.pdf)
- [APSC Transparent Use of AI](https://www.apsc.gov.au/about-us/accountability-and-reporting/transparent-use-ai-commission)
- [AI Regulatory Horizon Tracker - Australia](https://www.twobirds.com/en/capabilities/artificial-intelligence/ai-legal-services/ai-regulatory-horizon-tracker/australia)
- [IAPP Global AI Governance: Australia](https://iapp.org/resources/article/global-ai-governance-australia)
