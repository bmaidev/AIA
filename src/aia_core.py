# aia_core.py
# Core logic for the AI Impact Assessment object
# Aligned with DTA Policy for the Responsible Use of AI in Government v2.0 (Dec 2025)

import json
import datetime
import uuid

# --- Constants aligned to DTA Policy v2.0 ---

POLICY_VERSION = "2.0"

# Australia's 8 AI Ethics Principles
AI_ETHICS_PRINCIPLES = [
    "Human, societal and environmental wellbeing",
    "Human-centred values",
    "Fairness",
    "Privacy protection and security",
    "Reliability and safety",
    "Transparency and explainability",
    "Contestability",
    "Accountability",
]

# Inherent risk areas aligned to the DTA Impact Assessment Tool (Section 3)
INHERENT_RISK_AREAS = [
    "Fairness",
    "Reliability and Safety",
    "Privacy and Security",
    "Transparency and Explainability",
    "Contestability",
    "Human Oversight",
    "Accountability",
]

# Risk ratings for the 3-level model
RISK_RATINGS = ["Low", "Medium", "High"]

# Likelihood and consequence scales for inherent risk assessment
LIKELIHOOD_LEVELS = ["Rare", "Unlikely", "Possible", "Likely", "Almost Certain"]
CONSEQUENCE_LEVELS = ["Insignificant", "Minor", "Moderate", "Major", "Severe"]

# Risk matrix: likelihood x consequence -> rating
RISK_MATRIX = {
    ("Rare", "Insignificant"): "Low", ("Rare", "Minor"): "Low", ("Rare", "Moderate"): "Low",
    ("Rare", "Major"): "Medium", ("Rare", "Severe"): "Medium",
    ("Unlikely", "Insignificant"): "Low", ("Unlikely", "Minor"): "Low", ("Unlikely", "Moderate"): "Medium",
    ("Unlikely", "Major"): "Medium", ("Unlikely", "Severe"): "High",
    ("Possible", "Insignificant"): "Low", ("Possible", "Minor"): "Medium", ("Possible", "Moderate"): "Medium",
    ("Possible", "Major"): "High", ("Possible", "Severe"): "High",
    ("Likely", "Insignificant"): "Medium", ("Likely", "Minor"): "Medium", ("Likely", "Moderate"): "High",
    ("Likely", "Major"): "High", ("Likely", "Severe"): "High",
    ("Almost Certain", "Insignificant"): "Medium", ("Almost Certain", "Minor"): "Medium",
    ("Almost Certain", "Moderate"): "High", ("Almost Certain", "Major"): "High",
    ("Almost Certain", "Severe"): "High",
}

# In-scope criteria from Appendix C of Policy v2.0
IN_SCOPE_CRITERIA = [
    "The AI use case involves or supports a decision, recommendation, or prediction that affects individuals or entities",
    "The AI use case processes personal information or sensitive data",
    "The AI use case automates or augments a function previously performed by a person",
    "The AI use case has a public-facing component or directly interacts with external users",
    "The AI use case involves generative AI that produces content for external use",
    "The AI use case is used in a regulatory, compliance, or enforcement context",
    "The AI use case influences resource allocation, service delivery, or access to government services",
]

# Usage pattern categories
USAGE_PATTERNS = [
    "Decision support/recommendation",
    "Fully automated decision-making",
    "Information provision",
    "Content generation",
    "Data analysis and insights",
    "Process automation",
    "Monitoring and surveillance",
    "Customer/citizen interaction",
    "Internal operational tool",
    "Research and experimentation",
]

# AI technology types
AI_TECHNOLOGY_TYPES = [
    "Machine Learning (Supervised)",
    "Machine Learning (Unsupervised)",
    "Deep Learning / Neural Networks",
    "Natural Language Processing (NLP)",
    "Generative AI / Large Language Model",
    "Computer Vision",
    "Robotic Process Automation (RPA) with AI",
    "Rule-based / Expert System",
    "Reinforcement Learning",
    "Ensemble / Hybrid",
    "Other",
]

# Required governance actions by risk level (DTA Policy v2.0)
RISK_ACTIONS = {
    "Low": "Approving officer endorsement sufficient. Standard monitoring and evaluation. Document assessment. Proceed with use case.",
    "Medium": "Should be governed through a designated board or senior executive. Enhanced monitoring. Documented mitigation plan required.",
    "High": "Must report to agency Accountable Official. Must be governed through a designated board or senior executive. Must notify DTA. Comprehensive mitigation plan with strict oversight required.",
}

