# populate_db.py
# Script to add example AI Impact Assessment records aligned to DTA Policy v2.0

import datetime
import db_manager as db
from aia_core import AlgorithmicImpactAssessment, INHERENT_RISK_AREAS


# --- Example 1: Low Risk — Threshold assessment only ---
def create_example_aia_1():
    print("Creating Example 1: Low Risk - Internal Document Analyser")
    aia = AlgorithmicImpactAssessment(
        system_name="Internal Document Analyser v2",
        agency_name="Dept of Infrastructure"
    )

    # Section 1: Basic Information
    aia.set_basic_info(
        reference_id="DOI-AIA-001",
        ai_technology_type="Natural Language Processing (NLP)",
        usage_pattern="Internal operational tool",
        use_case_description="Assists staff by summarising internal reports and extracting key entities using NLP. Advisory only — no decisions are made by the system.",
        accountable_use_case_owner={"name": "Amit Singh", "email": "amit.singh@infrastructure.gov.au", "position": "Director, Digital Services"},
        assessing_officer={"name": "Amit Singh", "email": "amit.singh@infrastructure.gov.au", "position": "Director, Digital Services"},
        approving_officer={"name": "Eleanor Vance", "email": "eleanor.vance@infrastructure.gov.au", "position": "Branch Manager"},
        accountable_official={"name": "Sarah Chen", "email": "sarah.chen@infrastructure.gov.au", "position": "Chief Information Officer"},
    )

    # In-scope determination
    aia.set_scope_determination(
        criteria_met=[2],  # "automates or augments a function previously performed by a person"
        is_in_scope=True,
        rationale="System augments document analysis previously done manually by staff."
    )

    # Section 2: Purpose and Benefits
    aia.set_purpose_and_benefits(
        purpose="Assists staff by summarising internal reports and extracting key entities using NLP. Advisory only.",
        problem_statement="Policy staff spend significant time reading and summarising lengthy reports. This tool reduces that burden.",
        non_ai_alternatives="Manual reading and summarisation by staff (current process). Keyword-based search tools were also considered but lack contextual understanding.",
        expected_benefits="Reduced staff time on document review by approximately 40%. Improved consistency in entity extraction across documents.",
        stakeholders=[
            {"name": "Internal policy and admin staff", "impact": "positive", "description": "Reduced workload, faster access to information"},
            {"name": "IT Security team", "impact": "both", "description": "Need to ensure secure processing of internal documents"},
        ]
    )

    # System Details
    aia.set_system_details(
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
        related_assessments={"pia_ref": "PIA-DOC-ANA-02"}
    )

    # Section 3: Inherent Risk Assessment — All Low
    aia.set_inherent_risk("Fairness", "Rare", "Minor", "Minimal fairness concerns — internal tool for document summarisation only.")
    aia.set_inherent_risk("Reliability and Safety", "Unlikely", "Minor", "System is advisory. Graceful failure implemented for unsupported formats.")
    aia.set_inherent_risk("Privacy and Security", "Unlikely", "Moderate", "Processes internal docs, some may contain personal info. Handled within secure env, short retention.")
    aia.set_inherent_risk("Transparency and Explainability", "Unlikely", "Minor", "Standard NLP techniques. Feature importance available.")
    aia.set_inherent_risk("Contestability", "Rare", "Insignificant", "No contestable decisions — provides summaries only.")
    aia.set_inherent_risk("Human Oversight", "Rare", "Minor", "High human oversight — staff use outputs as input to their own work.")
    aia.set_inherent_risk("Accountability", "Rare", "Minor", "User actions logged. Summary generation process traceable.")

    # Section 4: Threshold — Low risk, no full assessment needed
    aia.set_threshold_decision(
        endorsed_by="Eleanor Vance (Branch Manager)",
        endorsement_date="2025-10-20",
        rationale="All inherent risks rated Low. Standard deployment with routine monitoring is appropriate."
    )

    # Approval
    aia.set_approval(
        assessing_officer={"name": "Amit Singh", "position": "Director, Digital Services", "date": "2025-10-15"},
        approving_officer={"name": "Eleanor Vance", "position": "Branch Manager", "date": "2025-10-20", "decision": "Approved"},
    )
    aia.set_links(inventory_ref="DOI-AI-001")

    # Monitoring
    aia.set_monitoring(plan_ref="Internal Monitoring SOP", frequency="Every 12 months", next_date="2026-10-20")
    aia.last_assessment_date = "2025-10-15"

    # Statuses
    aia.set_aia_status("Approved")
    aia.set_related_assessment_status("PIA", "Completed")
    aia.set_related_assessment_status("Security Assessment", "Completed")
    aia.set_related_assessment_status("Human Rights Assessment", "N/A")

    return aia


