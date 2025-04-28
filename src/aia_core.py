# aia_core.py
# Core logic for the Algorithmic Impact Assessment object

import json
import datetime
import uuid # For unique mitigation item IDs

# --- Constants based on AIA v1.1 ---

AIA_VERSION = "1.1"

DIMENSIONS = [
    "Human Impact",
    "Contestability and Redress",
    "Explainability and Interpretability",
    "Bias and Fairness",
    "Privacy Risk",
    "Data Representativeness",
    "Autonomy and Oversight",
    "Accountability and Auditability",
    "Security and Resilience",
    "Monitoring and Drift",
    "Ethical Considerations",
    "Legal Compliance",
    "Robustness and Reliability",
]

ETHICS_PRINCIPLES_MAP = {
    "Human Impact": "1 (Human, societal & environmental wellbeing), 2 (Human-centred values)",
    "Contestability and Redress": "7 (Contestability)",
    "Explainability and Interpretability": "6 (Transparency & explainability)",
    "Bias and Fairness": "3 (Fairness)",
    "Privacy Risk": "4 (Privacy protection & security)",
    "Data Representativeness": "3 (Fairness), 5 (Reliability & safety)",
    "Autonomy and Oversight": "8 (Accountability), 2 (Human-centred values)",
    "Accountability and Auditability": "8 (Accountability), 6 (Transparency & explainability)",
    "Security and Resilience": "5 (Reliability & safety), 4 (Privacy protection & security)",
    "Monitoring and Drift": "5 (Reliability & safety), 8 (Accountability)",
    "Ethical Considerations": "1 (Human, societal & environmental wellbeing), 2 (Human-centred values)",
    "Legal Compliance": "(Legal basis for all)",
    "Robustness and Reliability": "5 (Reliability & safety)",
}

RISK_CATEGORIES = [
    {"range": (0, 10), "category": "Low", "action": "Standard deployment procedures. Routine monitoring. Document AIA. Approval typically by Project/System Owner."},
    {"range": (11, 25), "category": "Medium", "action": "Requires documented Mitigation Plan (Section 9). Enhanced monitoring procedures. Requires review/endorsement by [Specify Role, e.g., AI Governance Committee or relevant Senior Manager]. Approval potentially involves Accountable AI Official oversight."},
    {"range": (26, 40), "category": "High", "action": "Requires comprehensive Mitigation Plan with clear timelines and owners. Strict oversight and monitoring. Requires formal approval from [Specify Senior Role, e.g., Designated Accountable AI Official, SES Band 1/2]. Limitations on use may be needed."},
    {"range": (41, 65), "category": "Severe", "action": "Requires robust Mitigation Plan addressing all significant risks. Requires highest level approval [Specify Executive Role, e.g., Agency Head / Deputy Secretary / Designated Senior Accountable AI Official]. Deployment may be contingent on significant redesign, specific limitations, independent review, or may be prohibited if risks cannot be adequately mitigated."},
]

# --- AIA Class Definition ---

