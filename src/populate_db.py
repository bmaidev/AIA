# populate_db.py
# Script to add example AIA records to the database.

import datetime
import db_manager as db
from aia_core import AlgorithmicImpactAssessment, DIMENSIONS

# --- Helper to create Example AIA 1: Low Risk ---
def create_example_aia_1():
    print("Creating Example 1: Low Risk - Internal Document Analyser")
    aia = AlgorithmicImpactAssessment(
        system_name="Internal Document Analyser v1",
        agency_name="Dept of Infrastructure"
    )

    # Metadata
    aia.set_metadata(
        assessed_by=["Amit Singh (Business Analyst)"],
        assessment_date="2024-10-15"
    )

    # System Details
    aia.set_system_details(
        purpose="Assists staff by summarising internal reports and extracting key entities using NLP. Advisory only.",
        tech_specs={
            "model_type": "NLP (Transformer - BERT based)",
            "algorithms": "Pre-trained Hugging Face Model (DistilBERT)",
            "language_libs": "Python (Transformers, spaCy)",
            "hardware_infra": "Cloud-based (Internal Secure Tenant)"
        },
        data_details={
            "sources": "Uploaded internal documents (Word, PDF)",
            "volume_velocity": "~50 docs/day",
            "types": "Unstructured text",
            "retention_policy": "Processed data deleted after 24h, source docs retained per agency policy."
        },
        deployment_context={
            "operational_env": "Internal intranet tool, integrated with document management",
            "target_users_affected": "Internal policy and admin staff",
            "decision_authority": "Information provision only"
        },
        procurement={"method": "Developed in-house using open-source components"},
        related_assessments={"pia_ref": "PIA-DOC-ANA-01"}
    )

    # Scores & Justifications (Low Risk Profile)
    scores = {
        "Human Impact": 1, "Contestability and Redress": 0, "Explainability and Interpretability": 2,
        "Bias and Fairness": 1, "Privacy Risk": 2, "Data Representativeness": 1,
        "Autonomy and Oversight": 4, "Accountability and Auditability": 1, "Security and Resilience": 1,
        "Monitoring and Drift": 2, "Ethical Considerations": 1, "Legal Compliance": 0,
        "Robustness and Reliability": 1
    }
    justifications = {
        "Human Impact": "Minor impact on staff efficiency. No direct impact on public rights/outcomes.",
        "Contestability and Redress": "N/A - System provides summaries, no contestable decisions.",
        "Explainability and Interpretability": "Uses standard NLP techniques. Feature importance available but not always intuitive for summaries.",
        "Bias and Fairness": "Tested on diverse internal docs. Potential for minor summary bias mitigated by human review.",
        "Privacy Risk": "Processes internal docs, some may contain personal info. Handled within secure env, short retention. PIA completed.",
        "Data Representativeness": "Data is representative of internal agency documents.",
        "Autonomy and Oversight": "System is advisory. Human staff use outputs as input to their own work. High human oversight.",
        "Accountability and Auditability": "User actions logged. Summary generation process traceable.",
        "Security and Resilience": "Deployed in secure cloud env, standard security controls applied.",
        "Monitoring and Drift": "Basic performance monitoring (accuracy, latency) in place.",
        "Ethical Considerations": "Minimal ethical concerns. Primary use is efficiency.",
        "Legal Compliance": "Legal review confirmed compliance with relevant agency acts and privacy.",
        "Robustness and Reliability": "Handles common document formats well. May fail on complex layouts - graceful failure implemented."
    }
    for dim, score in scores.items():
        aia.set_dimension_score(dim, score, justifications.get(dim, ""))

    # Mitigation Plan (None needed for Low Risk)

    # Approval
    aia.set_approval(
        assessor={"name": "Amit Singh", "role": "Business Analyst", "date": "2024-10-15"},
        approver={"name": "Eleanor Vance", "role": "Branch Manager", "decision": "Approved", "date": "2024-10-20"}
    )
    aia.set_links(inventory_ref="DOI-AI-001")

    # Monitoring
    aia.set_monitoring(plan_ref="Internal Monitoring SOP", frequency="Annually", next_date="2025-10-20")

    # Statuses
    aia.set_aia_status("Approved")
    aia.set_related_assessment_status("PIA", "Completed")
    aia.set_related_assessment_status("Security Assessment", "Completed")
    aia.set_related_assessment_status("Human Rights Assessment", "N/A")

    return aia

