# app.py
# Main Streamlit application for AI Register & Impact Assessment System
# Aligned with DTA Policy for the Responsible Use of AI in Government v2.0

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_oauth import OAuth2Component
import datetime
import json
import requests

# Import db functions and AIA class
import db_manager as db
from aia_core import (
    AlgorithmicImpactAssessment, INHERENT_RISK_AREAS, RISK_RATINGS,
    LIKELIHOOD_LEVELS, CONSEQUENCE_LEVELS, RISK_ACTIONS,
    IN_SCOPE_CRITERIA, USAGE_PATTERNS, AI_TECHNOLOGY_TYPES,
    AI_ETHICS_PRINCIPLES, POLICY_VERSION
)
from auth_manager import get_auth_manager, Permissions

# --- App Configuration ---
st.set_page_config(layout="wide", page_title="AI Register & Impact Assessment System")

# --- Google OAuth Setup ---
try:
    CLIENT_ID = st.secrets["google_auth"]["client_id"]
    CLIENT_SECRET = st.secrets["google_auth"]["client_secret"]
    REDIRECT_URI = st.secrets["google_auth"]["redirect_uri"]
except KeyError as e:
    st.error(f"Missing Google OAuth credential in secrets.toml: {e}")
    st.info("""
    Create a .streamlit/secrets.toml file with the following structure:

    [google_auth]
    client_id = "YOUR_GOOGLE_CLIENT_ID"
    client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
    redirect_uri = "http://localhost:8501"
    """)
    st.stop()

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"

oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, TOKEN_URL, REVOKE_URL)

# Initialize auth manager
auth_manager = get_auth_manager()

# Check if token exists in session state
if 'token' not in st.session_state:
    st.write("Please log in to access the AI Register & Impact Assessment System.")
    result = oauth2.authorize_button(
        name="Login with Google",
        icon="https://www.google.com.tw/favicon.ico",
        redirect_uri=REDIRECT_URI,
        scope="openid email profile",
        key="google_login",
        extras_params={"prompt": "consent", "access_type": "offline"},
        use_container_width=True
    )
    if result:
        token_info = result.get('token')
        access_token = token_info.get('access_token')
        st.session_state.token = access_token
        try:
            user_info_response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_info_response.raise_for_status()
            user_info = user_info_response.json()
            st.session_state.user_email = user_info.get('email')
            st.session_state.user_name = user_info.get('name')
            user = auth_manager.authenticate_user(st.session_state.user_email)
            if not user:
                auth_manager.add_user(
                    email=st.session_state.user_email,
                    name=st.session_state.user_name,
                    role='viewer', agency=''
                )
                user = auth_manager.get_user(st.session_state.user_email)
            st.session_state.user_role = user.role
        except Exception as e:
            st.error(f"Error fetching user info: {e}")
            st.session_state.user_email = None
            st.session_state.user_name = None
            st.session_state.user_role = None
        st.rerun()