class AlgorithmicImpactAssessment:
    """Represents a single Algorithmic Impact Assessment instance."""

    def __init__(self, system_name="[System Name]", agency_name="[Agency Name]"):
        """Initializes a new AIA instance."""
        self.aia_version = AIA_VERSION
        self.assessment_date = datetime.date.today().isoformat()
        self.assessed_by = [] # List of strings "[Name] ([Role])"
        self.referenced_frameworks = ""

        # Section 4: System Description
        self.system_name = system_name
        self.agency_name = agency_name
        self.system_purpose = ""
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
        self.related_assessments = { # Note: These are descriptions from AIA, statuses managed elsewhere
            "pia_status_desc": "", "pia_ref": "", "other_assessments": ""
        }

        # Section 5 & 6: Impact Dimensions, Scores, and Justifications
        self.dimensions = {
            dim: {"score": 0, "justification": ""} for dim in DIMENSIONS
        }

        # Section 7 & 8: Scoring Summary and Risk Category (Calculated)
        self.total_score = 0
        self.risk_category = {"category": "Low", "action": RISK_CATEGORIES[0]['action']} # Default to Low

        # Section 9: Mitigation Plan
        self.mitigation_plan = [] # List of dicts {id, dimension, risk_score_desc, action, responsible, target_date, status}

        # Section 10: Documentation and Approval
        self.approvals = {
            "assessor": {"name": "", "role": "", "date": ""}, # Can be list if multiple
            "reviewer": {"name": "", "role": "", "comments": "", "date": ""}, # Can be list
            "approver": {"name": "", "role": "", "decision": "", "conditions": "", "date": ""}
        }
        self.ai_inventory_ref = ""
        self.transparency_statement_link = ""

        # Section 11: Ongoing Monitoring and Review
        self.monitoring_plan_ref = ""
        self.review_frequency = ""
        self.next_review_date = ""

        # --- Attributes for Register Tracking (Managed via DB Interaction) ---
        self.system_id = None # Set when loaded/saved to DB
        self.aia_status = "Draft" # Overall status: Draft, In Progress, Review, Approved, Archived
        self.related_assessment_statuses = { # Track progress of key related assessments
            "PIA": "Not Started", # Status: Not Started, In Progress, Completed, N/A
            "Security Assessment": "Not Started",
            "Human Rights Assessment": "Not Started",
            # Add other assessment types as needed in db_manager and here for consistency
        }
        self.creation_date = datetime.datetime.now().isoformat() # Set on creation
        self.last_modified_date = datetime.datetime.now().isoformat() # Updated on any change


    # --- Methods for Setting Data ---

    def set_metadata(self, assessed_by, referenced_frameworks="", assessment_date=None):
        """Sets assessor info, frameworks, and assessment date."""
        if isinstance(assessed_by, list):
             self.assessed_by = assessed_by
        else:
             self.assessed_by = [assessed_by] # Assume single assessor if string
        self.referenced_frameworks = referenced_frameworks
        if assessment_date:
             # Add validation if needed (e.g., ensure it's a valid date string/object)
             self.assessment_date = assessment_date
        self.last_modified_date = datetime.datetime.now().isoformat()

    def set_system_details(self, system_name="", agency_name="", purpose="", tech_specs={}, data_details={},
                           deployment_context={}, procurement={}, related_assessments={}):
        """Updates system description sections."""
        if system_name: self.system_name = system_name
        if agency_name: self.agency_name = agency_name
        self.system_purpose = purpose or self.system_purpose
        self.technical_specs.update(tech_specs)
        self.data_details.update(data_details)
        self.deployment_context.update(deployment_context)
        self.procurement.update(procurement)
        # Update related_assessments descriptions (statuses managed separately)
        if 'pia_ref' in related_assessments:
             self.related_assessments['pia_ref'] = related_assessments['pia_ref']
        if 'other_assessments' in related_assessments:
             self.related_assessments['other_assessments'] = related_assessments['other_assessments']
        # Note: pia_status_desc is not directly set here, status comes from related_assessment_statuses
        self.last_modified_date = datetime.datetime.now().isoformat()


    def set_dimension_score(self, dimension_name, score, justification=""):
        """Sets the score and justification for a specific dimension."""
        if dimension_name not in self.dimensions:
            raise ValueError(f"Invalid dimension name: {dimension_name}")
        if not isinstance(score, int) or not (0 <= score <= 5):
            raise ValueError(f"Score for {dimension_name} must be an integer between 0 and 5.")

        self.dimensions[dimension_name]["score"] = score
        self.dimensions[dimension_name]["justification"] = justification
        self._update_risk_assessment() # Recalculate after score change
        self.last_modified_date = datetime.datetime.now().isoformat()

    # --- Methods for Mitigation Plan ---

    def add_mitigation_item(self, dimension, risk_score_desc, action, responsible, target_date, status="Planned"):
        """Adds an item to the mitigation plan."""
        item = {
            "id": str(uuid.uuid4()), # Unique ID for potential updates/deletions
            "dimension": dimension,
            "risk_score_desc": risk_score_desc, # e.g., "Potential bias (Score=4)"
            "action": action,
            "responsible": responsible,
            "target_date": target_date,
            "status": status # e.g., Planned, In Progress, Completed, Cancelled
        }
        self.mitigation_plan.append(item)
        self.last_modified_date = datetime.datetime.now().isoformat()
        return item['id']

    def update_mitigation_item(self, item_id, **updates):
        """Updates fields of an existing mitigation item by its ID."""
        found = False
        for item in self.mitigation_plan:
            if item['id'] == item_id:
                item.update(updates)
                found = True
                break
        if not found:
            raise ValueError(f"Mitigation item with ID {item_id} not found.")
        self.last_modified_date = datetime.datetime.now().isoformat()
        return True

    def remove_mitigation_item(self, item_id):
        """Removes a mitigation item by its ID."""
        initial_len = len(self.mitigation_plan)
        self.mitigation_plan = [item for item in self.mitigation_plan if item['id'] != item_id]
        if len(self.mitigation_plan) == initial_len:
            raise ValueError(f"Mitigation item with ID {item_id} not found.")
        self.last_modified_date = datetime.datetime.now().isoformat()
        return True

    # --- Methods for Approval and Monitoring ---

    def set_approval(self, assessor={}, reviewer={}, approver={}):
         """Sets approval details."""
         # Use update to only change provided fields
         if assessor: self.approvals['assessor'].update(assessor)
         if reviewer: self.approvals['reviewer'].update(reviewer)
         if approver: self.approvals['approver'].update(approver)
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

    # --- Methods for managing statuses ---
    def set_aia_status(self, status):
        """Sets the overall AIA status."""
        allowed_statuses = ["Draft", "In Progress", "Review", "Approved", "Archived"]
        if status not in allowed_statuses:
            raise ValueError(f"Invalid AIA status. Must be one of: {allowed_statuses}")
        self.aia_status = status
        self.last_modified_date = datetime.datetime.now().isoformat()

    def set_related_assessment_status(self, assessment_name, status):
        """Sets the status for a specific related assessment."""
        allowed_statuses = ["Not Started", "In Progress", "Completed", "N/A"]
        if assessment_name not in self.related_assessment_statuses:
            # Allow adding new assessment types dynamically if needed,
            # but ensure they are also tracked in the DB schema via db_manager.py
            print(f"Warning: Assessment type '{assessment_name}' not predefined. Adding dynamically.")
            # Or raise ValueError(f"Unknown assessment type: {assessment_name}")
        if status not in allowed_statuses:
            raise ValueError(f"Invalid status for {assessment_name}. Must be one of: {allowed_statuses}")
        self.related_assessment_statuses[assessment_name] = status
        self.last_modified_date = datetime.datetime.now().isoformat()

    # --- Calculation Methods ---

    def _calculate_total_score(self):
        """Calculates the sum of all dimension scores."""
        self.total_score = sum(dim["score"] for dim in self.dimensions.values())
        return self.total_score

    def _determine_risk_category(self):
        """Determines the risk category based on the total score."""
        score = self.total_score
        for category_info in RISK_CATEGORIES:
            min_score, max_score = category_info["range"]
            if min_score <= score <= max_score:
                self.risk_category = {
                    "category": category_info["category"],
                    "action": category_info["action"]
                }
                return self.risk_category
        # Fallback for scores outside expected 0-65 range
        self.risk_category = {"category": "Undefined", "action": "Score out of expected range."}
        return self.risk_category

    def _update_risk_assessment(self):
        """Recalculates total score and risk category. Should be called before saving or displaying."""
        self._calculate_total_score()
        self._determine_risk_category()


    # --- Reporting Method (Kept for generating text output) ---

    def generate_report(self):
        """Generates a formatted string report based on the current AIA data."""
        self._update_risk_assessment() # Ensure calculations are current

        report = f"""
# Algorithmic Impact Assessment (AIA)

**System Name:** {self.system_name} (ID: {self.system_id or 'N/A'})
**Agency:** {self.agency_name}
**AIA Version:** {self.aia_version}
**AIA Status:** {self.aia_status}
**Last Modified:** {self.last_modified_date}
**Assessment Date:** {self.assessment_date}
**Assessed By:** {', '.join(self.assessed_by) if self.assessed_by else '[Not Set]'}
**Referenced Frameworks:** {self.referenced_frameworks or '[Not Set]'}

## Related Assessment Statuses
"""
        for name, status in self.related_assessment_statuses.items():
             report += f"- **{name}:** {status}\n"
        report += "\n"

        # --- Sections 1-3 (Standard Text) ---
        report += """
## 1. Introduction
... [Standard Intro Text based on v1.1] ...

## 2. AIA Scope
... [Standard Scope Text based on v1.1] ...

## 3. Assessment Process Overview
... [Standard Process Text based on v1.1] ...
"""
        # --- Section 4 ---
        report += f"""
## 4. System Description
* **4.1 System Name:** {self.system_name}
* **4.2 System Purpose and Functionality:** {self.system_purpose or '[Not Set]'}
* **4.3 Technical Specifications:**
    * AI Model Type: {self.technical_specs.get('model_type', '[Not Set]')}
    * Algorithms Used: {self.technical_specs.get('algorithms', '[Not Set]')}
    * Programming Language and Key Libraries/Frameworks: {self.technical_specs.get('language_libs', '[Not Set]')}
    * Hardware and Infrastructure: {self.technical_specs.get('hardware_infra', '[Not Set]')}
* **4.4 Data Sources and Characteristics:**
    * Data Sources: {self.data_details.get('sources', '[Not Set]')}
    * Data Volume and Velocity: {self.data_details.get('volume_velocity', '[Not Set]')}
    * Data Types: {self.data_details.get('types', '[Not Set]')}
    * Data Retention Policy: {self.data_details.get('retention_policy', '[Not Set]')}
* **4.5 Deployment Context:**
    * Operational Environment: {self.deployment_context.get('operational_env', '[Not Set]')}
    * Target Users or Affected Individuals/Groups: {self.deployment_context.get('target_users_affected', '[Not Set]')}
    * Decision-Making Authority: {self.deployment_context.get('decision_authority', '[Not Set]')}
* **4.6 Procurement Method and Context:**
    * Procurement Method: {self.procurement.get('method', '[Not Set]')}
    * AI Ethical/Risk Requirements in Procurement: {self.procurement.get('ethical_reqs', '[Not Set]')}
* **4.7 Related Assessments:**
    * Privacy Impact Assessment (PIA) Status: {self.related_assessment_statuses.get('PIA', 'N/A')} (Ref/Link: {self.related_assessments.get('pia_ref', '[Not Set]')})
    * Other Relevant Assessments: {self.related_assessments.get('other_assessments', '[Not Set]')}
    * (Security Assessment Status: {self.related_assessment_statuses.get('Security Assessment', 'N/A')}, Human Rights Assessment Status: {self.related_assessment_statuses.get('Human Rights Assessment', 'N/A')})

## 5/6. Impact Assessment Dimensions & Justification
"""
        # --- Sections 5/6 ---
        for dim_name, data in self.dimensions.items():
            principles = ETHICS_PRINCIPLES_MAP.get(dim_name, '')
            report += f"### {dim_name}\n"
            report += f"* **Relevant Australian AI Ethics Principle(s):** {principles}\n"
            report += f"* **Score (0-5):** {data['score']}\n"
            report += f"* **Justification:** {data['justification'] or '[Not Set]'}\n\n"

        # --- Section 7 ---
        report += f"""
## 7. Scoring Summary
| Dimension                      | Score (0-5) | Primary Aust. AI Ethics Principle(s) |
| :----------------------------- | :---------- | :--------------------------------- |
"""
        for dim_name, data in self.dimensions.items():
             principles = ETHICS_PRINCIPLES_MAP.get(dim_name, '')
             report += f"| {dim_name:<30} | {data['score']:<11} | {principles:<34} |\n"
        report += f"| **{'Total Score':<30}** | **{self.total_score:<11}** |                                    |\n"

        # --- Section 8 ---
        report += f"""
## 8. Risk Categorization
**Overall System Risk Category:** {self.risk_category['category']}
**Total Score:** {self.total_score} / 65
**Required Action:** {self.risk_category['action']}
"""

        # --- Section 9 ---
        report += "\n## 9. Mitigation Plan\n"
        if not self.mitigation_plan:
            report += "[No mitigation items entered.]\n"
        else:
            report += "| Dimension        | Risk/Score Desc.       | Action                 | Responsible        | Target Date | Status      |\n"
            report += "| :--------------- | :--------------------- | :--------------------- | :----------------- | :---------- | :---------- |\n"
            for item in self.mitigation_plan:
                 report += f"| {item.get('dimension', ''):<16} | {item.get('risk_score_desc', ''):<22} | {item.get('action', ''):<22} | {item.get('responsible', ''):<18} | {item.get('target_date', ''):<11} | {item.get('status', ''):<11} |\n"

        # --- Section 10 ---
        report += f"""

## 10. Documentation and Approval
* **Assessor(s):**
    * Name: {self.approvals['assessor'].get('name', '[Not Set]')}, Role: {self.approvals['assessor'].get('role', '[Not Set]')}, Date: {self.approvals['assessor'].get('date', '[Not Set]')}
* **Reviewer(s):**
    * Name: {self.approvals['reviewer'].get('name', '[Not Set]')}, Role: {self.approvals['reviewer'].get('role', '[Not Set]')}, Date: {self.approvals['reviewer'].get('date', '[Not Set]')}
    * Comments: {self.approvals['reviewer'].get('comments', '[Not Set]')}
* **Approver:**
    * Name: {self.approvals['approver'].get('name', '[Not Set]')}, Role: {self.approvals['approver'].get('role', '[Not Set]')}, Date: {self.approvals['approver'].get('date', '[Not Set]')}
    * Decision: {self.approvals['approver'].get('decision', '[Not Set]')}, Conditions: {self.approvals['approver'].get('conditions', '[Not Set]')}
* **Agency AI Inventory Reference:** {self.ai_inventory_ref or '[Not Set]'}
* **Link to APS AI Transparency Statement:** {self.transparency_statement_link or '[Not Set]'}
"""
        # --- Section 11 ---
        report += f"""

## 11. Ongoing Monitoring and Review
* **Monitoring Plan Reference:** {self.monitoring_plan_ref or '[Not Set]'}
* **Review Frequency:** {self.review_frequency or '[Not Set]'}
* **Next Scheduled Review Date:** {self.next_review_date or '[Not Set]'}
"""
        return report.strip()