# app.py
# Main Streamlit application for AI Register & AIA System

import streamlit as st
import pandas as pd
import plotly.express as px # For better charts
from streamlit_oauth import OAuth2Component
import datetime
import json # Required if debugging aia object directly
import requests # For making API calls to Google

# Import db functions and AIA class
import db_manager as db
from aia_core import AlgorithmicImpactAssessment, DIMENSIONS, ETHICS_PRINCIPLES_MAP # Import necessary items
# Import auth manager for role-based authorization
from auth_manager import get_auth_manager, Permissions

# --- App Configuration ---
st.set_page_config(layout="wide", page_title="AI Register & AIA System")

# --- Google OAuth Setup ---
# Load credentials from secrets
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
    redirect_uri = "http://localhost:8501" # Or your deployed app URL
    """)
    st.stop()

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"

# Create OAuth2Component instance
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, TOKEN_URL, REVOKE_URL)

# Initialize auth manager
auth_manager = get_auth_manager()

# Check if token exists in session state
if 'token' not in st.session_state:
    # If not, show authorize button
    st.write("Please log in to access the AIA Dashboard.")
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
        # If authorization successful, save token in session state
        token_info = result.get('token')
        access_token = token_info.get('access_token')
        st.session_state.token = access_token
        
        # Get user info from Google
        try:
            user_info_response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_info_response.raise_for_status()
            user_info = user_info_response.json()
            
            # Store user info in session state
            st.session_state.user_email = user_info.get('email')
            st.session_state.user_name = user_info.get('name')
            
            # Authenticate user with our system
            user = auth_manager.authenticate_user(st.session_state.user_email)
            if not user:
                # If user doesn't exist, add them as a viewer
                auth_manager.add_user(
                    email=st.session_state.user_email,
                    name=st.session_state.user_name,
                    role='viewer',
                    agency=''
                )
                user = auth_manager.get_user(st.session_state.user_email)
            
            # Store user role in session state
            st.session_state.user_role = user.role
            
        except Exception as e:
            st.error(f"Error fetching user info: {e}")
            st.session_state.user_email = None
            st.session_state.user_name = None
            st.session_state.user_role = None
            
        st.rerun() # Rerun to show authenticated view
else:
    # If token exists in session state, show authenticated view
    access_token = st.session_state['token']
    
    # If we don't have user info yet, fetch it
    if 'user_email' not in st.session_state or not st.session_state.user_email:
        try:
            user_info_response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_info_response.raise_for_status()
            user_info = user_info_response.json()
            
            # Store user info in session state
            st.session_state.user_email = user_info.get('email')
            st.session_state.user_name = user_info.get('name')
            
            # Authenticate user with our system
            user = auth_manager.authenticate_user(st.session_state.user_email)
            if not user:
                # If user doesn't exist, add them as a viewer
                auth_manager.add_user(
                    email=st.session_state.user_email,
                    name=st.session_state.user_name,
                    role='viewer',
                    agency=''
                )
                user = auth_manager.get_user(st.session_state.user_email)
            
            # Store user role in session state
            st.session_state.user_role = user.role
            
        except Exception as e:
            st.error(f"Error fetching user info: {e}")
            st.session_state.user_email = None
            st.session_state.user_name = None
            st.session_state.user_role = None
            if st.button("Retry"):
                st.rerun()
            st.stop()
    
    # Get current user
    current_user = auth_manager.get_user(st.session_state.user_email)
    if not current_user:
        st.error("User not found in system. Please log out and try again.")
        if st.button("Logout", key="error_logout_button"):
            del st.session_state.token
            if 'user_email' in st.session_state:
                del st.session_state.user_email
            if 'user_name' in st.session_state:
                del st.session_state.user_name
            if 'user_role' in st.session_state:
                del st.session_state.user_role
            st.rerun()
        st.stop()
    
    # Display user info in sidebar
    st.sidebar.write(f"Logged in as: {current_user.name} ({current_user.email})")
    st.sidebar.write(f"Role: **{current_user.role.capitalize()}**")
    
    if st.sidebar.button("Logout", key="logout_button"):
        del st.session_state.token
        if 'user_email' in st.session_state:
            del st.session_state.user_email
        if 'user_name' in st.session_state:
            del st.session_state.user_name
        if 'user_role' in st.session_state:
            del st.session_state.user_role
        st.rerun() # Rerun to show login button

    # --- Initialize Session State ---
    if 'view' not in st.session_state:
        st.session_state.view = 'register' # Default view
    if 'selected_system_id' not in st.session_state:
        st.session_state.selected_system_id = None
    if 'current_aia' not in st.session_state:
        st.session_state.current_aia = None # Holds the loaded AIA object for editing
    if 'selected_row_index' not in st.session_state:
        st.session_state.selected_row_index = None # Store selected row index

    # --- Sidebar Navigation ---
    with st.sidebar:
        st.title("AI Governance Hub")
        st.write("Navigation")
        
        # Only show dashboard if user has permission
        if current_user.has_permission(Permissions.VIEW_DASHBOARD):
            if st.button("📊 Dashboard", use_container_width=True, type=("primary" if st.session_state.view == 'dashboard' else "secondary")):
                st.session_state.view = 'dashboard'
                st.session_state.selected_system_id = None # Clear selection when moving away
                st.session_state.current_aia = None
                st.rerun()

        # Only show register if user has permission
        if current_user.has_permission(Permissions.VIEW_REGISTER):
            if st.button(" Acknowledgment Register", use_container_width=True, type=("primary" if st.session_state.view == 'register' else "secondary")):
                st.session_state.view = 'register'
                st.session_state.selected_system_id = None
                st.session_state.current_aia = None
                st.rerun()
        
        # Only show user management if user has permission
        if current_user.has_permission(Permissions.MANAGE_USERS):
            if st.button("👥 User Management", use_container_width=True, type=("primary" if st.session_state.view == 'user_management' else "secondary")):
                st.session_state.view = 'user_management'
                st.session_state.selected_system_id = None
                st.session_state.current_aia = None
                st.rerun()

        st.divider()
        
        # Only show add system if user has permission
        if current_user.has_permission(Permissions.ADD_SYSTEM):
            st.subheader("Add New System")
            with st.form("new_system_form"):
                new_sys_name = st.text_input("System Name")
                # Find default agency name from existing entries or set a placeholder
                registered_systems = db.get_system_list()
                default_agency = registered_systems[0]['agency_name'] if registered_systems else "Example Agency"
                new_agency_name = st.text_input("Agency/Dept Name", value=default_agency)
                submitted = st.form_submit_button("Add System")
                if submitted and new_sys_name:
                    try:
                        new_id = db.add_system(new_sys_name, new_agency_name)
                        st.success(f"Added '{new_sys_name}'. Select it from the register to edit.")
                        # Switch view to edit the newly added system
                        st.session_state.selected_system_id = new_id
                        st.session_state.view = 'edit_aia'
                        st.session_state.current_aia = None # Force reload
                        st.rerun() # Refresh register view
                    except Exception as e:
                        st.error(f"Error adding system: {e}")
                elif submitted:
                    st.warning("Please enter a System Name.")

    # --- Main Content Area ---

    # == USER MANAGEMENT VIEW ==
    if st.session_state.view == 'user_management':
        if not current_user.has_permission(Permissions.MANAGE_USERS):
            st.error("You don't have permission to manage users.")
            st.button("Back to Register", on_click=lambda: setattr(st.session_state, 'view', 'register'))
            st.stop()
            
        st.title("👥 User Management")
        st.write("Manage user accounts and roles.")
        
        # Display existing users
        users = auth_manager.get_all_users()
        
        # Create a dataframe for display
        user_data = []
        for user in users:
            user_data.append({
                "Email": user.email,
                "Name": user.name,
                "Role": user.role.capitalize(),
                "Agency": user.agency,
                "Created": user.created_at[:10] if user.created_at else "",
                "Last Login": user.last_login[:10] if user.last_login else ""
            })
        
        if user_data:
            st.dataframe(pd.DataFrame(user_data), use_container_width=True)
        else:
            st.info("No users found.")
        
        # Add new user form
        st.subheader("Add New User")
        with st.form("add_user_form"):
            new_email = st.text_input("Email")
            new_name = st.text_input("Name")
            new_role = st.selectbox("Role", options=["viewer", "assessor", "reviewer", "admin"])
            new_agency = st.text_input("Agency/Department")
            submitted = st.form_submit_button("Add User")
            
            if submitted:
                if new_email and new_name:
                    if auth_manager.get_user(new_email):
                        st.error(f"User with email {new_email} already exists.")
                    else:
                        success = auth_manager.add_user(new_email, new_name, new_role, new_agency)
                        if success:
                            st.success(f"Added user {new_name} ({new_email}) with role {new_role}.")
                            st.rerun()  # Refresh the user list
                        else:
                            st.error("Failed to add user.")
                else:
                    st.warning("Please enter both email and name.")
        
        # Edit user form
        st.subheader("Edit User")
        edit_email = st.selectbox("Select User to Edit", options=[user.email for user in users])
        if edit_email:
            user_to_edit = auth_manager.get_user(edit_email)
            if user_to_edit:
                with st.form("edit_user_form"):
                    edit_name = st.text_input("Name", value=user_to_edit.name)
                    edit_role = st.selectbox("Role", options=["viewer", "assessor", "reviewer", "admin"], index=["viewer", "assessor", "reviewer", "admin"].index(user_to_edit.role))
                    edit_agency = st.text_input("Agency/Department", value=user_to_edit.agency)
                    submitted = st.form_submit_button("Update User")
                    
                    if submitted:
                        if edit_name:
                            success = auth_manager.update_user(edit_email, edit_name, edit_role, edit_agency)
                            if success:
                                st.success(f"Updated user {edit_name} ({edit_email}).")
                                st.rerun()  # Refresh the user list
                            else:
                                st.error("Failed to update user.")
                        else:
                            st.warning("Please enter a name.")
        
        # Delete user section
        st.subheader("Delete User")
        delete_email = st.selectbox("Select User to Delete", options=[user.email for user in users if user.email != current_user.email])
        if delete_email:
            if st.button(f"Delete User {delete_email}", type="primary"):
                confirm = st.checkbox("Confirm deletion")
                if confirm:
                    success = auth_manager.delete_user(delete_email)
                    if success:
                        st.success(f"Deleted user {delete_email}.")
                        st.rerun()  # Refresh the user list
                    else:
                        st.error("Failed to delete user.")
                else:
                    st.warning("Please confirm deletion.")

    # == REGISTER VIEW ==
    elif st.session_state.view == 'register':
        if not current_user.has_permission(Permissions.VIEW_REGISTER):
            st.error("You don't have permission to view the register.")
            st.stop()
            
        st.title(" AI Use Case Register")
        st.write("List of all registered AI systems and their AIA status.")

        systems_list = db.get_system_list()

        if not systems_list:
            st.info("No AI systems registered yet. Add one using the sidebar.")
        else:
            df_systems = pd.DataFrame(systems_list)
            # Improve display names
            df_systems.rename(columns={
                'system_id': 'ID', 'system_name': 'System Name', 'agency_name': 'Agency',
                'aia_status': 'AIA Status', 'risk_category': 'Risk Category',
                'total_score': 'Total Score', 'last_modified_date': 'Last Modified'
            }, inplace=True)

            # Format date for display
            try:
                df_systems['Last Modified'] = pd.to_datetime(df_systems['Last Modified']).dt.strftime('%Y-%m-%d %H:%M')
            except Exception: # Handle potential errors if date format is unexpected
                pass # Keep original string if conversion fails

            # Display the table
            st.write("AI Systems:")
            st.dataframe(df_systems, use_container_width=True)
            
            # Create a selection dropdown with system names
            system_options = [f"{row['ID']}: {row['System Name']}" for _, row in df_systems.iterrows()]
            selected_system = st.selectbox("Select a system to view details:", options=system_options)
            
            # Extract the ID from the selected option
            if selected_system:
                selected_id = int(selected_system.split(":")[0])
                
                # Button to go to details
                if st.button("Go to Details", key="go_details"):
                    if current_user.has_permission(Permissions.VIEW_AIA):
                        st.session_state.selected_system_id = selected_id
                        st.session_state.view = 'edit_aia'
                        st.session_state.current_aia = None # Clear previous edit object
                        st.rerun()
                    else:
                        st.error("You don't have permission to view AIA details.")

    # == DASHBOARD VIEW ==
    elif st.session_state.view == 'dashboard':
        if not current_user.has_permission(Permissions.VIEW_DASHBOARD):
            st.error("You don't have permission to view the dashboard.")
            st.stop()
            
        st.title(" Executive Dashboard")
        st.write("Overview of the AI register and AIA status.")

        dashboard_data = db.get_dashboard_data()

        if not dashboard_data or dashboard_data['total_systems'] == 0:
            st.warning("No data available for the dashboard. Please register systems and complete AIAs.")
        else:
            # --- Key Metrics ---
            st.subheader("Key Metrics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Registered Systems", dashboard_data['total_systems'])
            # Count approved systems - requires querying db differently or processing list
            approved_count = sum(1 for sys in db.get_system_list() if sys['aia_status'] == 'Approved')
            col2.metric("Approved Systems", approved_count)
            # Count high/severe risk systems
            high_severe_count = sum(1 for sys in db.get_system_list() if sys['risk_category'] in ['High', 'Severe'])
            col3.metric("High/Severe Risk Systems", high_severe_count)

            # --- Charts ---
            st.subheader("Visualizations")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Systems by AIA Status**")
                status_data = dashboard_data.get('by_status', {})
                if status_data:
                    fig_status = px.pie(names=list(status_data.keys()), values=list(status_data.values()),
                                        title="AIA Status Distribution", hole=0.3)
                    fig_status.update_layout(margin=dict(l=0, r=0, t=40, b=0))
                    st.plotly_chart(fig_status, use_container_width=True)
                else:
                    st.caption("No status data.")

                st.markdown("**Systems by PIA Status**")
                pia_data = dashboard_data.get('by_pia_status', {})
                if pia_data:
                    # Ensure consistent category order
                    pia_order = ["Not Started", "In Progress", "Completed", "N/A"]
                    ordered_pia = {k: pia_data.get(k, 0) for k in pia_order if k in pia_data}
                    df_pia = pd.DataFrame(list(ordered_pia.items()), columns=['Status', 'Count'])
                    fig_pia = px.bar(df_pia, x='Status', y='Count', title="PIA Status", color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig_pia.update_layout(margin=dict(l=0, r=0, t=40, b=0))
                    st.plotly_chart(fig_pia, use_container_width=True)
                    # st.bar_chart(df_pia.set_index('Status')) # Simpler alternative
                else:
                    st.caption("No PIA status data.")

            with col2:
                st.markdown("**Systems by Risk Category**")
                risk_data = dashboard_data.get('by_risk', {})
                risk_order = ["Low", "Medium", "High", "Severe", "Undefined"] # Define order
                ordered_risk_data = {k: risk_data.get(k, 0) for k in risk_order if k in risk_data or risk_data.get(k,0) > 0}
                if ordered_risk_data:
                    df_risk = pd.DataFrame(list(ordered_risk_data.items()), columns=['Risk Category', 'Count'])
                    fig_risk = px.bar(df_risk, x='Risk Category', y='Count', title="Risk Category Distribution",
                                    color='Risk Category',
                                    color_discrete_map={'Low':'#2ca02c', 'Medium':'#ff7f0e', 'High':'#d62728', 'Severe':'#8c564b', 'Undefined': '#7f7f7f'}) # Specific colours
                    fig_risk.update_layout(margin=dict(l=0, r=0, t=40, b=0), showlegend=False)
                    st.plotly_chart(fig_risk, use_container_width=True)
                else:
                    st.caption("No risk data.")

                st.markdown("**Systems by Security Assessment Status**")
                sec_data = dashboard_data.get('by_security_status', {})
                if sec_data:
                    sec_order = ["Not Started", "In Progress", "Completed", "N/A"]
                    ordered_sec = {k: sec_data.get(k, 0) for k in sec_order if k in sec_data}
                    df_sec = pd.DataFrame(list(ordered_sec.items()), columns=['Status', 'Count'])
                    fig_sec = px.bar(df_sec, x='Status', y='Count', title="Security Assessment Status", color_discrete_sequence=px.colors.qualitative.Pastel1)
                    fig_sec.update_layout(margin=dict(l=0, r=0, t=40, b=0))
                    st.plotly_chart(fig_sec, use_container_width=True)
                    # st.bar_chart(df_sec.set_index('Status')) # Simpler alternative
                else:
                    st.caption("No Security status data.")

            # --- Stakeholder Views Placeholder ---
            st.divider()
            st.subheader("Stakeholder Filters / Views")
            st.info("Future: Add widgets here to filter the dashboard view based on stakeholder needs.")
            # Example:
            # stakeholders = ["Default", "CDO", "CISO", "CIO/CTO", "Info Gov"]
            # view_as = st.selectbox("View As:", stakeholders)
            # if view_as == "CISO":
            #    st.write("Displaying CISO relevant view (e.g., focusing on Security Assessment Status and High/Severe Risks)")
            #    # Filter data or show specific CISO charts


    # == EDIT AIA VIEW ==
    elif st.session_state.view == 'edit_aia':
        if not current_user.has_permission(Permissions.VIEW_AIA):
            st.error("You don't have permission to view AIA details.")
            st.button("Back to Register", on_click=lambda: setattr(st.session_state, 'view', 'register'))
            st.stop()
            
        if st.session_state.selected_system_id is None:
            st.error("No system selected. Please go back to the Register.")
            if st.button("Back to Register"):
                st.session_state.view = 'register'
                st.rerun()
            st.stop()

        # Load the AIA object for editing if not already loaded or if ID changed
        if st.session_state.current_aia is None or st.session_state.current_aia.system_id != st.session_state.selected_system_id:
            print(f"Loading AIA for system ID: {st.session_state.selected_system_id}") # Debug print
            st.session_state.current_aia = db.get_aia_object(st.session_state.selected_system_id)
            if st.session_state.current_aia is None:
                st.error(f"Could not load AIA data for system ID {st.session_state.selected_system_id}. It might have been deleted.")
                if st.button("Back to Register"):
                    st.session_state.view = 'register'
                    st.session_state.selected_system_id = None
                    st.rerun()
                st.stop() # Stop execution if load fails

        # Get reference to the AIA object being edited
        aia = st.session_state.current_aia

        st.title(f"Edit AIA: {aia.system_name} (ID: {aia.system_id})")

        # --- Status Section ---
        st.divider()
        st.subheader("AIA & Assessment Status")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Overall AIA Status**")
            current_aia_status = aia.aia_status
            allowed_aia_statuses = ["Draft", "In Progress", "Review", "Approved", "Archived"]
            
            # Only allow status change if user has permission
            if current_user.has_permission(Permissions.CHANGE_STATUS):
                new_aia_status = st.selectbox("Overall AIA Status", options=allowed_aia_statuses, index=allowed_aia_statuses.index(current_aia_status), label_visibility="collapsed")
                if new_aia_status != current_aia_status:
                    try:
                        aia.set_aia_status(new_aia_status)
                        # No success message here, wait for save button
                    except ValueError as e:
                        st.error(e)
            else:
                st.write(f"**{current_aia_status}**")
                st.caption("You don't have permission to change the status.")


        with col2:
            st.markdown("**Related Assessment Statuses**")
            allowed_rel_statuses = ["Not Started", "In Progress", "Completed", "N/A"]
            # Ensure all predefined keys exist, add if needed
            for key in ["PIA", "Security Assessment", "Human Rights Assessment"]:
                if key not in aia.related_assessment_statuses:
                    aia.related_assessment_statuses[key] = "Not Started"

            for assessment, status in aia.related_assessment_statuses.items():
                current_status = status
                # Only allow status change if user has permission
                if current_user.has_permission(Permissions.CHANGE_STATUS):
                    new_status = st.selectbox(f"{assessment}", options=allowed_rel_statuses, index=allowed_rel_statuses.index(current_status), key=f"status_{assessment}")
                    if new_status != current_status:
                        try:
                            aia.set_related_assessment_status(assessment, new_status)
                        except ValueError as e:
                            st.error(e)
                else:
                    st.write(f"{assessment}: **{current_status}**")

        if current_user.has_permission(Permissions.EDIT_AIA):
            st.caption("Remember to click 'Save Changes' below to persist status updates.")
        st.divider()


        # --- Re-use Tabs from previous single-AIA app for editing ---
        tab_metadata, tab_sysdesc, tab_impact, tab_summary, tab_mitigation, tab_approval, tab_monitoring, tab_report = st.tabs([
            "Metadata", "System Description", "Impact Assessment", "Summary & Risk", "Mitigation Plan", "Approval", "Monitoring", "Full Report"
        ])

        # Determine if user can edit content
        can_edit = current_user.has_permission(Permissions.EDIT_AIA)
        
        # --- Populate tabs using the 'aia' object ---
        # For each tab, we'll check if the user has edit permission
        # If not, we'll display the data in read-only mode

        with tab_metadata:
            st.header("Metadata and Introduction")
            st.write(f"**AIA Template Version:** {aia.aia_version}")

            # Convert ISO date string to datetime.date object for widget
            try:
                assessment_date_obj = datetime.date.fromisoformat(aia.assessment_date)
            except (ValueError, TypeError):
                assessment_date_obj = datetime.date.today() # Default if invalid

            if can_edit:
                new_assessment_date = st.date_input("Date of Assessment", value=assessment_date_obj)
                aia.assessment_date = new_assessment_date.isoformat() # Store back as string

                assessed_by_str = "\n".join(aia.assessed_by)
                new_assessed_by_str = st.text_area("Assessed By (Name (Role) - one per line)", value=assessed_by_str, height=100, key="edit_assessed_by")
                aia.assessed_by = [line.strip() for line in new_assessed_by_str.split('\n') if line.strip()]

                aia.referenced_frameworks = st.text_input("Referenced Frameworks (Optional)", value=aia.referenced_frameworks, key="edit_frameworks")
                aia.agency_name = st.text_input("Agency Name", value=aia.agency_name, key="edit_agency")
            else:
                st.write(f"**Date of Assessment:** {aia.assessment_date}")
                st.write(f"**Assessed By:**")
                for assessor in aia.assessed_by:
                    st.write(f"- {assessor}")
                st.write(f"**Referenced Frameworks:** {aia.referenced_frameworks}")
                st.write(f"**Agency Name:** {aia.agency_name}")

        with tab_sysdesc:
            st.header("4. System Description")
            
            if can_edit:
                # Allow editing system name? Be cautious as it's used for display elsewhere.
                # Maybe make it read-only here or add a specific 'Rename' feature?
                # For now, allow edit:
                aia.system_name = st.text_input("4.1 System Name", value=aia.system_name, key="edit_sysname")
                aia.system_purpose = st.text_area("4.2 System Purpose and Functionality", value=aia.system_purpose, height=150, key="edit_purpose")

                st.subheader("4.3 Technical Specifications")
                col1, col2 = st.columns(2)
                with col1:
                    aia.technical_specs['model_type'] = st.text_input("AI Model Type", value=aia.technical_specs.get('model_type', ''), key="edit_modeltype")
                    aia.technical_specs['language_libs'] = st.text_input("Programming Language & Libraries", value=aia.technical_specs.get('language_libs', ''), key="edit_langlibs")
                with col2:
                    aia.technical_specs['algorithms'] = st.text_input("Algorithms Used", value=aia.technical_specs.get('algorithms', ''), key="edit_algos")
                    aia.technical_specs['hardware_infra'] = st.text_input("Hardware & Infrastructure", value=aia.technical_specs.get('hardware_infra', ''), key="edit_infra")

                st.subheader("4.4 Data Sources and Characteristics")
                aia.data_details['sources'] = st.text_area("Data Sources", value=aia.data_details.get('sources', ''), height=100, key="edit_datasrc")
                col1, col2 = st.columns(2)
                with col1:
                    aia.data_details['volume_velocity'] = st.text_input("Data Volume and Velocity", value=aia.data_details.get('volume_velocity', ''), key="edit_datavol")
                    aia.data_details['retention_policy'] = st.text_input("Data Retention Policy", value=aia.data_details.get('retention_policy', ''), key="edit_dataret")
                with col2:
                    aia.data_details['types'] = st.text_input("Data Types", value=aia.data_details.get('types', ''), key="edit_datatype")

                st.subheader("4.5 Deployment Context")
                aia.deployment_context['operational_env'] = st.text_area("Operational Environment", value=aia.deployment_context.get('operational_env', ''), height=100, key="edit_depenv")
                aia.deployment_context['target_users_affected'] = st.text_area("Target Users or Affected Individuals/Groups", value=aia.deployment_context.get('target_users_affected', ''), height=100, key="edit_depusers")
                # Existing decision authority or default to first option if empty/invalid
                da_options = ["Fully automated decision", "Decision support/recommendation requiring human approval", "Information provision only", "Content generation for review"]
                current_da_val = aia.deployment_context.get('decision_authority', '')
                try:
                    da_index = da_options.index(current_da_val)
                except ValueError:
                    da_index = 0 # Default to first option if not found
                aia.deployment_context['decision_authority'] = st.selectbox(
                    "Decision-Making Authority",
                    options=da_options,
                    index=da_index,
                    key="edit_depauth"
                )

                st.subheader("4.6 Procurement Method and Context")
                aia.procurement['method'] = st.text_input("Procurement Method", value=aia.procurement.get('method', ''), key="edit_procmethod")
                aia.procurement['ethical_reqs'] = st.text_area("AI Ethical/Risk Requirements in Procurement (if applicable)", value=aia.procurement.get('ethical_reqs', ''), height=100, key="edit_procethic")

                st.subheader("4.7 Related Assessments (Descriptions/References)")
                # Statuses are managed in the status section above
                aia.related_assessments['pia_ref'] = st.text_input("PIA Reference/Link (if applicable)", value=aia.related_assessments.get('pia_ref', ''), key="edit_piaref")
                aia.related_assessments['other_assessments'] = st.text_area("Other Relevant Assessments (Desc./Refs.)", value=aia.related_assessments.get('other_assessments', ''), height=100, key="edit_otherassess")
            else:
                # Read-only view
                st.write(f"**4.1 System Name:** {aia.system_name}")
                st.write(f"**4.2 System Purpose and Functionality:**")
                st.write(aia.system_purpose)
                
                st.subheader("4.3 Technical Specifications")
                st.write(f"**AI Model Type:** {aia.technical_specs.get('model_type', '')}")
                st.write(f"**Programming Language & Libraries:** {aia.technical_specs.get('language_libs', '')}")
                st.write(f"**Algorithms Used:** {aia.technical_specs.get('algorithms', '')}")
                st.write(f"**Hardware & Infrastructure:** {aia.technical_specs.get('hardware_infra', '')}")
                
                st.subheader("4.4 Data Sources and Characteristics")
                st.write(f"**Data Sources:**")
                st.write(aia.data_details.get('sources', ''))
                st.write(f"**Data Volume and Velocity:** {aia.data_details.get('volume_velocity', '')}")
                st.write(f"**Data Retention Policy:** {aia.data_details.get('retention_policy', '')}")
                st.write(f"**Data Types:** {aia.data_details.get('types', '')}")
                
                st.subheader("4.5 Deployment Context")
                st.write(f"**Operational Environment:**")
                st.write(aia.deployment_context.get('operational_env', ''))
                st.write(f"**Target Users or Affected Individuals/Groups:**")
                st.write(aia.deployment_context.get('target_users_affected', ''))
                st.write(f"**Decision-Making Authority:** {aia.deployment_context.get('decision_authority', '')}")
                
                st.subheader("4.6 Procurement Method and Context")
                st.write(f"**Procurement Method:** {aia.procurement.get('method', '')}")
                st.write(f"**AI Ethical/Risk Requirements in Procurement:**")
                st.write(aia.procurement.get('ethical_reqs', ''))
                
                st.subheader("4.7 Related Assessments")
                st.write(f"**PIA Reference/Link:** {aia.related_assessments.get('pia_ref', '')}")
                st.write(f"**Other Relevant Assessments:**")
                st.write(aia.related_assessments.get('other_assessments', ''))

        with tab_impact:
            st.header("5/6. Impact Assessment Dimensions & Justification")
            st.markdown("Rate each dimension from **0 (Negligible Risk)** to **5 (Severe Risk)**.") 

            for dim in DIMENSIONS:
                st.subheader(f"{dim}")
                st.caption(f"*Relevant Australian AI Ethics Principle(s): {ETHICS_PRINCIPLES_MAP.get(dim, '')}*")

                current_score = aia.dimensions[dim]['score']
                current_justification = aia.dimensions[dim]['justification']

                if can_edit:
                    cols = st.columns([1, 3]) # Column for slider, column for justification
                    with cols[0]:
                        # Use unique key for edit view slider
                        new_score = st.slider(f"Score for {dim}", 0, 5, current_score, key=f"edit_score_{dim}_{aia.system_id}")
                    with cols[1]:
                        # Use unique key for edit view text area
                        new_justification = st.text_area(f"Justification for {dim}", value=current_justification, key=f"edit_just_{dim}_{aia.system_id}", height=100)

                    # Update session state object if changes detected using the dedicated method
                    if new_score != current_score or new_justification != current_justification:
                        try:
                            # Call the method which also updates last_modified_date
                            aia.set_dimension_score(dim, new_score, new_justification)
                            # No need to rerun, state is updated directly
                        except ValueError as e:
                            st.error(f"Error updating score for {dim}: {e}")
                else:
                    # Read-only view
                    st.write(f"**Score:** {current_score}/5")
                    st.write(f"**Justification:**")
                    st.write(current_justification)


        with tab_summary:
            st.header("7. Scoring Summary")
            # Ensure calculations are up to date
            aia._update_risk_assessment() # Recalculate based on potentially changed scores

            summary_data = []
            for dim_name, data in aia.dimensions.items():
                principles = ETHICS_PRINCIPLES_MAP.get(dim_name, '')
                summary_data.append({
                    "Dimension": dim_name,
                    "Score (0-5)": data['score'],
                    "Primary Aust. AI Ethics Principle(s)": principles
                })
            st.dataframe(summary_data, hide_index=True, use_container_width=True)
            st.markdown(f"**Total Score:** **{aia.total_score}** / 65")

            st.header("8. Risk Categorization")
            st.metric(label="Overall System Risk Category", value=aia.risk_category['category'])
            st.info(f"**Required Action:** {aia.risk_category['action']}")
            st.caption(f"*(Note: Approval levels should align with {aia.agency_name}'s internal governance and Accountable AI Official responsibilities.)*")


        with tab_mitigation:
            st.header("9. Mitigation Plan")

            if can_edit:
                st.subheader("Add New Mitigation Item")
                # Use unique key for form in edit view if needed, or rely on clear_on_submit
                with st.form(key=f"edit_mitigation_form_{aia.system_id}", clear_on_submit=True):
                    mit_dim = st.selectbox("Dimension", options=DIMENSIONS, key=f"edit_mit_dim_{aia.system_id}")
                    mit_risk = st.text_input("Identified Risk / Score Description", key=f"edit_mit_risk_{aia.system_id}", placeholder="e.g., Potential bias (Score=4)")
                    mit_action = st.text_area("Proposed Mitigation Action(s)", key=f"edit_mit_action_{aia.system_id}", height=100)
                    mit_resp = st.text_input("Responsible Party/Team", key=f"edit_mit_resp_{aia.system_id}")
                    mit_date = st.date_input("Target Completion Date", key=f"edit_mit_date_{aia.system_id}", value=None) # Allow no date initially
                    mit_status = st.selectbox("Status", options=["Planned", "In Progress", "Completed", "Cancelled"], key=f"edit_mit_status_{aia.system_id}")

                    submitted = st.form_submit_button("Add Mitigation Item")
                    if submitted:
                        if mit_dim and mit_risk and mit_action and mit_resp and mit_date:
                            aia.add_mitigation_item( # This updates the aia object in session state
                                dimension=mit_dim,
                                risk_score_desc=mit_risk,
                                action=mit_action,
                                responsible=mit_resp,
                                target_date=mit_date.isoformat(), # Store date as string
                                status=mit_status
                            )
                            st.success("Mitigation item added to current view. Click 'Save Changes' to persist.")
                            st.rerun() # Rerun to update displayed list below
                        else:
                            st.warning("Please fill in all fields (including date) for the mitigation item.")

            st.divider()
            st.subheader("Existing Mitigation Items")
            if not aia.mitigation_plan:
                st.info("No mitigation items added yet.")
            else:
                # Display items with delete buttons if user can edit
                for index, item in enumerate(aia.mitigation_plan):
                    item_id = item['id'] # Get the unique ID
                    st.markdown(f"**Item {index + 1} (ID: `{item_id}`):**")
                    cols = st.columns([4, 1]) if can_edit else [st.columns([1])[0]]
                    with cols[0]:
                        st.markdown(f"""
                            - **Dimension:** {item.get('dimension', 'N/A')}
                            - **Risk/Score:** {item.get('risk_score_desc', 'N/A')}
                            - **Action:** {item.get('action', 'N/A')}
                            - **Responsible:** {item.get('responsible', 'N/A')}
                            - **Target Date:** {item.get('target_date', 'N/A')}
                            - **Status:** {item.get('status', 'N/A')}
                        """)
                    if can_edit:
                        with cols[1]:
                            # Use unique key for delete button
                            if st.button(f"❌ Delete Item {index + 1}", key=f"edit_del_{item_id}"):
                                try:
                                    aia.remove_mitigation_item(item_id) # This updates the aia object in session state
                                    st.success(f"Mitigation item {index + 1} removed from view. Click 'Save Changes' to persist.")
                                    st.rerun() # Rerun to update list
                                except ValueError as e:
                                    st.error(e)
                    st.markdown("---") # Separator

        with tab_approval:
            st.header("10. Documentation and Approval")

            if can_edit and current_user.has_permission(Permissions.APPROVE_AIA):
                st.subheader("Assessor(s)")
                # Ensure unique keys for edit view
                aia.approvals['assessor']['name'] = st.text_input("Assessor Name(s)", value=aia.approvals['assessor'].get('name', ''), key="edit_assessor_name")
                aia.approvals['assessor']['role'] = st.text_input("Assessor Role(s)", value=aia.approvals['assessor'].get('role', ''), key="edit_assessor_role")
                assessor_date_val = datetime.date.fromisoformat(aia.approvals['assessor']['date']) if aia.approvals['assessor'].get('date') else None
                new_assessor_date = st.date_input("Assessor Date", value=assessor_date_val, key="edit_assessor_date")
                aia.approvals['assessor']['date'] = new_assessor_date.isoformat() if new_assessor_date else ""

                st.subheader("Reviewer(s)")
                aia.approvals['reviewer']['name'] = st.text_input("Reviewer Name(s)", value=aia.approvals['reviewer'].get('name', ''), key="edit_reviewer_name")
                aia.approvals['reviewer']['role'] = st.text_input("Reviewer Role(s)", value=aia.approvals['reviewer'].get('role', ''), key="edit_reviewer_role")
                reviewer_date_val = datetime.date.fromisoformat(aia.approvals['reviewer']['date']) if aia.approvals['reviewer'].get('date') else None
                new_reviewer_date = st.date_input("Reviewer Date", value=reviewer_date_val, key="edit_reviewer_date")
                aia.approvals['reviewer']['date'] = new_reviewer_date.isoformat() if new_reviewer_date else ""
                aia.approvals['reviewer']['comments'] = st.text_area("Reviewer Comments", value=aia.approvals['reviewer'].get('comments', ''), height=100, key="edit_reviewer_comments")


                st.subheader("Approver")
                aia.approvals['approver']['name'] = st.text_input("Approver Name", value=aia.approvals['approver'].get('name', ''), key="edit_approver_name")
                aia.approvals['approver']['role'] = st.text_input("Approver Role (Aligned with Risk Category)", value=aia.approvals['approver'].get('role', ''), key="edit_approver_role")
                approver_date_val = datetime.date.fromisoformat(aia.approvals['approver']['date']) if aia.approvals['approver'].get('date') else None
                new_approver_date = st.date_input("Approver Date", value=approver_date_val, key="edit_approver_date")
                aia.approvals['approver']['date'] = new_approver_date.isoformat() if new_approver_date else ""
                # Existing decision or default
                dec_options = ["Approved", "Approved with Conditions", "Rejected"]
                current_dec_val = aia.approvals['approver'].get('decision', '')
                try:
                    dec_index = dec_options.index(current_dec_val)
                except ValueError:
                    dec_index = 0 # Default to first option
                aia.approvals['approver']['decision'] = st.selectbox("Approval Decision", options=dec_options, index=dec_index, key="edit_approver_decision")
                # Handle empty selection if needed
                # if aia.approvals['approver']['decision'] == "[Select...]": aia.approvals['approver']['decision'] = ""
                aia.approvals['approver']['conditions'] = st.text_area("Approval Conditions (if any)", value=aia.approvals['approver'].get('conditions', ''), height=100, key="edit_approver_conditions")


                st.subheader("Links")
                aia.ai_inventory_ref = st.text_input("Agency AI Inventory Reference (if applicable)", value=aia.ai_inventory_ref, key="edit_inv_ref")
                aia.transparency_statement_link = st.text_input("Link to APS AI Transparency Statement (if applicable)", value=aia.transparency_statement_link, key="edit_transp_link")
            else:
                # Read-only view
                st.subheader("Assessor(s)")
                st.write(f"**Name(s):** {aia.approvals['assessor'].get('name', '')}")
                st.write(f"**Role(s):** {aia.approvals['assessor'].get('role', '')}")
                st.write(f"**Date:** {aia.approvals['assessor'].get('date', '')}")
                
                st.subheader("Reviewer(s)")
                st.write(f"**Name(s):** {aia.approvals['reviewer'].get('name', '')}")
                st.write(f"**Role(s):** {aia.approvals['reviewer'].get('role', '')}")
                st.write(f"**Date:** {aia.approvals['reviewer'].get('date', '')}")
                st.write(f"**Comments:**")
                st.write(aia.approvals['reviewer'].get('comments', ''))
                
                st.subheader("Approver")
                st.write(f"**Name:** {aia.approvals['approver'].get('name', '')}")
                st.write(f"**Role:** {aia.approvals['approver'].get('role', '')}")
                st.write(f"**Date:** {aia.approvals['approver'].get('date', '')}")
                st.write(f"**Decision:** {aia.approvals['approver'].get('decision', '')}")
                st.write(f"**Conditions:**")
                st.write(aia.approvals['approver'].get('conditions', ''))
                
                st.subheader("Links")
                st.write(f"**Agency AI Inventory Reference:** {aia.ai_inventory_ref}")
                st.write(f"**Link to APS AI Transparency Statement:** {aia.transparency_statement_link}")


        with tab_monitoring:
            st.header("11. Ongoing Monitoring and Review")
            # Use unique keys for edit view
            if can_edit:
                aia.monitoring_plan_ref = st.text_input("Monitoring Plan Reference", value=aia.monitoring_plan_ref, key="edit_mon_plan")
                aia.review_frequency = st.text_input("Review Frequency", value=aia.review_frequency, placeholder="e.g., Every 12 months", key="edit_mon_freq")
                next_review_date_val = datetime.date.fromisoformat(aia.next_review_date) if aia.next_review_date else None
                new_next_review_date = st.date_input("Next Scheduled Review Date", value=next_review_date_val, key="edit_mon_next_date")
                aia.next_review_date = new_next_review_date.isoformat() if new_next_review_date else ""
            else:
                # Read-only view
                st.write(f"**Monitoring Plan Reference:** {aia.monitoring_plan_ref}")
                st.write(f"**Review Frequency:** {aia.review_frequency}")
                st.write(f"**Next Scheduled Review Date:** {aia.next_review_date}")


        with tab_report:
            st.header("Full AIA Report")
            st.info("This is a generated text version of the current AIA data. Save changes before relying on this report.")
            # Ensure calculations are up to date before generating report
            aia._update_risk_assessment()
            report_text = aia.generate_report()
            st.markdown(f"```markdown\n{report_text}\n```")
            
            # Add a download button for the report text if user has export permission
            if current_user.has_permission(Permissions.EXPORT_AIA):
                st.download_button(
                    label="Download Report as Text File",
                    data=report_text,
                    file_name=f"AIA_Report_{''.join(c if c.isalnum() else '_' for c in aia.system_name)}_{datetime.date.today().isoformat()}.txt",
                    mime="text/plain"
                )


        # --- Save Button ---
        st.divider()
        if can_edit and st.button("💾 Save Changes to Database", key="save_aia", type="primary"):
            try:
                # Ensure latest calculations before saving object state
                aia._update_risk_assessment()
                # Update the last modified date explicitly on save
                aia.last_modified_date = datetime.datetime.now().isoformat()
                db.update_aia(aia) # Pass the modified aia object from session state
                st.success(f"AIA for '{aia.system_name}' updated successfully!")
                # Optionally provide feedback or navigation
            except Exception as e:
                st.error(f"Error saving AIA: {e}")
                st.exception(e) # Show full traceback for debugging

        # --- Delete Button ---
        if current_user.has_permission(Permissions.DELETE_SYSTEM):
            st.divider()
            st.subheader("Delete System")
            st.warning("🚨 Deleting a system is permanent and cannot be undone.")
            if st.button(f"❌ Delete System '{aia.system_name}'", key="delete_aia"):
                confirm_delete = st.checkbox(f"Tick to confirm deletion of '{aia.system_name}'", key="confirm_delete_box")
                if confirm_delete:
                    if db.delete_system(aia.system_id):
                        st.success(f"System '{aia.system_name}' deleted.")
                        # Clear session state related to the deleted item
                        st.session_state.view = 'register'
                        st.session_state.selected_system_id = None
                        st.session_state.current_aia = None
                        st.rerun()
                    else:
                        st.error(f"Failed to delete system {aia.system_id}.")
                else:
                    st.warning("Please tick the confirmation box to delete.")


    # --- Initial App Load Check ---
    # Initialize DB on first run or if module reloaded
    try:
        db.init_db()
    except Exception as e:
        st.error(f"Database initialization failed: {e}")