else:
    access_token = st.session_state['token']

    if 'user_email' not in st.session_state or not st.session_state.user_email:
        try:
            user_info_response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_info_response.raise_for_status()
            user_info = user_info_response.json()
            st.session_state.user_email = user_info.get('email')
            st.session_state.user_name = user_info.get('name')
            user = auth_manager.authenticate_user(st.session_state.user_email)
            if not user:
                auth_manager.add_user(
                    email=st.session_state.user_email,
                    name=st.session_state.user_name,
                    role='viewer', agency=''
                )
                user = auth_manager.get_user(st.session_state.user_email)
            st.session_state.user_role = user.role
        except Exception as e:
            st.error(f"Error fetching user info: {e}")
            st.session_state.user_email = None
            st.session_state.user_name = None
            st.session_state.user_role = None
            if st.button("Retry"):
                st.rerun()
            st.stop()

    current_user = auth_manager.get_user(st.session_state.user_email)
    if not current_user:
        st.error("User not found in system. Please log out and try again.")
        if st.button("Logout", key="error_logout_button"):
            for key in ['token', 'user_email', 'user_name', 'user_role']:
                st.session_state.pop(key, None)
            st.rerun()
        st.stop()

    # Display user info in sidebar
    st.sidebar.write(f"Logged in as: {current_user.name} ({current_user.email})")
    st.sidebar.write(f"Role: **{current_user.role.replace('_', ' ').title()}**")

    if st.sidebar.button("Logout", key="logout_button"):
        for key in ['token', 'user_email', 'user_name', 'user_role']:
            st.session_state.pop(key, None)
        st.rerun()

    # --- Initialize Session State ---
    if 'view' not in st.session_state:
        st.session_state.view = 'register'
    if 'selected_system_id' not in st.session_state:
        st.session_state.selected_system_id = None
    if 'current_aia' not in st.session_state:
        st.session_state.current_aia = None

    # --- Sidebar Navigation ---
    with st.sidebar:
        st.title("AI Governance Hub")
        st.caption(f"Policy v{POLICY_VERSION}")
        st.write("Navigation")

        if current_user.has_permission(Permissions.VIEW_DASHBOARD):
            if st.button("Dashboard", use_container_width=True,
                        type=("primary" if st.session_state.view == 'dashboard' else "secondary")):
                st.session_state.view = 'dashboard'
                st.session_state.selected_system_id = None
                st.session_state.current_aia = None
                st.rerun()

        if current_user.has_permission(Permissions.VIEW_REGISTER):
            if st.button("AI Use Case Register", use_container_width=True,
                        type=("primary" if st.session_state.view == 'register' else "secondary")):
                st.session_state.view = 'register'
                st.session_state.selected_system_id = None
                st.session_state.current_aia = None
                st.rerun()

        if current_user.has_permission(Permissions.DTA_EXPORT):
            if st.button("DTA Export", use_container_width=True,
                        type=("primary" if st.session_state.view == 'dta_export' else "secondary")):
                st.session_state.view = 'dta_export'
                st.session_state.selected_system_id = None
                st.session_state.current_aia = None
                st.rerun()

        if current_user.has_permission(Permissions.MANAGE_USERS):
            if st.button("User Management", use_container_width=True,
                        type=("primary" if st.session_state.view == 'user_management' else "secondary")):
                st.session_state.view = 'user_management'
                st.session_state.selected_system_id = None
                st.session_state.current_aia = None
                st.rerun()

        st.divider()

        # Add New Use Case
        if current_user.has_permission(Permissions.ADD_SYSTEM):
            st.subheader("Add New AI Use Case")
            with st.form("new_system_form"):
                new_sys_name = st.text_input("Use Case Name")
                registered_systems = db.get_system_list()
                default_agency = registered_systems[0]['agency_name'] if registered_systems else "Example Agency"
                new_agency_name = st.text_input("Agency/Dept Name", value=default_agency)
                submitted = st.form_submit_button("Add Use Case")
                if submitted and new_sys_name:
                    try:
                        new_id = db.add_system(new_sys_name, new_agency_name)
                        st.success(f"Added '{new_sys_name}'. Select it from the register to start the assessment.")
                        st.session_state.selected_system_id = new_id
                        st.session_state.view = 'edit_aia'
                        st.session_state.current_aia = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding use case: {e}")
                elif submitted:
                    st.warning("Please enter a Use Case Name.")

    # =========================================================================
    # MAIN CONTENT AREA
    # =========================================================================

    # == USER MANAGEMENT VIEW ==
    if st.session_state.view == 'user_management':
        if not current_user.has_permission(Permissions.MANAGE_USERS):
            st.error("You don't have permission to manage users.")
            st.stop()

        st.title("User Management")
        st.write("Manage user accounts and roles.")

        users = auth_manager.get_all_users()
        user_data = []
        for user in users:
            user_data.append({
                "Email": user.email,
                "Name": user.name,
                "Role": user.role.replace('_', ' ').title(),
                "Agency": user.agency,
                "Created": user.created_at[:10] if user.created_at else "",
                "Last Login": user.last_login[:10] if user.last_login else ""
            })
        if user_data:
            st.dataframe(pd.DataFrame(user_data), use_container_width=True)

        st.subheader("Add New User")
        with st.form("add_user_form"):
            new_email = st.text_input("Email")
            new_name = st.text_input("Name")
            role_options = ["viewer", "assessor", "reviewer", "accountable_official", "admin"]
            new_role = st.selectbox("Role", options=role_options,
                                   format_func=lambda x: x.replace('_', ' ').title())
            new_agency = st.text_input("Agency/Department")
            submitted = st.form_submit_button("Add User")
            if submitted:
                if new_email and new_name:
                    if auth_manager.get_user(new_email):
                        st.error(f"User with email {new_email} already exists.")
                    else:
                        success = auth_manager.add_user(new_email, new_name, new_role, new_agency)
                        if success:
                            st.success(f"Added user {new_name} ({new_email}) as {new_role.replace('_', ' ').title()}.")
                            st.rerun()
                        else:
                            st.error("Failed to add user.")
                else:
                    st.warning("Please enter both email and name.")

        st.subheader("Edit User")
        edit_email = st.selectbox("Select User to Edit", options=[user.email for user in users])
        if edit_email:
            user_to_edit = auth_manager.get_user(edit_email)
            if user_to_edit:
                with st.form("edit_user_form"):
                    edit_name = st.text_input("Name", value=user_to_edit.name)
                    role_options = ["viewer", "assessor", "reviewer", "accountable_official", "admin"]
                    current_idx = role_options.index(user_to_edit.role) if user_to_edit.role in role_options else 0
                    edit_role = st.selectbox("Role", options=role_options, index=current_idx,
                                           format_func=lambda x: x.replace('_', ' ').title())
                    edit_agency = st.text_input("Agency/Department", value=user_to_edit.agency)
                    submitted = st.form_submit_button("Update User")
                    if submitted and edit_name:
                        success = auth_manager.update_user(edit_email, edit_name, edit_role, edit_agency)
                        if success:
                            st.success(f"Updated user {edit_name}.")
                            st.rerun()

        st.subheader("Delete User")
        delete_email = st.selectbox("Select User to Delete",
                                    options=[user.email for user in users if user.email != current_user.email])
        if delete_email:
            if st.button(f"Delete User {delete_email}", type="primary"):
                confirm = st.checkbox("Confirm deletion")
                if confirm:
                    if auth_manager.delete_user(delete_email):
                        st.success(f"Deleted user {delete_email}.")
                        st.rerun()

    # == DTA EXPORT VIEW ==
    elif st.session_state.view == 'dta_export':
        if not current_user.has_permission(Permissions.DTA_EXPORT):
            st.error("You don't have permission to access DTA exports.")
            st.stop()

        st.title("DTA Register Export")
        st.write("Export the AI register for 6-monthly DTA reporting as required by Policy v2.0.")

        st.subheader("High-Risk Use Cases Requiring DTA Notification")
        high_risk = db.get_high_risk_systems()
        if high_risk:
            st.warning(f"{len(high_risk)} high-risk use case(s) have not been reported to DTA.")
            st.dataframe(pd.DataFrame(high_risk), use_container_width=True)
        else:
            st.success("All high-risk use cases have been reported to DTA.")

        st.subheader("Overdue Reviews")
        overdue = db.get_overdue_reviews()
        if overdue:
            st.warning(f"{len(overdue)} use case(s) are overdue for review (>12 months).")
            st.dataframe(pd.DataFrame(overdue), use_container_width=True)
        else:
            st.success("No overdue reviews.")

        st.divider()
        st.subheader("Download Register Export")
        st.write("Export all in-scope use cases as CSV for DTA submission.")
        csv_data = db.get_dta_export()
        st.download_button(
            label="Download DTA Register CSV",
            data=csv_data,
            file_name=f"DTA_AI_Register_Export_{datetime.date.today().isoformat()}.csv",
            mime="text/csv",
            type="primary"
        )

    # == REGISTER VIEW ==
    elif st.session_state.view == 'register':
        if not current_user.has_permission(Permissions.VIEW_REGISTER):
            st.error("You don't have permission to view the register.")
            st.stop()

        st.title("AI Use Case Register")
        st.write("List of all registered AI use cases and their assessment status.")

        systems_list = db.get_system_list()

        if not systems_list:
            st.info("No AI use cases registered yet. Add one using the sidebar.")
        else:
            df_systems = pd.DataFrame(systems_list)

            # Select display columns for the register view
            display_cols = {
                'system_id': 'ID',
                'system_name': 'Use Case Name',
                'agency_name': 'Agency',
                'aia_status': 'Status',
                'inherent_risk_rating': 'Inherent Risk',
                'residual_risk_rating': 'Residual Risk',
                'usage_pattern': 'Usage Pattern',
                'accountable_owner_name': 'Accountable Owner',
                'is_in_scope': 'In Scope',
                'last_modified_date': 'Last Modified',
            }
            df_display = df_systems[[c for c in display_cols.keys() if c in df_systems.columns]].copy()
            df_display.rename(columns=display_cols, inplace=True)

            # Format in-scope column
            if 'In Scope' in df_display.columns:
                df_display['In Scope'] = df_display['In Scope'].map(
                    {1: 'Yes', 0: 'No', None: 'Not Screened'})

            try:
                df_display['Last Modified'] = pd.to_datetime(df_display['Last Modified']).dt.strftime('%Y-%m-%d %H:%M')
            except Exception:
                pass

            st.dataframe(df_display, use_container_width=True)

            # Selection
            system_options = [f"{row['system_id']}: {row['system_name']}" for _, row in df_systems.iterrows()]
            selected_system = st.selectbox("Select a use case to view details:", options=system_options)

            if selected_system:
                selected_id = int(selected_system.split(":")[0])
                if st.button("Go to Details", key="go_details"):
                    if current_user.has_permission(Permissions.VIEW_AIA):
                        st.session_state.selected_system_id = selected_id
                        st.session_state.view = 'edit_aia'
                        st.session_state.current_aia = None
                        st.rerun()
                    else:
                        st.error("You don't have permission to view use case details.")

    # == DASHBOARD VIEW ==
    elif st.session_state.view == 'dashboard':
        if not current_user.has_permission(Permissions.VIEW_DASHBOARD):
            st.error("You don't have permission to view the dashboard.")
            st.stop()

        st.title("Executive Dashboard")
        st.caption(f"DTA Policy for the Responsible Use of AI in Government v{POLICY_VERSION}")

        dashboard_data = db.get_dashboard_data()

        if not dashboard_data or dashboard_data['total_systems'] == 0:
            st.warning("No data available. Register AI use cases and complete assessments.")
        else:
            # Key Metrics
            st.subheader("Key Metrics")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Registered", dashboard_data['total_systems'])
            col2.metric("In Scope", dashboard_data.get('in_scope_count', 0))
            col3.metric("High Inherent Risk", dashboard_data.get('high_risk_count', 0))

            approved_count = dashboard_data.get('by_status', {}).get('Approved', 0)
            col4.metric("Approved", approved_count)

            # Compliance indicators
            st.subheader("Compliance Status")
            col1, col2, col3 = st.columns(3)
            not_screened = dashboard_data.get('not_screened_count', 0)
            col1.metric("Not Yet Screened", not_screened,
                        delta=f"-{not_screened}" if not_screened > 0 else None,
                        delta_color="inverse")

            high_risk_unreported = len(db.get_high_risk_systems())
            col2.metric("High Risk (DTA Not Notified)", high_risk_unreported,
                        delta=f"-{high_risk_unreported}" if high_risk_unreported > 0 else None,
                        delta_color="inverse")

            overdue_count = len(db.get_overdue_reviews())
            col3.metric("Overdue Reviews (>12 months)", overdue_count,
                        delta=f"-{overdue_count}" if overdue_count > 0 else None,
                        delta_color="inverse")

            # Charts
            st.subheader("Visualizations")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Assessment Status**")
                status_data = dashboard_data.get('by_status', {})
                if status_data:
                    fig_status = px.pie(names=list(status_data.keys()),
                                       values=list(status_data.values()),
                                       title="Assessment Status Distribution", hole=0.3)
                    fig_status.update_layout(margin=dict(l=0, r=0, t=40, b=0))
                    st.plotly_chart(fig_status, use_container_width=True)

                st.markdown("**In-Scope Determination**")
                scope_data = {
                    "In Scope": dashboard_data.get('in_scope_count', 0),
                    "Out of Scope": dashboard_data.get('out_scope_count', 0),
                    "Not Screened": dashboard_data.get('not_screened_count', 0),
                }
                scope_data = {k: v for k, v in scope_data.items() if v > 0}
                if scope_data:
                    fig_scope = px.pie(names=list(scope_data.keys()),
                                      values=list(scope_data.values()),
                                      title="Scope Determination", hole=0.3,
                                      color_discrete_sequence=['#2ca02c', '#7f7f7f', '#ff7f0e'])
                    fig_scope.update_layout(margin=dict(l=0, r=0, t=40, b=0))
                    st.plotly_chart(fig_scope, use_container_width=True)

            with col2:
                st.markdown("**Inherent Risk Distribution**")
                risk_data = dashboard_data.get('by_inherent_risk', {})
                risk_order = ["Low", "Medium", "High", "Not Assessed"]
                ordered_risk = {k: risk_data.get(k, 0) for k in risk_order if risk_data.get(k, 0) > 0}
                if ordered_risk:
                    df_risk = pd.DataFrame(list(ordered_risk.items()), columns=['Risk Rating', 'Count'])
                    fig_risk = px.bar(df_risk, x='Risk Rating', y='Count',
                                    title="Inherent Risk Distribution",
                                    color='Risk Rating',
                                    color_discrete_map={
                                        'Low': '#2ca02c', 'Medium': '#ff7f0e',
                                        'High': '#d62728', 'Not Assessed': '#7f7f7f'
                                    })
                    fig_risk.update_layout(margin=dict(l=0, r=0, t=40, b=0), showlegend=False)
                    st.plotly_chart(fig_risk, use_container_width=True)

                st.markdown("**Residual Risk Distribution**")
                res_data = dashboard_data.get('by_residual_risk', {})
                ordered_res = {k: res_data.get(k, 0) for k in risk_order if res_data.get(k, 0) > 0}
                if ordered_res:
                    df_res = pd.DataFrame(list(ordered_res.items()), columns=['Risk Rating', 'Count'])
                    fig_res = px.bar(df_res, x='Risk Rating', y='Count',
                                   title="Residual Risk Distribution",
                                   color='Risk Rating',
                                   color_discrete_map={
                                       'Low': '#2ca02c', 'Medium': '#ff7f0e',
                                       'High': '#d62728', 'Not Assessed': '#7f7f7f'
                                   })
                    fig_res.update_layout(margin=dict(l=0, r=0, t=40, b=0), showlegend=False)
                    st.plotly_chart(fig_res, use_container_width=True)

    # == EDIT AIA VIEW ==
    elif st.session_state.view == 'edit_aia':
        if not current_user.has_permission(Permissions.VIEW_AIA):
            st.error("You don't have permission to view use case details.")
            st.button("Back to Register", on_click=lambda: setattr(st.session_state, 'view', 'register'))
            st.stop()

        if st.session_state.selected_system_id is None:
            st.error("No use case selected. Please go back to the Register.")
            if st.button("Back to Register"):
                st.session_state.view = 'register'
                st.rerun()
            st.stop()

        # Load the AIA object
        if st.session_state.current_aia is None or st.session_state.current_aia.system_id != st.session_state.selected_system_id:
            st.session_state.current_aia = db.get_aia_object(st.session_state.selected_system_id)
            if st.session_state.current_aia is None:
                st.error(f"Could not load data for system ID {st.session_state.selected_system_id}.")
                if st.button("Back to Register"):
                    st.session_state.view = 'register'
                    st.session_state.selected_system_id = None
                    st.rerun()
                st.stop()

        aia = st.session_state.current_aia
        can_edit = current_user.has_permission(Permissions.EDIT_AIA)

        st.title(f"AI Impact Assessment: {aia.system_name}")
        st.caption(f"ID: {aia.system_id} | Policy v{getattr(aia, 'policy_version', '2.0')} | Status: {aia.aia_status}")

        # --- Status Bar ---
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Assessment Status**")
            if current_user.has_permission(Permissions.CHANGE_STATUS):
                allowed_statuses = ["Draft", "Screening", "Threshold", "Full Assessment",
                                   "Review", "Approved", "Archived"]
                current_idx = allowed_statuses.index(aia.aia_status) if aia.aia_status in allowed_statuses else 0
                new_status = st.selectbox("Status", options=allowed_statuses,
                                         index=current_idx, label_visibility="collapsed")
                if new_status != aia.aia_status:
                    try:
                        aia.set_aia_status(new_status)
                    except ValueError as e:
                        st.error(e)
            else:
                st.write(f"**{aia.aia_status}**")

        with col2:
            inherent = getattr(aia, 'inherent_risk_rating', 'Not Assessed')
            color = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}.get(inherent, 'gray')
            st.markdown(f"**Inherent Risk:** :{color}[{inherent}]")

        with col3:
            residual = getattr(aia, 'residual_risk_rating', 'Not Assessed')
            color = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}.get(residual, 'gray')
            st.markdown(f"**Residual Risk:** :{color}[{residual}]")

        st.divider()

        # --- Tabs aligned to DTA 12-section structure ---
        tab_basic, tab_purpose, tab_risk, tab_threshold, tab_full, tab_mitigations, tab_approval, tab_monitoring, tab_report = st.tabs([
            "1. Basic Info", "2. Purpose & Benefits", "3. Inherent Risk",
            "4. Threshold", "5-11. Full Assessment", "12. Mitigations",
            "Approval", "Monitoring", "Report"
        ])

        # === TAB 1: Basic Information ===
        with tab_basic:
            st.header("Section 1: Basic Information")

            if can_edit:
                aia.system_name = st.text_input("Use Case Name", value=aia.system_name, key="e_name")
                aia.agency_name = st.text_input("Agency/Department", value=aia.agency_name, key="e_agency")
                aia.reference_id = st.text_input("Reference ID", value=getattr(aia, 'reference_id', ''), key="e_refid",
                                                 help="Unique identifier for this assessment")
                aia.use_case_description = st.text_area("Use Case Description (plain language)",
                    value=getattr(aia, 'use_case_description', ''), height=100, key="e_desc")

                col1, col2 = st.columns(2)
                with col1:
                    tech_types = AI_TECHNOLOGY_TYPES
                    current_tech = getattr(aia, 'ai_technology_type', '')
                    tech_idx = tech_types.index(current_tech) if current_tech in tech_types else 0
                    aia.ai_technology_type = st.selectbox("AI Technology Type", options=tech_types,
                                                         index=tech_idx, key="e_techtype")
                with col2:
                    patterns = USAGE_PATTERNS
                    current_pat = getattr(aia, 'usage_pattern', '')
                    pat_idx = patterns.index(current_pat) if current_pat in patterns else 0
                    aia.usage_pattern = st.selectbox("Usage Pattern", options=patterns,
                                                    index=pat_idx, key="e_usage")

                # Accountability roles
                st.subheader("Accountability Roles")
                st.caption("Required by DTA Policy v2.0")

                owner = getattr(aia, 'accountable_use_case_owner', {"name": "", "email": "", "position": ""})
                col1, col2, col3 = st.columns(3)
                with col1:
                    owner['name'] = st.text_input("Accountable Use Case Owner - Name",
                                                  value=owner.get('name', ''), key="e_owner_name")
                with col2:
                    owner['email'] = st.text_input("Owner Email", value=owner.get('email', ''), key="e_owner_email")
                with col3:
                    owner['position'] = st.text_input("Owner Position", value=owner.get('position', ''), key="e_owner_pos")
                aia.accountable_use_case_owner = owner

                ao = getattr(aia, 'assessing_officer', {"name": "", "email": "", "position": ""})
                col1, col2, col3 = st.columns(3)
                with col1:
                    ao['name'] = st.text_input("Assessing Officer - Name", value=ao.get('name', ''), key="e_ao_name")
                with col2:
                    ao['email'] = st.text_input("AO Email", value=ao.get('email', ''), key="e_ao_email")
                with col3:
                    ao['position'] = st.text_input("AO Position", value=ao.get('position', ''), key="e_ao_pos")
                aia.assessing_officer = ao

                appo = getattr(aia, 'approving_officer', {"name": "", "email": "", "position": ""})
                col1, col2, col3 = st.columns(3)
                with col1:
                    appo['name'] = st.text_input("Approving Officer - Name", value=appo.get('name', ''), key="e_appo_name")
                with col2:
                    appo['email'] = st.text_input("Approving Officer Email", value=appo.get('email', ''), key="e_appo_email")
                with col3:
                    appo['position'] = st.text_input("Approving Officer Position", value=appo.get('position', ''), key="e_appo_pos")
                aia.approving_officer = appo

                acc_off = getattr(aia, 'accountable_official', {"name": "", "email": "", "position": ""})
                col1, col2, col3 = st.columns(3)
                with col1:
                    acc_off['name'] = st.text_input("Accountable Official - Name", value=acc_off.get('name', ''), key="e_accoff_name")
                with col2:
                    acc_off['email'] = st.text_input("Accountable Official Email", value=acc_off.get('email', ''), key="e_accoff_email")
                with col3:
                    acc_off['position'] = st.text_input("Accountable Official Position", value=acc_off.get('position', ''), key="e_accoff_pos")
                aia.accountable_official = acc_off

                # In-scope screening
                st.subheader("In-Scope Determination")
                st.caption("Assess against Appendix C criteria to determine if this use case is in scope of the AI Policy.")

                criteria_met = getattr(aia, 'in_scope_criteria_met', [])
                selected_criteria = []
                for i, criterion in enumerate(IN_SCOPE_CRITERIA):
                    checked = st.checkbox(criterion, value=(i in criteria_met), key=f"e_scope_{i}")
                    if checked:
                        selected_criteria.append(i)
                aia.in_scope_criteria_met = selected_criteria

                is_in_scope = len(selected_criteria) > 0
                aia.is_in_scope = is_in_scope
                if is_in_scope:
                    st.success("This use case is IN SCOPE of the AI Policy. Proceed with the impact assessment.")
                else:
                    st.info("This use case does not meet any in-scope criteria. It may be OUT OF SCOPE.")

                aia.scope_determination_rationale = st.text_area(
                    "Scope Determination Rationale",
                    value=getattr(aia, 'scope_determination_rationale', ''), key="e_scope_rat")

                # Technical details
                st.subheader("Technical Specifications")
                col1, col2 = st.columns(2)
                with col1:
                    aia.technical_specs['model_type'] = st.text_input("AI Model Type",
                        value=aia.technical_specs.get('model_type', ''), key="e_modeltype")
                    aia.technical_specs['language_libs'] = st.text_input("Languages & Libraries",
                        value=aia.technical_specs.get('language_libs', ''), key="e_langlibs")
                with col2:
                    aia.technical_specs['algorithms'] = st.text_input("Algorithms Used",
                        value=aia.technical_specs.get('algorithms', ''), key="e_algos")
                    aia.technical_specs['hardware_infra'] = st.text_input("Hardware & Infrastructure",
                        value=aia.technical_specs.get('hardware_infra', ''), key="e_infra")

                st.subheader("Data Sources and Characteristics")
                aia.data_details['sources'] = st.text_area("Data Sources",
                    value=aia.data_details.get('sources', ''), height=80, key="e_datasrc")
                col1, col2 = st.columns(2)
                with col1:
                    aia.data_details['volume_velocity'] = st.text_input("Volume & Velocity",
                        value=aia.data_details.get('volume_velocity', ''), key="e_datavol")
                    aia.data_details['retention_policy'] = st.text_input("Retention Policy",
                        value=aia.data_details.get('retention_policy', ''), key="e_dataret")
                with col2:
                    aia.data_details['types'] = st.text_input("Data Types",
                        value=aia.data_details.get('types', ''), key="e_datatype")

                st.subheader("Deployment Context")
                aia.deployment_context['operational_env'] = st.text_area("Operational Environment",
                    value=aia.deployment_context.get('operational_env', ''), height=80, key="e_depenv")
                aia.deployment_context['target_users_affected'] = st.text_area("Target Users / Affected Groups",
                    value=aia.deployment_context.get('target_users_affected', ''), height=80, key="e_depusers")
                da_options = ["Fully automated decision", "Decision support/recommendation requiring human approval",
                             "Information provision only", "Content generation for review"]
                current_da = aia.deployment_context.get('decision_authority', '')
                da_idx = da_options.index(current_da) if current_da in da_options else 0
                aia.deployment_context['decision_authority'] = st.selectbox(
                    "Decision-Making Authority", options=da_options, index=da_idx, key="e_depauth")

                st.subheader("Procurement")
                aia.procurement['method'] = st.text_input("Procurement Method",
                    value=aia.procurement.get('method', ''), key="e_procmethod")
                aia.procurement['ethical_reqs'] = st.text_area("AI Ethical/Risk Requirements in Procurement",
                    value=aia.procurement.get('ethical_reqs', ''), height=80, key="e_procethic")

            else:
                # Read-only view
                st.write(f"**Use Case Name:** {aia.system_name}")
                st.write(f"**Agency:** {aia.agency_name}")
                st.write(f"**Reference ID:** {getattr(aia, 'reference_id', '')}")
                st.write(f"**Description:** {getattr(aia, 'use_case_description', '')}")
                st.write(f"**AI Technology Type:** {getattr(aia, 'ai_technology_type', '')}")
                st.write(f"**Usage Pattern:** {getattr(aia, 'usage_pattern', '')}")

                st.subheader("Accountability Roles")
                owner = getattr(aia, 'accountable_use_case_owner', {})
                st.write(f"**Accountable Use Case Owner:** {owner.get('name', '')} ({owner.get('email', '')})")
                ao = getattr(aia, 'assessing_officer', {})
                st.write(f"**Assessing Officer:** {ao.get('name', '')} ({ao.get('email', '')})")

                st.subheader("In-Scope Determination")
                scope = getattr(aia, 'is_in_scope', None)
                st.write(f"**In Scope:** {'Yes' if scope else 'No' if scope is False else 'Not Yet Determined'}")

        # === TAB 2: Purpose and Expected Benefits ===
        with tab_purpose:
            st.header("Section 2: Purpose and Expected Benefits")

            if can_edit:
                aia.system_purpose = st.text_area("Purpose", value=aia.system_purpose, height=120, key="e_purpose")
                aia.problem_statement = st.text_area("Problem Statement",
                    value=getattr(aia, 'problem_statement', ''), height=100, key="e_problem",
                    help="What problem does this AI use case solve?")
                aia.non_ai_alternatives = st.text_area("Non-AI Alternatives Considered",
                    value=getattr(aia, 'non_ai_alternatives', ''), height=100, key="e_nonai",
                    help="What alternatives to AI were considered?")
                aia.expected_benefits = st.text_area("Expected Benefits",
                    value=getattr(aia, 'expected_benefits', ''), height=100, key="e_benefits")

                # Stakeholders
                st.subheader("Stakeholders")
                stakeholders = getattr(aia, 'stakeholders', [])
                if not stakeholders:
                    stakeholders = []

                for i, s in enumerate(stakeholders):
                    col1, col2, col3, col4 = st.columns([3, 2, 4, 1])
                    with col1:
                        s['name'] = st.text_input("Stakeholder", value=s.get('name', ''), key=f"e_sh_name_{i}")
                    with col2:
                        impact_opts = ["positive", "negative", "both"]
                        imp_idx = impact_opts.index(s.get('impact', 'positive')) if s.get('impact') in impact_opts else 0
                        s['impact'] = st.selectbox("Impact", options=impact_opts, index=imp_idx, key=f"e_sh_imp_{i}")
                    with col3:
                        s['description'] = st.text_input("Description", value=s.get('description', ''), key=f"e_sh_desc_{i}")
                    with col4:
                        if st.button("Remove", key=f"e_sh_del_{i}"):
                            stakeholders.pop(i)
                            aia.stakeholders = stakeholders
                            st.rerun()

                if st.button("Add Stakeholder", key="e_add_sh"):
                    stakeholders.append({"name": "", "impact": "positive", "description": ""})
                aia.stakeholders = stakeholders

                # Related assessments
                st.subheader("Related Assessments")
                allowed_rel_statuses = ["Not Started", "In Progress", "Completed", "N/A"]
                for key in ["PIA", "Security Assessment", "Human Rights Assessment"]:
                    if key not in aia.related_assessment_statuses:
                        aia.related_assessment_statuses[key] = "Not Started"

                for assessment, status in aia.related_assessment_statuses.items():
                    new_status = st.selectbox(f"{assessment}", options=allowed_rel_statuses,
                        index=allowed_rel_statuses.index(status), key=f"e_relstatus_{assessment}")
                    if new_status != status:
                        aia.set_related_assessment_status(assessment, new_status)

                aia.related_assessments['pia_ref'] = st.text_input("PIA Reference/Link",
                    value=aia.related_assessments.get('pia_ref', ''), key="e_piaref")
                aia.related_assessments['other_assessments'] = st.text_area("Other Assessments",
                    value=aia.related_assessments.get('other_assessments', ''), height=80, key="e_otherassess")

            else:
                st.write(f"**Purpose:** {aia.system_purpose}")
                st.write(f"**Problem Statement:** {getattr(aia, 'problem_statement', '')}")
                st.write(f"**Non-AI Alternatives:** {getattr(aia, 'non_ai_alternatives', '')}")
                st.write(f"**Expected Benefits:** {getattr(aia, 'expected_benefits', '')}")
                st.subheader("Stakeholders")
                for s in getattr(aia, 'stakeholders', []):
                    st.write(f"- {s.get('name', '')} ({s.get('impact', '')}): {s.get('description', '')}")

        # === TAB 3: Inherent Risk Assessment ===
        with tab_risk:
            st.header("Section 3: Inherent Risk Assessment")
            st.markdown("Assess inherent risks (before mitigations) for each AI Ethics Principle area using likelihood and consequence.")

            inherent_risks = getattr(aia, 'inherent_risks', {})
            # Ensure all areas exist
            for area in INHERENT_RISK_AREAS:
                if area not in inherent_risks:
                    inherent_risks[area] = {"likelihood": "", "consequence": "", "rating": "", "justification": ""}

            for area in INHERENT_RISK_AREAS:
                st.subheader(area)
                r = inherent_risks[area]

                if can_edit:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        lik_options = [""] + LIKELIHOOD_LEVELS
                        lik_idx = lik_options.index(r['likelihood']) if r['likelihood'] in lik_options else 0
                        new_lik = st.selectbox(f"Likelihood ({area})", options=lik_options,
                                              index=lik_idx, key=f"e_lik_{area}")
                    with col2:
                        con_options = [""] + CONSEQUENCE_LEVELS
                        con_idx = con_options.index(r['consequence']) if r['consequence'] in con_options else 0
                        new_con = st.selectbox(f"Consequence ({area})", options=con_options,
                                              index=con_idx, key=f"e_con_{area}")
                    with col3:
                        # Auto-calculated rating
                        if new_lik and new_con:
                            from aia_core import RISK_MATRIX
                            calc_rating = RISK_MATRIX.get((new_lik, new_con), "")
                            color = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}.get(calc_rating, 'gray')
                            st.markdown(f"**Rating:** :{color}[{calc_rating}]")
                        else:
                            st.markdown("**Rating:** Not set")
                            calc_rating = ""

                    justification = st.text_area(f"Justification ({area})",
                        value=r.get('justification', ''), height=80, key=f"e_just_{area}")

                    # Update if changed
                    if new_lik != r['likelihood'] or new_con != r['consequence'] or justification != r.get('justification', ''):
                        try:
                            aia.set_inherent_risk(area,
                                                 likelihood=new_lik if new_lik else "",
                                                 consequence=new_con if new_con else "",
                                                 justification=justification)
                        except ValueError as e:
                            st.error(str(e))
                else:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Likelihood:** {r.get('likelihood', '-')}")
                    with col2:
                        st.write(f"**Consequence:** {r.get('consequence', '-')}")
                    with col3:
                        st.write(f"**Rating:** {r.get('rating', '-')}")
                    st.write(f"**Justification:** {r.get('justification', '')}")

            # Overall inherent risk summary
            st.divider()
            aia._update_overall_inherent_risk()
            rating = getattr(aia, 'inherent_risk_rating', 'Not Assessed')
            color = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}.get(rating, 'gray')
            st.markdown(f"### Overall Inherent Risk: :{color}[{rating}]")
            action = RISK_ACTIONS.get(rating, '')
            if action:
                st.info(f"**Required Action:** {action}")

        # === TAB 4: Threshold Decision ===
        with tab_threshold:
            st.header("Section 4: Threshold Decision")

            threshold = getattr(aia, 'threshold_decision', {})
            requires_full = threshold.get('requires_full_assessment')
            inherent = getattr(aia, 'inherent_risk_rating', 'Not Assessed')

            if inherent == 'Low':
                st.success("All inherent risks are rated LOW. You can seek approving officer endorsement to conclude the assessment.")
                st.markdown("Proceed with the use case with appropriate plans for monitoring, evaluation, and re-validation.")
            elif inherent in ('Medium', 'High'):
                st.warning(f"Inherent risk is **{inherent}**. A full assessment (Sections 5-11) is required.")
                if inherent == 'High':
                    st.error("HIGH RISK: Must report to agency Accountable Official and notify DTA.")
            else:
                st.info("Complete the Inherent Risk Assessment (Section 3) first.")

            if can_edit and current_user.has_permission(Permissions.SET_THRESHOLD):
                st.subheader("Threshold Endorsement")
                threshold['endorsed_by'] = st.text_input("Endorsed By (Approving Officer)",
                    value=threshold.get('endorsed_by', ''), key="e_thresh_by")
                thresh_date = threshold.get('endorsement_date', '')
                thresh_date_val = datetime.date.fromisoformat(thresh_date) if thresh_date else None
                new_thresh_date = st.date_input("Endorsement Date", value=thresh_date_val, key="e_thresh_date")
                threshold['endorsement_date'] = new_thresh_date.isoformat() if new_thresh_date else ""
                threshold['rationale'] = st.text_area("Rationale",
                    value=threshold.get('rationale', ''), height=100, key="e_thresh_rat")
                aia.threshold_decision = threshold
            else:
                st.write(f"**Endorsed By:** {threshold.get('endorsed_by', '[Not Set]')}")
                st.write(f"**Date:** {threshold.get('endorsement_date', '[Not Set]')}")
                st.write(f"**Rationale:** {threshold.get('rationale', '[Not Set]')}")

        # === TAB 5-11: Full Assessment ===
        with tab_full:
            st.header("Sections 5-11: Full Assessment")

            requires_full = getattr(aia, 'threshold_decision', {}).get('requires_full_assessment')
            if requires_full is False:
                st.info("Full assessment not required — all inherent risks are Low.")
            else:
                st.markdown("Detailed assessment for each AI Ethics Principle area. Document existing controls, proposed mitigations, and residual risk.")

                full_assessment = getattr(aia, 'full_assessment', {})
                section_num = 5
                for area in INHERENT_RISK_AREAS:
                    if area not in full_assessment:
                        full_assessment[area] = {"assessment": "", "controls": "", "mitigations": "", "residual_risk": ""}

                    fa = full_assessment[area]
                    inherent_r = getattr(aia, 'inherent_risks', {}).get(area, {}).get('rating', '')

                    st.subheader(f"Section {section_num}: {area}")
                    if inherent_r:
                        color = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}.get(inherent_r, 'gray')
                        st.caption(f"Inherent risk: :{color}[{inherent_r}]")

                    if can_edit:
                        fa['assessment'] = st.text_area(f"Assessment — {area}",
                            value=fa.get('assessment', ''), height=100, key=f"e_fa_assess_{area}")
                        fa['controls'] = st.text_area(f"Existing Controls — {area}",
                            value=fa.get('controls', ''), height=80, key=f"e_fa_ctrl_{area}")
                        fa['mitigations'] = st.text_area(f"Proposed Mitigations — {area}",
                            value=fa.get('mitigations', ''), height=80, key=f"e_fa_mit_{area}")

                        res_options = [""] + RISK_RATINGS
                        res_idx = res_options.index(fa['residual_risk']) if fa['residual_risk'] in res_options else 0
                        fa['residual_risk'] = st.selectbox(f"Residual Risk — {area}",
                            options=res_options, index=res_idx, key=f"e_fa_res_{area}")

                        if fa['residual_risk']:
                            try:
                                aia.set_full_assessment(area, residual_risk=fa['residual_risk'])
                            except ValueError:
                                pass
                    else:
                        st.write(f"**Assessment:** {fa.get('assessment', '')}")
                        st.write(f"**Controls:** {fa.get('controls', '')}")
                        st.write(f"**Mitigations:** {fa.get('mitigations', '')}")
                        st.write(f"**Residual Risk:** {fa.get('residual_risk', '')}")

                    section_num += 1

                aia.full_assessment = full_assessment

                # Overall residual risk
                aia._update_overall_residual_risk()
                st.divider()
                res_rating = getattr(aia, 'residual_risk_rating', 'Not Assessed')
                color = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}.get(res_rating, 'gray')
                st.markdown(f"### Overall Residual Risk: :{color}[{res_rating}]")

        # === TAB 12: Mitigations ===
        with tab_mitigations:
            st.header("Section 12: Mitigation Plan")

            if can_edit:
                st.subheader("Add New Mitigation Item")
                with st.form(key=f"mit_form_{aia.system_id}", clear_on_submit=True):
                    mit_area = st.selectbox("Risk Area", options=INHERENT_RISK_AREAS, key="e_mit_area")
                    mit_risk = st.text_input("Risk Description", key="e_mit_risk",
                                            placeholder="e.g., Potential bias in training data")
                    mit_action = st.text_area("Proposed Mitigation Action(s)", key="e_mit_action", height=100)
                    mit_resp = st.text_input("Responsible Party/Team", key="e_mit_resp")
                    mit_date = st.date_input("Target Completion Date", key="e_mit_date", value=None)
                    mit_status = st.selectbox("Status", options=["Planned", "In Progress", "Completed", "Cancelled"],
                                            key="e_mit_status")
                    submitted = st.form_submit_button("Add Mitigation Item")
                    if submitted:
                        if mit_area and mit_risk and mit_action and mit_resp and mit_date:
                            aia.add_mitigation_item(
                                risk_area=mit_area,
                                risk_description=mit_risk,
                                action=mit_action,
                                responsible=mit_resp,
                                target_date=mit_date.isoformat(),
                                status=mit_status
                            )
                            st.success("Mitigation item added. Click 'Save Changes' to persist.")
                            st.rerun()
                        else:
                            st.warning("Please fill in all fields.")

            st.divider()
            st.subheader("Existing Mitigation Items")
            if not aia.mitigation_plan:
                st.info("No mitigation items added yet.")
            else:
                for index, item in enumerate(aia.mitigation_plan):
                    item_id = item['id']
                    st.markdown(f"**Item {index + 1}**")
                    cols = st.columns([4, 1]) if can_edit else [st.columns([1])[0]]
                    with cols[0]:
                        st.markdown(f"""
- **Risk Area:** {item.get('risk_area', item.get('dimension', 'N/A'))}
- **Risk Description:** {item.get('risk_description', item.get('risk_score_desc', 'N/A'))}
- **Action:** {item.get('action', 'N/A')}
- **Responsible:** {item.get('responsible', 'N/A')}
- **Target Date:** {item.get('target_date', 'N/A')}
- **Status:** {item.get('status', 'N/A')}
                        """)
                    if can_edit:
                        with cols[1]:
                            if st.button(f"Delete", key=f"del_{item_id}"):
                                try:
                                    aia.remove_mitigation_item(item_id)
                                    st.rerun()
                                except ValueError as e:
                                    st.error(e)
                    st.markdown("---")

        # === TAB: Approval ===
        with tab_approval:
            st.header("Documentation and Approval")

            can_approve = can_edit and current_user.has_permission(Permissions.APPROVE_AIA)

            if can_approve:
                st.subheader("Assessing Officer Sign-off")
                approvals = getattr(aia, 'approvals', {})
                ao = approvals.get('assessing_officer', {})
                ao['name'] = st.text_input("Assessing Officer Name", value=ao.get('name', ''), key="e_app_ao_name")
                ao['position'] = st.text_input("Position", value=ao.get('position', ''), key="e_app_ao_pos")
                ao_date = ao.get('date', '')
                ao_date_val = datetime.date.fromisoformat(ao_date) if ao_date else None
                new_ao_date = st.date_input("Date", value=ao_date_val, key="e_app_ao_date")
                ao['date'] = new_ao_date.isoformat() if new_ao_date else ""
                approvals['assessing_officer'] = ao

                st.subheader("Approving Officer Decision")
                appo = approvals.get('approving_officer', {})
                appo['name'] = st.text_input("Approving Officer Name", value=appo.get('name', ''), key="e_app_appo_name")
                appo['position'] = st.text_input("Position", value=appo.get('position', ''), key="e_app_appo_pos")
                appo_date = appo.get('date', '')
                appo_date_val = datetime.date.fromisoformat(appo_date) if appo_date else None
                new_appo_date = st.date_input("Date", value=appo_date_val, key="e_app_appo_date")
                appo['date'] = new_appo_date.isoformat() if new_appo_date else ""
                dec_options = ["", "Approved", "Approved with Conditions", "Rejected"]
                dec_idx = dec_options.index(appo.get('decision', '')) if appo.get('decision', '') in dec_options else 0
                appo['decision'] = st.selectbox("Decision", options=dec_options, index=dec_idx, key="e_app_appo_dec")
                appo['conditions'] = st.text_area("Conditions (if any)", value=appo.get('conditions', ''),
                                                  height=80, key="e_app_appo_cond")
                approvals['approving_officer'] = appo

                st.subheader("Accountable Official (for Medium/High Risk)")
                acc = approvals.get('accountable_official', {})
                acc['name'] = st.text_input("Accountable Official Name", value=acc.get('name', ''), key="e_app_acc_name")
                acc['position'] = st.text_input("Position", value=acc.get('position', ''), key="e_app_acc_pos")
                acc_date = acc.get('date', '')
                acc_date_val = datetime.date.fromisoformat(acc_date) if acc_date else None
                new_acc_date = st.date_input("Date", value=acc_date_val, key="e_app_acc_date")
                acc['date'] = new_acc_date.isoformat() if new_acc_date else ""
                acc_dec_options = ["", "Approved", "Approved with Conditions", "Rejected"]
                acc_dec_idx = acc_dec_options.index(acc.get('decision', '')) if acc.get('decision', '') in acc_dec_options else 0
                acc['decision'] = st.selectbox("Decision", options=acc_dec_options, index=acc_dec_idx, key="e_app_acc_dec")
                acc['conditions'] = st.text_area("Conditions (if any)", value=acc.get('conditions', ''),
                                                 height=80, key="e_app_acc_cond")
                approvals['accountable_official'] = acc
                aia.approvals = approvals

                st.subheader("Links & References")
                aia.ai_inventory_ref = st.text_input("Agency AI Inventory Reference",
                    value=aia.ai_inventory_ref, key="e_inv_ref")
                aia.transparency_statement_link = st.text_input("Transparency Statement Link",
                    value=aia.transparency_statement_link, key="e_transp_link")
                aia.referenced_frameworks = st.text_input("Referenced Frameworks",
                    value=aia.referenced_frameworks, key="e_frameworks")

                # DTA Notification
                if getattr(aia, 'inherent_risk_rating', '') == 'High':
                    st.subheader("DTA Notification (Mandatory for High Risk)")
                    dta_notified = st.checkbox("DTA has been notified",
                        value=getattr(aia, 'dta_notified', False), key="e_dta_notified")
                    aia.dta_notified = dta_notified
                    if dta_notified:
                        dta_date = getattr(aia, 'dta_notification_date', '')
                        dta_date_val = datetime.date.fromisoformat(dta_date) if dta_date else datetime.date.today()
                        new_dta_date = st.date_input("Notification Date", value=dta_date_val, key="e_dta_date")
                        aia.dta_notification_date = new_dta_date.isoformat()

            else:
                # Read-only approval view
                approvals = getattr(aia, 'approvals', {})
                st.subheader("Assessing Officer")
                ao = approvals.get('assessing_officer', {})
                st.write(f"**Name:** {ao.get('name', '')}, **Position:** {ao.get('position', '')}, **Date:** {ao.get('date', '')}")

                st.subheader("Approving Officer")
                appo = approvals.get('approving_officer', {})
                st.write(f"**Name:** {appo.get('name', '')}, **Position:** {appo.get('position', '')}, **Date:** {appo.get('date', '')}")
                st.write(f"**Decision:** {appo.get('decision', '')}")
                st.write(f"**Conditions:** {appo.get('conditions', '')}")

                st.subheader("Accountable Official")
                acc = approvals.get('accountable_official', {})
                st.write(f"**Name:** {acc.get('name', '')}, **Position:** {acc.get('position', '')}")
                st.write(f"**Decision:** {acc.get('decision', '')}")

                st.subheader("Links")
                st.write(f"**AI Inventory Ref:** {aia.ai_inventory_ref}")
                st.write(f"**Transparency Statement:** {aia.transparency_statement_link}")

        # === TAB: Monitoring ===
        with tab_monitoring:
            st.header("Ongoing Monitoring and Review")
            st.caption("DTA Policy requires a minimum 12-month review cycle.")

            if can_edit:
                aia.monitoring_plan_ref = st.text_input("Monitoring Plan Reference",
                    value=aia.monitoring_plan_ref, key="e_mon_plan")
                aia.review_frequency = st.text_input("Review Frequency",
                    value=aia.review_frequency, placeholder="e.g., Every 12 months", key="e_mon_freq")
                next_review = aia.next_review_date
                next_review_val = datetime.date.fromisoformat(next_review) if next_review else None
                new_next_review = st.date_input("Next Scheduled Review Date", value=next_review_val, key="e_mon_next")
                aia.next_review_date = new_next_review.isoformat() if new_next_review else ""

                last_assess = getattr(aia, 'last_assessment_date', '')
                last_assess_val = datetime.date.fromisoformat(last_assess) if last_assess else None
                new_last_assess = st.date_input("Last Assessment Date", value=last_assess_val, key="e_mon_last")
                aia.last_assessment_date = new_last_assess.isoformat() if new_last_assess else ""

                st.info("Remember: Re-validate the assessment when there is a material change in scope, usage, or operation.")
            else:
                st.write(f"**Monitoring Plan Reference:** {aia.monitoring_plan_ref}")
                st.write(f"**Review Frequency:** {aia.review_frequency}")
                st.write(f"**Next Scheduled Review Date:** {aia.next_review_date}")
                st.write(f"**Last Assessment Date:** {getattr(aia, 'last_assessment_date', '')}")

        # === TAB: Report ===
        with tab_report:
            st.header("Full Impact Assessment Report")
            st.info("This is a generated report of the current assessment data. Save changes before relying on this report.")
            aia._update_risk_assessment()
            report_text = aia.generate_report()
            st.markdown(f"```markdown\n{report_text}\n```")

            if current_user.has_permission(Permissions.EXPORT_AIA):
                st.download_button(
                    label="Download Report as Text File",
                    data=report_text,
                    file_name=f"AI_Impact_Assessment_{''.join(c if c.isalnum() else '_' for c in aia.system_name)}_{datetime.date.today().isoformat()}.txt",
                    mime="text/plain"
                )

        # --- Save Button ---
        st.divider()
        if can_edit and st.button("Save Changes to Database", key="save_aia", type="primary"):
            try:
                aia._update_risk_assessment()
                aia.last_modified_date = datetime.datetime.now().isoformat()
                db.update_aia(aia)
                st.success(f"Assessment for '{aia.system_name}' saved successfully!")
            except Exception as e:
                st.error(f"Error saving: {e}")
                st.exception(e)

        # --- Delete Button ---
        if current_user.has_permission(Permissions.DELETE_SYSTEM):
            st.divider()
            st.subheader("Delete Use Case")
            st.warning("Deleting a use case is permanent and cannot be undone.")
            if st.button(f"Delete '{aia.system_name}'", key="delete_aia"):
                confirm_delete = st.checkbox(f"Confirm deletion of '{aia.system_name}'", key="confirm_delete")
                if confirm_delete:
                    if db.delete_system(aia.system_id):
                        st.success(f"Use case '{aia.system_name}' deleted.")
                        st.session_state.view = 'register'
                        st.session_state.selected_system_id = None
                        st.session_state.current_aia = None
                        st.rerun()