# --- Example 2: Medium Risk — Full assessment required ---
def create_example_aia_2():
    print("Creating Example 2: Medium Risk - Public Service Chatbot")
    aia = AlgorithmicImpactAssessment(
        system_name="Citizen Assist Chatbot v3",
        agency_name="Dept of Human Services"
    )

    # Section 1: Basic Information
    aia.set_basic_info(
        reference_id="DHS-AIA-015",
        ai_technology_type="Generative AI / Large Language Model",
        usage_pattern="Customer/citizen interaction",
        use_case_description="Public-facing chatbot providing information and guiding users through application processes. Escalates complex queries to human agents.",
        accountable_use_case_owner={"name": "Dr. Evelyn Reed", "email": "evelyn.reed@humanservices.gov.au", "position": "AI Ethics Lead"},
        assessing_officer={"name": "Dr. Evelyn Reed", "email": "evelyn.reed@humanservices.gov.au", "position": "AI Ethics Lead"},
        approving_officer={"name": "Marcus Webb", "email": "marcus.webb@humanservices.gov.au", "position": "Director, Digital Channels"},
        accountable_official={"name": "Julia Hernandez", "email": "julia.hernandez@humanservices.gov.au", "position": "Deputy Secretary, Service Delivery"},
    )

    aia.set_scope_determination(
        criteria_met=[0, 3, 6],  # Decision/recommendation, public-facing, service delivery
        is_in_scope=True,
        rationale="Public-facing chatbot that influences access to government services and directly interacts with external users."
    )

    # Section 2
    aia.set_purpose_and_benefits(
        purpose="Provides information and guides users through application processes on the public website. Escalates complex queries to human agents.",
        problem_statement="High call volumes and wait times for citizens seeking information about services. Many queries are routine and can be handled by guided assistance.",
        non_ai_alternatives="Traditional FAQ pages, IVR phone system, increased call centre staff. These were considered but lack the contextual, conversational assistance that improves user experience.",
        expected_benefits="Reduced call centre wait times by 30%. 24/7 availability for common queries. Improved citizen satisfaction scores.",
        stakeholders=[
            {"name": "General public", "impact": "both", "description": "Improved access to info but risk of incorrect guidance"},
            {"name": "Call centre staff", "impact": "positive", "description": "Reduced routine query load"},
            {"name": "Vulnerable populations", "impact": "negative", "description": "May struggle with chatbot interaction, digital literacy barriers"},
        ]
    )

    aia.set_system_details(
        tech_specs={
            "model_type": "NLP (Conversational AI - RAG)",
            "algorithms": "Fine-tuned LLM with Retrieval Augmented Generation",
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
            "decision_authority": "Information provision only"
        },
        procurement={"method": "Co-developed with external partner"},
        related_assessments={"pia_ref": "DHS-PIA-CB-03", "other_assessments": "Security Assessment Ref: SA-CB-03"}
    )

    # Section 3: Inherent Risk — Medium overall
    aia.set_inherent_risk("Fairness", "Possible", "Moderate",
        "Potential for bias based on training data. Language model tested, some demographic performance variance noted.")
    aia.set_inherent_risk("Reliability and Safety", "Possible", "Moderate",
        "Generally reliable but susceptible to hallucinations. Guardrails in place.")
    aia.set_inherent_risk("Privacy and Security", "Unlikely", "Moderate",
        "Anonymised logs used. No PII collection via chatbot itself. PIA completed.")
    aia.set_inherent_risk("Transparency and Explainability", "Possible", "Moderate",
        "RAG architecture helps trace sources but LLM reasoning isn't fully explainable.")
    aia.set_inherent_risk("Contestability", "Unlikely", "Moderate",
        "Users can request human review via escalation button. Process documented.")
    aia.set_inherent_risk("Human Oversight", "Unlikely", "Minor",
        "Human-in-the-loop for escalation. Regular review of conversation logs.")
    aia.set_inherent_risk("Accountability", "Unlikely", "Minor",
        "Conversations logged (anonymised). Escalation pathway tracked.")

    # Sections 5-11: Full Assessment
    aia.set_full_assessment("Fairness",
        assessment="Potential for bias based on training data where website content may have implicit biases. Language model tested with diverse user personas.",
        controls="Demographic testing during development. Bias monitoring in production.",
        mitigations="Implement targeted testing with diverse user personas. Fine-tune on augmented data.",
        residual_risk="Low")
    aia.set_full_assessment("Reliability and Safety",
        assessment="Generally reliable but susceptible to hallucinations or off-topic conversations.",
        controls="Guardrails, input sanitization, confidence thresholds.",
        mitigations="Enhanced safety filters. Increased human QA sample rate.",
        residual_risk="Low")
    aia.set_full_assessment("Privacy and Security",
        assessment="Anonymised logs used. No PII collection via chatbot.",
        controls="PIA completed. Standard cloud security. Access controls.",
        mitigations="Regular security reviews aligned with SA-CB-03.",
        residual_risk="Low")
    aia.set_full_assessment("Transparency and Explainability",
        assessment="RAG architecture helps trace info sources but LLM reasoning not fully explainable.",
        controls="Response confidence scores used. Source citations displayed.",
        mitigations="Enhance RAG source citation display. Provide clearer 'Why this answer?' explanations.",
        residual_risk="Low")
    aia.set_full_assessment("Contestability",
        assessment="Users can escalate to human agents. Process documented internally.",
        controls="Escalation button available. Response includes 'Talk to a person' option.",
        mitigations="Improve escalation visibility. Add feedback mechanism.",
        residual_risk="Low")
    aia.set_full_assessment("Human Oversight",
        assessment="Human-in-the-loop for escalation. Regular review of conversation logs by dedicated team.",
        controls="Monthly review cycle. Automated escalation rate monitoring.",
        mitigations="Increase sampling frequency for QA reviews.",
        residual_risk="Low")
    aia.set_full_assessment("Accountability",
        assessment="Conversations logged. Escalation pathway tracked. Clear ownership structure.",
        controls="Audit trail maintained. Team responsible identified.",
        mitigations="Formalise reporting structure to governance committee.",
        residual_risk="Low")

    # Mitigations
    aia.add_mitigation_item("Fairness", "Demographic performance variance", "Implement targeted testing with diverse user personas. Fine-tune model on augmented data.", "AI Ethics & Dev Team", "2026-06-30", "Planned")
    aia.add_mitigation_item("Transparency and Explainability", "LLM reasoning opaque", "Enhance RAG source citation display. Provide users with clearer explanations.", "Dev Team", "2026-07-31", "Planned")
    aia.add_mitigation_item("Reliability and Safety", "Misleading info risk", "Strengthen safety filters. Increase human QA sample rate for responses.", "QA & Policy Team", "2026-05-30", "In Progress")

    # Approval
    aia.set_approval(
        assessing_officer={"name": "Dr. Evelyn Reed", "position": "AI Ethics Lead", "date": "2026-02-10"},
        approving_officer={"name": "Marcus Webb", "position": "Director, Digital Channels", "date": "2026-03-05",
                          "decision": "Approved with Conditions", "conditions": "Mitigation plan must be actioned by target dates."},
    )
    aia.set_links(inventory_ref="DHS-AI-015")
    aia.set_monitoring(plan_ref="Chatbot Monitoring Plan v2", frequency="Monthly Review Cycle", next_date="2026-05-01")
    aia.last_assessment_date = "2026-02-10"

    aia.set_aia_status("Review")
    aia.set_related_assessment_status("PIA", "Completed")
    aia.set_related_assessment_status("Security Assessment", "Completed")
    aia.set_related_assessment_status("Human Rights Assessment", "Not Started")

    return aia