# --- Helper to create Example AIA 2: Medium Risk ---
def create_example_aia_2():
    print("Creating Example 2: Medium Risk - Public Service Chatbot")
    aia = AlgorithmicImpactAssessment(
        system_name="Citizen Assist Chatbot v3",
        agency_name="Dept of Human Services"
    )

    # Metadata
    aia.set_metadata(
        assessed_by=["Dr. Evelyn Reed (AI Ethicist)", "Kenji Tanaka (Lead Dev)"],
        assessment_date="2025-02-10",
        referenced_frameworks="National AI Assurance Framework"
    )

    # System Details
    aia.set_system_details(
        purpose="Provides information and guides users through application processes on the public website. Escalates complex queries to human agents.",
        tech_specs={
            "model_type": "NLP (Conversational AI - RAG)",
            "algorithms": "Fine-tuned LLM (e.g., Llama variant) with Retrieval Augmented Generation",
            "language_libs": "Python (LangChain, FastAPI, VectorDB)",
            "hardware_infra": "Cloud PaaS (Managed Service)"
        },
        data_details={
            "sources": "Public website content, anonymised query logs, curated FAQs",
            "volume_velocity": "~1000 queries/day",
            "types": "Unstructured text (queries), Structured FAQs",
            "retention_policy": "Anonymised logs retained 90 days for analysis."
        },
        deployment_context={
            "operational_env": "Public facing agency website",
            "target_users_affected": "General public seeking information or assistance",
            "decision_authority": "Information provision only, with clear escalation paths"
        },
        procurement={"method": "Co-developed with external partner"},
        related_assessments={"pia_ref": "DHS-PIA-CB-03", "other_assessments": "Security Assessment Ref: SA-CB-03"}
    )

    # Scores & Justifications (Medium Risk Profile)
    scores = {
        "Human Impact": 3, "Contestability and Redress": 2, "Explainability and Interpretability": 3,
        "Bias and Fairness": 3, "Privacy Risk": 2, "Data Representativeness": 2,
        "Autonomy and Oversight": 2, "Accountability and Auditability": 2, "Security and Resilience": 2,
        "Monitoring and Drift": 2, "Ethical Considerations": 3, "Legal Compliance": 1,
        "Robustness and Reliability": 2
    }
    justifications = {
        "Human Impact": "Moderate impact on access to information. Incorrect info could disadvantage users. Clear escalation helps mitigate.",
        "Contestability and Redress": "Users can request human review via escalation button. Process documented internally.",
        "Explainability and Interpretability": "RAG architecture helps trace info sources, but LLM reasoning isn't fully explainable. Response confidence scores used.",
        "Bias and Fairness": "Potential for bias based on training data (website content may have implicit biases). Language model tested, some demographic performance variance noted. Mitigation planned.",
        "Privacy Risk": "Anonymised logs used. No PII collection via chatbot itself. PIA completed.",
        "Data Representativeness": "Knowledge base covers main services, but edge cases might be missing. User feedback loop exists.",
        "Autonomy and Oversight": "Human-in-the-loop for escalation. Regular review of conversation logs by dedicated team.",
        "Accountability and Auditability": "Logs conversations (anonymised). Escalation pathway tracked.",
        "Security and Resilience": "Standard cloud security. Input sanitization implemented. Model robustness tested.",
        "Monitoring and Drift": "Automated monitoring of escalation rates, user satisfaction scores, common failure points.",
        "Ethical Considerations": "Potential for user frustration, providing misleading info. Tone/safety filters implemented. Transparency about AI use provided.",
        "Legal Compliance": "Internal legal review conducted. Complies with privacy, accessibility standards checked.",
        "Robustness and Reliability": "Generally reliable, but susceptible to 'hallucinations' or off-topic conversations. Guardrails in place."
    }
    for dim, score in scores.items():
        aia.set_dimension_score(dim, score, justifications.get(dim, ""))

    # Mitigation Plan
    aia.add_mitigation_item("Bias and Fairness", "Demographic performance variance (Score=3)", "Implement targeted testing with diverse user personas. Fine-tune model on augmented data.", "AI Ethics & Dev Team", "2025-06-30", "Planned")
    aia.add_mitigation_item("Explainability", "LLM reasoning opaque (Score=3)", "Enhance RAG source citation display. Provide users with clearer 'Why this answer?' explanations.", "Dev Team", "2025-07-31", "Planned")
    aia.add_mitigation_item("Ethical Considerations", "Misleading info risk (Score=3)", "Strengthen safety filters. Increase human QA sample rate for responses.", "QA & Policy Team", "2025-05-30", "In Progress")

    # Approval
    aia.set_approval(
        assessor={"name": "Dr. E. Reed, K. Tanaka", "role": "AI Ethicist, Lead Dev", "date": "2025-02-10"},
        reviewer={"name": "Service Delivery Committee", "role": "Governance Body", "date": "2025-03-05", "comments":"Mitigation plan must be actioned."},
        # Approver might be pending review completion
    )
    aia.set_links(inventory_ref="DHS-AI-015")

    # Monitoring
    aia.set_monitoring(plan_ref="Chatbot Monitoring Plan v2", frequency="Monthly Review Cycle", next_date="2025-05-01")

    # Statuses
    aia.set_aia_status("Review") # Pending final approval after mitigation
    aia.set_related_assessment_status("PIA", "Completed")
    aia.set_related_assessment_status("Security Assessment", "Completed")
    aia.set_related_assessment_status("Human Rights Assessment", "Not Started") # Might be triggered by review

    return aia