# --- Legacy v1.1 constants (kept for migration) ---
LEGACY_DIMENSIONS = [
    "Human Impact", "Contestability and Redress", "Explainability and Interpretability",
    "Bias and Fairness", "Privacy Risk", "Data Representativeness",
    "Autonomy and Oversight", "Accountability and Auditability", "Security and Resilience",
    "Monitoring and Drift", "Ethical Considerations", "Legal Compliance", "Robustness and Reliability",
]

LEGACY_RISK_CATEGORIES = [
    {"range": (0, 10), "category": "Low"},
    {"range": (11, 25), "category": "Medium"},
    {"range": (26, 40), "category": "High"},
    {"range": (41, 65), "category": "High"},  # Severe maps to High in v2.0
]


# --- AIA Class Definition (Policy v2.0) ---

class AlgorithmicImpactAssessment:
    """Represents a single AI Use Case Impact Assessment aligned to DTA Policy v2.0."""

    def __init__(self, system_name="[Use Case Name]", agency_name="[Agency Name]"):
        """Initializes a new AI Impact Assessment instance."""
        self.policy_version = POLICY_VERSION

        # === SECTION 1: Basic Information ===
        self.system_name = system_name
        self.agency_name = agency_name
        self.reference_id = ""  # Unique reference identifier for this assessment
        self.ai_technology_type = ""  # From AI_TECHNOLOGY_TYPES
        self.usage_pattern = ""  # From USAGE_PATTERNS
        self.use_case_description = ""  # Plain language description of how AI is used

        # Accountability roles (DTA Policy v2.0 mandatory)
        self.accountable_use_case_owner = {"name": "", "email": "", "position": ""}
        self.assessing_officer = {"name": "", "email": "", "position": ""}
        self.approving_officer = {"name": "", "email": "", "position": ""}
        self.accountable_official = {"name": "", "email": "", "position": ""}  # Agency-level AO

        # In-scope determination
        self.in_scope_criteria_met = []  # List of criteria indices that were met
        self.is_in_scope = None  # True/False/None (not yet determined)
        self.scope_determination_rationale = ""

        # === SECTION 2: Purpose and Expected Benefits ===
        self.system_purpose = ""  # Detailed purpose
        self.problem_statement = ""  # What problem does this solve
        self.non_ai_alternatives = ""  # Alternatives considered
        self.expected_benefits = ""  # Documented expected benefits
        self.stakeholders = []  # List of {"name": "", "impact": "positive/negative/both", "description": ""}

        # === SECTION 3: Inherent Risk Assessment ===
        self.inherent_risks = {
            area: {
                "likelihood": "",
                "consequence": "",
                "rating": "",  # Low/Medium/High (auto-calculated from matrix)
                "justification": "",
            }
            for area in INHERENT_RISK_AREAS
        }
        self.inherent_risk_rating = "Not Assessed"  # Overall: highest of individual ratings

        # === SECTION 4: Threshold Decision ===
        self.threshold_decision = {
            "requires_full_assessment": None,  # True/False
            "endorsed_by": "",
            "endorsement_date": "",
            "rationale": "",
        }

        # === SECTIONS 5-11: Full Assessment (only if Medium/High inherent risk) ===
        self.full_assessment = {
            area: {
                "assessment": "",  # Detailed assessment text
                "controls": "",  # Existing controls/measures
                "mitigations": "",  # Proposed additional mitigations
                "residual_risk": "",  # Low/Medium/High after mitigations
            }
            for area in INHERENT_RISK_AREAS
        }

        # === SECTION 12: Summary, Mitigations & Approval ===
        self.residual_risk_rating = "Not Assessed"  # Overall residual risk after mitigations

        # Mitigation Plan
        self.mitigation_plan = []  # List of mitigation items

        # Approval workflow
        self.approvals = {
            "assessing_officer": {"name": "", "position": "", "date": "", "signature": ""},
            "approving_officer": {"name": "", "position": "", "date": "", "decision": "", "conditions": ""},
            "accountable_official": {"name": "", "position": "", "date": "", "decision": "", "conditions": ""},
        }

        # Monitoring and review
        self.monitoring_plan_ref = ""
        self.review_frequency = "Every 12 months"  # DTA minimum requirement
        self.next_review_date = ""
        self.last_assessment_date = ""

        # Links and references
        self.ai_inventory_ref = ""
        self.transparency_statement_link = ""
        self.referenced_frameworks = ""

        # DTA reporting (high-risk use cases)
        self.dta_notified = False
        self.dta_notification_date = ""

        # === System Description (retained from v1.1, now part of Sections 1-2) ===
        self.technical_specs = {
            "model_type": "", "algorithms": "", "language_libs": "", "hardware_infra": ""
        }
        self.data_details = {
            "sources": "", "volume_velocity": "", "types": "", "retention_policy": ""
        }
        self.deployment_context = {
            "operational_env": "", "target_users_affected": "", "decision_authority": ""
        }
        self.procurement = {
            "method": "", "ethical_reqs": ""
        }
        self.related_assessments = {
            "pia_ref": "", "other_assessments": ""
        }

        # === Register Tracking ===
        self.system_id = None
        self.aia_status = "Draft"  # Draft, Screening, Threshold, Full Assessment, Review, Approved, Archived
        self.related_assessment_statuses = {
            "PIA": "Not Started",
            "Security Assessment": "Not Started",
            "Human Rights Assessment": "Not Started",
        }
        self.creation_date = datetime.datetime.now().isoformat()
        self.last_modified_date = datetime.datetime.now().isoformat()

        # === Legacy v1.1 data (for migration support) ===
        self.dimensions = {}  # Populated only when loading v1.1 data
        self.total_score = 0  # Legacy score
        self.risk_category = {"category": "Low", "action": ""}  # Legacy risk category

    # --- Section 1: Basic Information Methods ---

    def set_basic_info(self, **kwargs):
        """Sets basic information fields."""
        for key in ['system_name', 'agency_name', 'reference_id', 'ai_technology_type',
                     'usage_pattern', 'use_case_description']:
            if key in kwargs:
                setattr(self, key, kwargs[key])
        for key in ['accountable_use_case_owner', 'assessing_officer', 'approving_officer',
                     'accountable_official']:
            if key in kwargs and isinstance(kwargs[key], dict):
                getattr(self, key).update(kwargs[key])
        self.last_modified_date = datetime.datetime.now().isoformat()

    def set_scope_determination(self, criteria_met, is_in_scope, rationale=""):
        """Sets the in-scope determination for this use case."""
        self.in_scope_criteria_met = criteria_met
        self.is_in_scope = is_in_scope
        self.scope_determination_rationale = rationale
        self.last_modified_date = datetime.datetime.now().isoformat()

    # --- Section 2: Purpose and Benefits Methods ---

    def set_purpose_and_benefits(self, purpose="", problem_statement="", non_ai_alternatives="",
                                  expected_benefits="", stakeholders=None):
        """Sets purpose and expected benefits."""
        if purpose: self.system_purpose = purpose
        if problem_statement: self.problem_statement = problem_statement
        if non_ai_alternatives: self.non_ai_alternatives = non_ai_alternatives
        if expected_benefits: self.expected_benefits = expected_benefits
        if stakeholders is not None: self.stakeholders = stakeholders
        self.last_modified_date = datetime.datetime.now().isoformat()

    # --- Section 3: Inherent Risk Assessment Methods ---

    def set_inherent_risk(self, risk_area, likelihood="", consequence="", justification=""):
        """Sets the inherent risk for a specific risk area."""
        if risk_area not in self.inherent_risks:
            raise ValueError(f"Invalid risk area: {risk_area}. Must be one of: {INHERENT_RISK_AREAS}")
        if likelihood and likelihood not in LIKELIHOOD_LEVELS:
            raise ValueError(f"Invalid likelihood: {likelihood}. Must be one of: {LIKELIHOOD_LEVELS}")
        if consequence and consequence not in CONSEQUENCE_LEVELS:
            raise ValueError(f"Invalid consequence: {consequence}. Must be one of: {CONSEQUENCE_LEVELS}")

        risk = self.inherent_risks[risk_area]
        if likelihood: risk["likelihood"] = likelihood
        if consequence: risk["consequence"] = consequence
        if justification: risk["justification"] = justification

        # Auto-calculate rating from matrix
        if risk["likelihood"] and risk["consequence"]:
            risk["rating"] = RISK_MATRIX.get(
                (risk["likelihood"], risk["consequence"]), ""
            )

        self._update_overall_inherent_risk()
        self.last_modified_date = datetime.datetime.now().isoformat()

    def _update_overall_inherent_risk(self):
        """Calculates the overall inherent risk as the highest individual rating."""
        ratings = [r["rating"] for r in self.inherent_risks.values() if r["rating"]]
        if not ratings:
            self.inherent_risk_rating = "Not Assessed"
            return

        priority = {"High": 3, "Medium": 2, "Low": 1}
        max_rating = max(ratings, key=lambda r: priority.get(r, 0))
        self.inherent_risk_rating = max_rating

        # Auto-set threshold decision
        if all(r == "Low" for r in ratings):
            self.threshold_decision["requires_full_assessment"] = False
        elif any(r in ("Medium", "High") for r in ratings):
            self.threshold_decision["requires_full_assessment"] = True

    # --- Section 4: Threshold Decision Methods ---

    def set_threshold_decision(self, endorsed_by="", endorsement_date="", rationale=""):
        """Sets the threshold decision (for low-risk use cases)."""
        self.threshold_decision["endorsed_by"] = endorsed_by
        self.threshold_decision["endorsement_date"] = endorsement_date
        self.threshold_decision["rationale"] = rationale
        self.last_modified_date = datetime.datetime.now().isoformat()

    # --- Sections 5-11: Full Assessment Methods ---

    def set_full_assessment(self, risk_area, assessment="", controls="", mitigations="",
                            residual_risk=""):
        """Sets the full assessment for a specific risk area."""
        if risk_area not in self.full_assessment:
            raise ValueError(f"Invalid risk area: {risk_area}. Must be one of: {INHERENT_RISK_AREAS}")
        if residual_risk and residual_risk not in RISK_RATINGS:
            raise ValueError(f"Invalid residual risk: {residual_risk}. Must be one of: {RISK_RATINGS}")

        fa = self.full_assessment[risk_area]
        if assessment: fa["assessment"] = assessment
        if controls: fa["controls"] = controls
        if mitigations: fa["mitigations"] = mitigations
        if residual_risk: fa["residual_risk"] = residual_risk

        self._update_overall_residual_risk()
        self.last_modified_date = datetime.datetime.now().isoformat()

    def _update_overall_residual_risk(self):
        """Calculates overall residual risk as the highest individual residual risk."""
        residuals = [fa["residual_risk"] for fa in self.full_assessment.values() if fa["residual_risk"]]
        if not residuals:
            self.residual_risk_rating = "Not Assessed"
            return

        priority = {"High": 3, "Medium": 2, "Low": 1}
        self.residual_risk_rating = max(residuals, key=lambda r: priority.get(r, 0))

    # --- Section 12: Mitigation Plan Methods ---

    def add_mitigation_item(self, risk_area, risk_description, action, responsible,
                            target_date, status="Planned"):
        """Adds an item to the mitigation plan."""
        item = {
            "id": str(uuid.uuid4()),
            "risk_area": risk_area,
            "risk_description": risk_description,
            "action": action,
            "responsible": responsible,
            "target_date": target_date,
            "status": status,
        }
        self.mitigation_plan.append(item)
        self.last_modified_date = datetime.datetime.now().isoformat()
        return item['id']

    def update_mitigation_item(self, item_id, **updates):
        """Updates fields of an existing mitigation item by its ID."""
        for item in self.mitigation_plan:
            if item['id'] == item_id:
                item.update(updates)
                self.last_modified_date = datetime.datetime.now().isoformat()
                return True
        raise ValueError(f"Mitigation item with ID {item_id} not found.")

    def remove_mitigation_item(self, item_id):
        """Removes a mitigation item by its ID."""
        initial_len = len(self.mitigation_plan)
        self.mitigation_plan = [item for item in self.mitigation_plan if item['id'] != item_id]
        if len(self.mitigation_plan) == initial_len:
            raise ValueError(f"Mitigation item with ID {item_id} not found.")
        self.last_modified_date = datetime.datetime.now().isoformat()
        return True

    # --- Approval and Monitoring Methods ---

    def set_approval(self, assessing_officer=None, approving_officer=None, accountable_official=None):
        """Sets approval details."""
        if assessing_officer:
            self.approvals['assessing_officer'].update(assessing_officer)
        if approving_officer:
            self.approvals['approving_officer'].update(approving_officer)
        if accountable_official:
            self.approvals['accountable_official'].update(accountable_official)
        self.last_modified_date = datetime.datetime.now().isoformat()

    def set_links(self, inventory_ref="", transparency_link=""):
        """Sets AI inventory and transparency statement links."""
        if inventory_ref is not None: self.ai_inventory_ref = inventory_ref
        if transparency_link is not None: self.transparency_statement_link = transparency_link
        self.last_modified_date = datetime.datetime.now().isoformat()

    def set_monitoring(self, plan_ref="", frequency="", next_date=""):
        """Sets monitoring details."""
        if plan_ref is not None: self.monitoring_plan_ref = plan_ref
        if frequency is not None: self.review_frequency = frequency
        if next_date is not None: self.next_review_date = next_date
        self.last_modified_date = datetime.datetime.now().isoformat()

    # --- System Description Methods (retained) ---

    def set_system_details(self, system_name="", agency_name="", purpose="", tech_specs=None,
                           data_details=None, deployment_context=None, procurement=None,
                           related_assessments=None):
        """Updates system description sections."""
        if system_name: self.system_name = system_name
        if agency_name: self.agency_name = agency_name
        if purpose: self.system_purpose = purpose
        if tech_specs: self.technical_specs.update(tech_specs)
        if data_details: self.data_details.update(data_details)
        if deployment_context: self.deployment_context.update(deployment_context)
        if procurement: self.procurement.update(procurement)
        if related_assessments:
            if 'pia_ref' in related_assessments:
                self.related_assessments['pia_ref'] = related_assessments['pia_ref']
            if 'other_assessments' in related_assessments:
                self.related_assessments['other_assessments'] = related_assessments['other_assessments']
        self.last_modified_date = datetime.datetime.now().isoformat()

    # --- Status Methods ---

    def set_aia_status(self, status):
        """Sets the overall AIA status."""
        allowed_statuses = ["Draft", "Screening", "Threshold", "Full Assessment",
                           "Review", "Approved", "Archived"]
        if status not in allowed_statuses:
            raise ValueError(f"Invalid AIA status. Must be one of: {allowed_statuses}")
        self.aia_status = status
        self.last_modified_date = datetime.datetime.now().isoformat()

    def set_related_assessment_status(self, assessment_name, status):
        """Sets the status for a specific related assessment."""
        allowed_statuses = ["Not Started", "In Progress", "Completed", "N/A"]
        if status not in allowed_statuses:
            raise ValueError(f"Invalid status for {assessment_name}. Must be one of: {allowed_statuses}")
        self.related_assessment_statuses[assessment_name] = status
        self.last_modified_date = datetime.datetime.now().isoformat()

    # --- DTA Notification ---

    def set_dta_notification(self, notified=True, notification_date=""):
        """Records DTA notification for high-risk use cases."""
        self.dta_notified = notified
        self.dta_notification_date = notification_date or datetime.date.today().isoformat()
        self.last_modified_date = datetime.datetime.now().isoformat()

    # --- Legacy compatibility ---

    def _update_risk_assessment(self):
        """Updates risk assessment. For v2.0 this recalculates inherent and residual risk."""
        self._update_overall_inherent_risk()
        self._update_overall_residual_risk()
        # Update legacy fields for DB compatibility
        self.risk_category = {
            "category": self.inherent_risk_rating if self.inherent_risk_rating != "Not Assessed" else "Low",
            "action": RISK_ACTIONS.get(self.inherent_risk_rating, ""),
        }

    def set_dimension_score(self, dimension_name, score, justification=""):
        """Legacy method: Sets score for a v1.1 dimension. Kept for migration compatibility."""
        if not self.dimensions:
            self.dimensions = {dim: {"score": 0, "justification": ""} for dim in LEGACY_DIMENSIONS}
        if dimension_name not in self.dimensions:
            raise ValueError(f"Invalid dimension name: {dimension_name}")
        if not isinstance(score, int) or not (0 <= score <= 5):
            raise ValueError(f"Score for {dimension_name} must be an integer between 0 and 5.")
        self.dimensions[dimension_name]["score"] = score
        self.dimensions[dimension_name]["justification"] = justification
        self.total_score = sum(dim["score"] for dim in self.dimensions.values())
        self.last_modified_date = datetime.datetime.now().isoformat()

    # --- Report Generation ---

    def generate_report(self):
        """Generates a formatted string report based on the DTA v2.0 structure."""
        self._update_risk_assessment()

        report = f"""# AI Use Case Impact Assessment Report

**Use Case Name:** {self.system_name} (ID: {self.system_id or 'N/A'})
**Agency:** {self.agency_name}
**Policy Version:** {self.policy_version}
**Assessment Status:** {self.aia_status}
**Reference ID:** {self.reference_id or '[Not Set]'}
**Last Modified:** {self.last_modified_date}

---

## Section 1: Basic Information

* **Use Case Name:** {self.system_name}
* **Agency/Department:** {self.agency_name}
* **AI Technology Type:** {self.ai_technology_type or '[Not Set]'}
* **Usage Pattern:** {self.usage_pattern or '[Not Set]'}
* **Use Case Description:** {self.use_case_description or '[Not Set]'}

### Accountability
* **Accountable Use Case Owner:** {self.accountable_use_case_owner.get('name', '[Not Set]')} ({self.accountable_use_case_owner.get('email', '')})
* **Assessing Officer:** {self.assessing_officer.get('name', '[Not Set]')} ({self.assessing_officer.get('email', '')})
* **Approving Officer:** {self.approving_officer.get('name', '[Not Set]')} ({self.approving_officer.get('email', '')})
* **Accountable Official:** {self.accountable_official.get('name', '[Not Set]')} ({self.accountable_official.get('email', '')})

### In-Scope Determination
* **In Scope:** {'Yes' if self.is_in_scope else 'No' if self.is_in_scope is False else 'Not Yet Determined'}
* **Criteria Met:** {', '.join(str(i+1) for i in self.in_scope_criteria_met) if self.in_scope_criteria_met else 'None'}
* **Rationale:** {self.scope_determination_rationale or '[Not Set]'}

---

## Section 2: Purpose and Expected Benefits

* **Purpose:** {self.system_purpose or '[Not Set]'}
* **Problem Statement:** {self.problem_statement or '[Not Set]'}
* **Non-AI Alternatives Considered:** {self.non_ai_alternatives or '[Not Set]'}
* **Expected Benefits:** {self.expected_benefits or '[Not Set]'}

### Stakeholders
"""
        if self.stakeholders:
            for s in self.stakeholders:
                report += f"* {s.get('name', 'Unknown')} — Impact: {s.get('impact', 'N/A')} — {s.get('description', '')}\n"
        else:
            report += "* [No stakeholders identified]\n"

        report += f"""
---

## Section 3: Inherent Risk Assessment

| Risk Area | Likelihood | Consequence | Rating | Justification |
| :--- | :--- | :--- | :--- | :--- |
"""
        for area in INHERENT_RISK_AREAS:
            r = self.inherent_risks[area]
            report += f"| {area} | {r['likelihood'] or '-'} | {r['consequence'] or '-'} | **{r['rating'] or '-'}** | {r['justification'] or '-'} |\n"

        report += f"""
**Overall Inherent Risk Rating:** **{self.inherent_risk_rating}**
**Required Action:** {RISK_ACTIONS.get(self.inherent_risk_rating, 'N/A')}

---

## Section 4: Threshold Decision

* **Requires Full Assessment:** {'Yes' if self.threshold_decision['requires_full_assessment'] else 'No' if self.threshold_decision['requires_full_assessment'] is False else 'Not Yet Determined'}
* **Endorsed By:** {self.threshold_decision['endorsed_by'] or '[Not Set]'}
* **Endorsement Date:** {self.threshold_decision['endorsement_date'] or '[Not Set]'}
* **Rationale:** {self.threshold_decision['rationale'] or '[Not Set]'}
"""

        # Full assessment sections (5-11) only if required
        if self.threshold_decision.get('requires_full_assessment'):
            section_num = 5
            for area in INHERENT_RISK_AREAS:
                fa = self.full_assessment[area]
                report += f"""
---

## Section {section_num}: {area}

* **Assessment:** {fa['assessment'] or '[Not Set]'}
* **Existing Controls:** {fa['controls'] or '[Not Set]'}
* **Proposed Mitigations:** {fa['mitigations'] or '[Not Set]'}
* **Residual Risk:** {fa['residual_risk'] or '[Not Assessed]'}
"""
                section_num += 1

        report += f"""
---

## Section 12: Summary, Mitigations & Approval

**Overall Residual Risk Rating:** **{self.residual_risk_rating}**

### Mitigation Plan
"""
        if not self.mitigation_plan:
            report += "[No mitigation items entered.]\n"
        else:
            report += "| Risk Area | Risk Description | Action | Responsible | Target Date | Status |\n"
            report += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
            for item in self.mitigation_plan:
                report += f"| {item.get('risk_area', '')} | {item.get('risk_description', '')} | {item.get('action', '')} | {item.get('responsible', '')} | {item.get('target_date', '')} | {item.get('status', '')} |\n"

        report += f"""
### Approval

**Assessing Officer:**
* Name: {self.approvals['assessing_officer'].get('name', '[Not Set]')}, Position: {self.approvals['assessing_officer'].get('position', '[Not Set]')}, Date: {self.approvals['assessing_officer'].get('date', '[Not Set]')}

**Approving Officer:**
* Name: {self.approvals['approving_officer'].get('name', '[Not Set]')}, Position: {self.approvals['approving_officer'].get('position', '[Not Set]')}, Date: {self.approvals['approving_officer'].get('date', '[Not Set]')}
* Decision: {self.approvals['approving_officer'].get('decision', '[Not Set]')}, Conditions: {self.approvals['approving_officer'].get('conditions', '[Not Set]')}

**Accountable Official:**
* Name: {self.approvals['accountable_official'].get('name', '[Not Set]')}, Position: {self.approvals['accountable_official'].get('position', '[Not Set]')}, Date: {self.approvals['accountable_official'].get('date', '[Not Set]')}
* Decision: {self.approvals['accountable_official'].get('decision', '[Not Set]')}, Conditions: {self.approvals['accountable_official'].get('conditions', '[Not Set]')}

### Links & References
* **Agency AI Inventory Reference:** {self.ai_inventory_ref or '[Not Set]'}
* **Transparency Statement Link:** {self.transparency_statement_link or '[Not Set]'}
* **Referenced Frameworks:** {self.referenced_frameworks or '[Not Set]'}

### DTA Notification
* **DTA Notified:** {'Yes' if self.dta_notified else 'No'}
* **Notification Date:** {self.dta_notification_date or 'N/A'}

---

## Ongoing Monitoring and Review

* **Monitoring Plan Reference:** {self.monitoring_plan_ref or '[Not Set]'}
* **Review Frequency:** {self.review_frequency or '[Not Set]'}
* **Next Scheduled Review Date:** {self.next_review_date or '[Not Set]'}
* **Last Assessment Date:** {self.last_assessment_date or '[Not Set]'}

## Related Assessment Statuses
"""
        for name, status in self.related_assessment_statuses.items():
            report += f"* **{name}:** {status}\n"

        # Include system description details
        report += f"""
---

## Technical Details

### Technical Specifications
* AI Model Type: {self.technical_specs.get('model_type', '[Not Set]')}
* Algorithms Used: {self.technical_specs.get('algorithms', '[Not Set]')}
* Programming Language and Libraries: {self.technical_specs.get('language_libs', '[Not Set]')}
* Hardware and Infrastructure: {self.technical_specs.get('hardware_infra', '[Not Set]')}

### Data Sources and Characteristics
* Data Sources: {self.data_details.get('sources', '[Not Set]')}
* Data Volume and Velocity: {self.data_details.get('volume_velocity', '[Not Set]')}
* Data Types: {self.data_details.get('types', '[Not Set]')}
* Data Retention Policy: {self.data_details.get('retention_policy', '[Not Set]')}

### Deployment Context
* Operational Environment: {self.deployment_context.get('operational_env', '[Not Set]')}
* Target Users or Affected Individuals: {self.deployment_context.get('target_users_affected', '[Not Set]')}
* Decision-Making Authority: {self.deployment_context.get('decision_authority', '[Not Set]')}

### Procurement
* Procurement Method: {self.procurement.get('method', '[Not Set]')}
* AI Ethical/Risk Requirements: {self.procurement.get('ethical_reqs', '[Not Set]')}
"""
        return report.strip()