# --- Example 3: High Risk — Full assessment + DTA notification ---
def create_example_aia_3():
    print("Creating Example 3: High Risk - Compliance Risk Analyser")
    aia = AlgorithmicImpactAssessment(
        system_name="Regulated Entity Risk Analyser (RERA)",
        agency_name="National Compliance Agency"
    )

    # Section 1
    aia.set_basic_info(
        reference_id="NCA-AIA-001",
        ai_technology_type="Ensemble / Hybrid",
        usage_pattern="Decision support/recommendation",
        use_case_description="Analyses regulated entity data submissions to identify potential non-compliance indicators and prioritise entities for audit/inspection. Assists human decision-makers — does not make autonomous decisions.",
        accountable_use_case_owner={"name": "Dr. James Morton", "email": "james.morton@compliance.gov.au", "position": "Director, Analytics & Intelligence"},
        assessing_officer={"name": "Compliance AI Working Group", "email": "ai-wg@compliance.gov.au", "position": "Cross-functional Team"},
        approving_officer={"name": "Catherine Zhou", "email": "catherine.zhou@compliance.gov.au", "position": "First Assistant Secretary, Compliance Operations"},
        accountable_official={"name": "Robert Langley", "email": "robert.langley@compliance.gov.au", "position": "Deputy Secretary Compliance (SES Band 2)"},
    )

    aia.set_scope_determination(
        criteria_met=[0, 1, 2, 5, 6],
        is_in_scope=True,
        rationale="System directly supports compliance decisions affecting regulated entities. Processes sensitive commercial data in a regulatory context and influences audit selection."
    )

    # Section 2
    aia.set_purpose_and_benefits(
        purpose="Analyses regulated entity data submissions to identify potential non-compliance indicators and prioritise entities for audit/inspection.",
        problem_statement="Manual review of all regulated entity submissions is resource-intensive and inconsistent. Risk-based prioritisation enables more effective use of limited audit resources.",
        non_ai_alternatives="Manual review with basic rule-based filtering. Random sampling for audit selection. Both approaches were less effective at identifying genuine non-compliance.",
        expected_benefits="More effective identification of non-compliance. Consistent application of risk indicators. Reduced time per audit selection decision by 60%.",
        stakeholders=[
            {"name": "Regulated entities", "impact": "negative", "description": "May be selected for audit based on AI risk scoring — financial/reputational consequences"},
            {"name": "Internal Audit/Compliance staff", "impact": "positive", "description": "Better prioritised workload, clearer risk indicators"},
            {"name": "General public", "impact": "positive", "description": "Improved regulatory compliance benefits public interest"},
            {"name": "Legal/advocacy groups", "impact": "both", "description": "Interest in fairness and transparency of audit selection"},
        ]
    )

    aia.set_system_details(
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
            "target_users_affected": "Regulated entities (indirectly), Internal Audit/Compliance staff (directly)",
            "decision_authority": "Decision support/recommendation requiring human approval"
        },
        procurement={"method": "Developed in-house with specialist contractor support"},
        related_assessments={"pia_ref": "NCA-PIA-RERA-01", "other_assessments": "Security Assessment: SA-RERA-01 (High); Human Rights Assessment: HRA-RERA-01"}
    )

    # Section 3: Inherent Risk — High overall
    aia.set_inherent_risk("Fairness", "Likely", "Major",
        "High risk of bias (proxy discrimination) based on historical data. Extensive fairness testing conducted but residual risk remains.")
    aia.set_inherent_risk("Reliability and Safety", "Possible", "Major",
        "Ensemble approach improves reliability but edge cases exist for unusual entity types.")
    aia.set_inherent_risk("Privacy and Security", "Possible", "Moderate",
        "Processes sensitive commercial data. Access controls stringent. PIA completed.")
    aia.set_inherent_risk("Transparency and Explainability", "Likely", "Moderate",
        "Ensemble model complex. SHAP values & Rule Engine tracing provide partial explanations.")
    aia.set_inherent_risk("Contestability", "Likely", "Major",
        "Entities can contest audit findings but contesting the selection for audit is difficult.")
    aia.set_inherent_risk("Human Oversight", "Unlikely", "Moderate",
        "Human audit teams make final decisions. Mandatory senior review for AI-flagged high-risk cases.")
    aia.set_inherent_risk("Accountability", "Unlikely", "Minor",
        "Full audit trail of data inputs, model outputs, user overrides, and final decisions.")

    # Sections 5-11: Full Assessment
    aia.set_full_assessment("Fairness",
        assessment="High risk of bias (proxy discrimination) based on historical data or data gaps. Extensive fairness testing conducted, mitigations implemented but residual risk remains.",
        controls="Fairness metrics monitoring. Protected attribute analysis. Bias testing framework.",
        mitigations="Post-processing fairness adjustments. Annual external fairness audit. Ongoing data improvement strategy.",
        residual_risk="Medium")
    aia.set_full_assessment("Reliability and Safety",
        assessment="Ensemble approach improves reliability but edge cases exist.",
        controls="Model validation framework. Performance monitoring. Error handling.",
        mitigations="Enhanced testing for edge cases. Regular retraining schedule.",
        residual_risk="Low")
    aia.set_full_assessment("Privacy and Security",
        assessment="Processes sensitive commercial data. Deployed in high-security environment.",
        controls="Access controls. Encryption at rest and in transit. PIA completed.",
        mitigations="Ongoing vulnerability management. Regular penetration testing.",
        residual_risk="Low")
    aia.set_full_assessment("Transparency and Explainability",
        assessment="Ensemble model complex. SHAP values and Rule Engine tracing provide partial explanations.",
        controls="SHAP value generation for each prediction. Rule Engine output documentation.",
        mitigations="Develop simplified explanation summaries for audit teams. Pilot counterfactual explanation methods.",
        residual_risk="Medium")
    aia.set_full_assessment("Contestability",
        assessment="Entities can contest audit findings, but contesting selection for audit is difficult.",
        controls="Formal complaints process. Internal review mechanisms.",
        mitigations="Improve documentation justifying audit selection. Establish internal review panel for selection methodology.",
        residual_risk="Medium")
    aia.set_full_assessment("Human Oversight",
        assessment="Human audit teams make final decisions. Strong oversight protocols.",
        controls="Mandatory senior review for AI-flagged high-risk cases. Override capability.",
        mitigations="Enhanced training for audit teams on AI limitations.",
        residual_risk="Low")
    aia.set_full_assessment("Accountability",
        assessment="Full audit trail of data inputs, model outputs, user overrides, and final decisions.",
        controls="Comprehensive logging. Clear governance structure. Ethics Committee oversight.",
        mitigations="Publish high-level methodology transparency report. Ongoing stakeholder engagement.",
        residual_risk="Low")

    # Mitigations
    aia.add_mitigation_item("Fairness", "Residual bias risk", "Implement post-processing fairness adjustments. Conduct annual external fairness audit.", "AI Governance & Stats Team", "2026-08-30", "Planned")
    aia.add_mitigation_item("Transparency and Explainability", "Complex model explanations", "Develop simplified explanation summaries for audit teams. Pilot counterfactual methods.", "AI Dev & User Training Team", "2026-10-31", "Planned")
    aia.add_mitigation_item("Contestability", "Audit selection contestability", "Improve justification documentation. Establish internal review panel.", "Legal & Compliance Policy", "2026-09-30", "Planned")
    aia.add_mitigation_item("Fairness", "Fairness/Proportionality concerns", "Ongoing stakeholder engagement. Publish high-level methodology transparency report.", "Ethics Committee & Comms", "Ongoing", "In Progress")

    # Approval
    aia.set_approval(
        assessing_officer={"name": "Compliance AI WG", "position": "Cross-functional Team", "date": "2026-01-20"},
        approving_officer={"name": "Catherine Zhou", "position": "FAS, Compliance Operations", "date": "2026-03-15",
                          "decision": "Approved with Conditions",
                          "conditions": "Approval contingent on mitigation plan execution and monitoring."},
        accountable_official={"name": "Robert Langley", "position": "Deputy Secretary (SES Band 2)", "date": "2026-04-10",
                             "decision": "Approved with Conditions",
                             "conditions": "Strict adherence to oversight protocols & mitigation plan. Annual review by Ethics Committee."},
    )
    aia.set_links(inventory_ref="NCA-AI-001", transparency_link="Published: nca.gov.au/transparency/ai-rera")
    aia.referenced_frameworks = "NCA AI Governance Policy, National AI Assurance Framework, ISO 23894"

    aia.set_monitoring(plan_ref="RERA Monitoring & Evaluation Framework v1", frequency="Quarterly Performance & Fairness Review", next_date="2026-07-15")
    aia.last_assessment_date = "2026-01-20"

    # DTA notification (mandatory for High risk)
    aia.set_dta_notification(notified=True, notification_date="2026-04-15")

    aia.set_aia_status("Approved")
    aia.set_related_assessment_status("PIA", "Completed")
    aia.set_related_assessment_status("Security Assessment", "Completed")
    aia.set_related_assessment_status("Human Rights Assessment", "Completed")

    return aia


# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting DB Population Script (Policy v2.0) ---")

    db.init_db()

    example_aias = []

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

    for aia_obj in example_aias:
        try:
            print(f"\nProcessing: {aia_obj.system_name}")
            system_id = db.add_system(aia_obj.system_name, aia_obj.agency_name)
            aia_obj.system_id = system_id
            db.update_aia(aia_obj)
            print(f"Successfully added/updated {aia_obj.system_name} in the database.")
        except Exception as e:
            print(f"Error processing {aia_obj.system_name} for database: {e}")

    print("\n--- DB Population Script Finished ---")