# --- Helper to create Example AIA 3: High Risk ---
def create_example_aia_3():
    print("Creating Example 3: High Risk - Compliance Risk Analyser")
    aia = AlgorithmicImpactAssessment(
        system_name="Regulated Entity Risk Analyser (RERA)",
        agency_name="National Compliance Agency"
    )

    # Metadata
    aia.set_metadata(
        assessed_by=["Compliance AI Working Group", "External Audit Partners (Ethics & Legal)"],
        assessment_date="2025-01-20",
        referenced_frameworks="NCA AI Governance Policy, National AI Assurance Framework, ISO 23894"
    )

    # System Details
    aia.set_system_details(
        purpose="Analyses regulated entity data submissions to identify potential non-compliance indicators and prioritise entities for audit/inspection. Assists human decision-makers.",
        tech_specs={
            "model_type": "Ensemble (Classification, Anomaly Detection)",
            "algorithms": "Gradient Boosting, Isolation Forest, Custom Rule Engine",
            "language_libs": "Python (Scikit-learn, Pandas), SQL",
            "hardware_infra": "On-premise Secure Data Centre"
        },
        data_details={
            "sources": "Mandatory entity reporting data, Historical audit outcomes, External financial indicators",
            "volume_velocity": "Batch processing ~10k records quarterly",
            "types": "Structured financial/operational data",
            "retention_policy": "Aligned with legislative record-keeping requirements (7+ years)."
        },
        deployment_context={
            "operational_env": "Internal secure analyst platform",
            "target_users_affected": "Regulated entities (indirectly via audit selection), Internal Audit/Compliance staff (directly)",
            "decision_authority": "Decision support/recommendation requiring human approval - High-risk indicators require mandatory senior review."
        },
        procurement={"method": "Developed in-house with specialist contractor support"},
        related_assessments={"pia_ref": "NCA-PIA-RERA-01", "other_assessments": "Security Assessment: SA-RERA-01 (High); Human Rights Assessment: HRA-RERA-01"}
    )

    # Scores & Justifications (High Risk Profile)
    scores = {
        "Human Impact": 4, "Contestability and Redress": 3, "Explainability and Interpretability": 3,
        "Bias and Fairness": 4, "Privacy Risk": 3, "Data Representativeness": 3,
        "Autonomy and Oversight": 2, "Accountability and Auditability": 1, "Security and Resilience": 2,
        "Monitoring and Drift": 2, "Ethical Considerations": 4, "Legal Compliance": 2, # Assumes compliance pending mitigations
        "Robustness and Reliability": 3
    }
    justifications = {
        "Human Impact": "Significant impact on regulated entities via audit selection, potential financial/reputational consequences.",
        "Contestability and Redress": "Entities can contest audit *findings*, but contesting the *selection* for audit is difficult. Focus on justification for audit.",
        "Explainability and Interpretability": "Ensemble model complex. SHAP values & Rule Engine tracing provide partial explanations. Work ongoing for clearer justifications.",
        "Bias and Fairness": "High risk of bias (proxy discrimination) based on historical data or data gaps. Extensive fairness testing conducted, mitigations implemented but residual risk remains.",
        "Privacy Risk": "Processes sensitive commercial data. Access controls stringent. PIA completed, risks identified and managed.",
        "Data Representativeness": "Data gaps for certain entity types/sizes. Historical data may reflect past biases. Ongoing data improvement strategy.",
        "Autonomy and Oversight": "Human audit teams make final decisions. Mandatory senior review for AI-flagged high-risk cases. Strong oversight protocols.",
        "Accountability and Auditability": "Full audit trail of data inputs, model outputs, user overrides, and final decisions.",
        "Security and Resilience": "Deployed in high-security environment. Model robustness testing performed. Ongoing vulnerability management.",
        "Monitoring and Drift": "Continuous monitoring of model performance, indicator stability, and fairness metrics. Alerting mechanism in place.",
        "Ethical Considerations": "High ethical concerns regarding fairness, potential chilling effects on reporting. Proportionality debated. Stakeholder consultation undertaken.",
        "Legal Compliance": "Extensive legal review against enabling legislation, admin law, privacy. Conditional compliance based on mitigations and human oversight.",
        "Robustness and Reliability": "Model tested against data quality issues. Ensemble approach improves reliability but edge cases exist."
    }
    for dim, score in scores.items():
        aia.set_dimension_score(dim, score, justifications.get(dim, ""))

    # Mitigation Plan
    aia.add_mitigation_item("Bias and Fairness", "Residual bias risk (Score=4)", "Implement post-processing fairness adjustments (e.g., disparate impact remover). Conduct annual external fairness audit.", "AI Governance & Stats Team", "2025-08-30", "Planned")
    aia.add_mitigation_item("Explainability", "Complex model (Score=3)", "Develop simplified explanation summaries for audit teams. Pilot counterfactual explanation methods.", "AI Dev & User Training Team", "2025-10-31", "Planned")
    aia.add_mitigation_item("Contestability", "Audit selection contestability (Score=3)", "Improve documentation justifying audit selection provided to entity (where legally permissible). Establish internal review panel for selection methodology.", "Legal & Compliance Policy", "2025-09-30", "Planned")
    aia.add_mitigation_item("Ethical Considerations", "Fairness/Proportionality (Score=4)", "Ongoing stakeholder engagement. Publish high-level methodology transparency report.", "Ethics Committee & Comms", "Ongoing", "In Progress")

    # Approval
    aia.set_approval(
        assessor={"name": "Compliance AI WG", "role": "Cross-functional Team", "date": "2025-01-20"},
        reviewer={"name": "External Audit Partners", "role": "Independent Review", "date": "2025-03-15", "comments":"Approval contingent on mitigation plan execution and monitoring."},
        approver={"name": "Dep. Secretary Compliance", "role": "SES Band 2 (Accountable Official)", "decision": "Approved with Conditions", "conditions":"Strict adherence to oversight protocols & mitigation plan required. Annual review by Ethics Committee.", "date": "2025-04-10"}
    )
    aia.set_links(inventory_ref="NCA-AI-001", transparency_statement_link="Published: [Link to NCA Website]")

    # Monitoring
    aia.set_monitoring(plan_ref="RERA Monitoring & Evaluation Framework v1", frequency="Quarterly Performance & Fairness Review", next_date="2025-07-15")

    # Statuses
    aia.set_aia_status("Approved") # Approved with Conditions counts as Approved here
    aia.set_related_assessment_status("PIA", "Completed")
    aia.set_related_assessment_status("Security Assessment", "Completed")
    aia.set_related_assessment_status("Human Rights Assessment", "Completed")

    return aia


# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting DB Population Script ---")

    # Initialize DB (ensure tables exist)
    db.init_db()

    # List to hold populated AIA objects
    example_aias = []

    # Create example objects
    try:
        aia1 = create_example_aia_1()
        example_aias.append(aia1)
    except Exception as e:
        print(f"Error creating Example AIA 1: {e}")

    try:
        aia2 = create_example_aia_2()
        example_aias.append(aia2)
    except Exception as e:
        print(f"Error creating Example AIA 2: {e}")

    try:
        aia3 = create_example_aia_3()
        example_aias.append(aia3)
    except Exception as e:
        print(f"Error creating Example AIA 3: {e}")

    # Add/Update examples in the database
    for aia_obj in example_aias:
        try:
            print(f"\nProcessing: {aia_obj.system_name}")
            # Check if system already exists (optional, update_aia handles non-existent IDs gracefully but doesn't insert)
            # For simplicity, we'll add then update.
            system_id = db.add_system(aia_obj.system_name, aia_obj.agency_name)
            aia_obj.system_id = system_id # Assign the new ID to the object
            # Update the record with the full details
            db.update_aia(aia_obj)
            print(f"Successfully added/updated {aia_obj.system_name} in the database.")
        except Exception as e:
            print(f"Error processing {aia_obj.system_name} for database: {e}")

    print("\n--- DB Population Script Finished ---")