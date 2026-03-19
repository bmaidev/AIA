"""
Canberra Charities Database - Streamlit Interface
Searchable, filterable interface for 350+ ACT charities and not-for-profits.
Supporting Hands Across Canberra x Black Mountain AI strategic partnership.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
import charity_db as cdb

# --- Page Configuration ---
st.set_page_config(
    layout="wide",
    page_title="Canberra Charities Database | Hands Across Canberra x Black Mountain AI",
    page_icon="🏛️",
)

# --- Initialize Database ---
cdb.init_db()

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555;
        margin-top: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
    }
    .stDataFrame {
        font-size: 0.85rem;
    }
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 0.5rem;
        padding: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
col_logo, col_title = st.columns([1, 5])
with col_title:
    st.markdown('<p class="main-header">Canberra Charities & Not-for-Profits Database</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Hands Across Canberra x Black Mountain AI | Strategic Partnership for Sector Capability Building</p>', unsafe_allow_html=True)

# --- Sidebar Navigation ---
with st.sidebar:
    st.title("Navigation")
    page = st.radio("Go to", [
        "Dashboard",
        "Browse Charities",
        "Search & Filter",
        "Sector Analysis",
        "Functions Map",
        "Board & Leadership",
        "Technology Landscape",
        "Workshop Targeting",
        "Export Data"
    ], label_visibility="collapsed")

    st.divider()
    st.caption("Data Sources: ACNC Register, Hands Across Canberra, Individual Charity Websites")
    st.caption("Last Updated: March 2026")

# --- Get data ---
all_charities = cdb.get_all_charities()
stats = cdb.get_statistics()
sectors = cdb.get_sectors()

# ============================================================
# DASHBOARD PAGE
# ============================================================
if page == "Dashboard":
    st.header("Sector Overview")

    if stats['total_charities'] == 0:
        st.warning("Database is empty. Run the seed script first: `python populate_charities.py`")
        st.stop()

    # Key metrics
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Organisations", stats['total_charities'])
    c2.metric("With CEO Identified", stats['with_ceo'])
    c3.metric("With Board Info", stats['with_board'])
    c4.metric("With Website", stats['with_website'])
    c5.metric("HAC Members", stats['hac_members'])
    c6.metric("Avg Data Completeness", f"{stats['avg_completeness']:.0%}")

    st.divider()

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Charities by Sector")
        if stats['by_sector']:
            df_sector = pd.DataFrame(list(stats['by_sector'].items()), columns=['Sector', 'Count'])
            df_sector = df_sector.sort_values('Count', ascending=True)
            fig = px.bar(df_sector, x='Count', y='Sector', orientation='h',
                        color='Count', color_continuous_scale='Viridis')
            fig.update_layout(height=max(400, len(df_sector) * 25), margin=dict(l=0, r=0, t=10, b=0),
                            showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Organisation Size Distribution")
        if stats['by_size']:
            df_size = pd.DataFrame(list(stats['by_size'].items()), columns=['Size', 'Count'])
            fig2 = px.pie(df_size, names='Size', values='Count', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Set2)
            fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig2, use_container_width=True)

    # Data completeness overview
    st.subheader("Data Completeness")
    completeness_data = []
    for c in all_charities:
        completeness_data.append({
            'Name': c['name'],
            'Sector': c.get('sector', ''),
            'Completeness': c.get('data_completeness', 0)
        })
    df_comp = pd.DataFrame(completeness_data)
    if not df_comp.empty:
        fig3 = px.histogram(df_comp, x='Completeness', nbins=10,
                           labels={'Completeness': 'Data Completeness Score'},
                           color_discrete_sequence=['#667eea'])
        fig3.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig3, use_container_width=True)

# ============================================================
# BROWSE CHARITIES PAGE
# ============================================================
elif page == "Browse Charities":
    st.header("Browse All Charities")

    if not all_charities:
        st.warning("No charities in database yet.")
        st.stop()

    # Quick filters
    col1, col2, col3 = st.columns(3)
    with col1:
        sector_filter = st.selectbox("Filter by Sector", ["All"] + [s[0] for s in sectors])
    with col2:
        size_filter = st.selectbox("Filter by Size", ["All", "Small", "Medium", "Large"])
    with col3:
        hac_filter = st.selectbox("HAC Affiliation", ["All", "HAC Members Only", "Non-HAC"])

    # Apply filters
    filtered = all_charities
    if sector_filter != "All":
        filtered = [c for c in filtered if c.get('sector') == sector_filter]
    if size_filter != "All":
        filtered = [c for c in filtered if c.get('charity_size') == size_filter]
    if hac_filter == "HAC Members Only":
        filtered = [c for c in filtered if c.get('hac_member')]
    elif hac_filter == "Non-HAC":
        filtered = [c for c in filtered if not c.get('hac_member')]

    st.write(f"Showing **{len(filtered)}** of {len(all_charities)} organisations")

    # Display as dataframe
    display_data = []
    for c in filtered:
        display_data.append({
            'Name': c['name'],
            'Sector': c.get('sector', ''),
            'Sub-Sector': c.get('sub_sector', ''),
            'CEO': c.get('ceo_name', ''),
            'Board Chair': c.get('board_chair', ''),
            'Website': c.get('website', ''),
            'Suburb': c.get('suburb', ''),
            'Size': c.get('charity_size', ''),
            'HAC': 'Yes' if c.get('hac_member') else 'No',
            'Data %': f"{c.get('data_completeness', 0):.0%}"
        })

    df_display = pd.DataFrame(display_data)
    st.dataframe(df_display, use_container_width=True, height=600,
                column_config={
                    "Website": st.column_config.LinkColumn("Website"),
                    "Data %": st.column_config.ProgressColumn("Data %", min_value=0, max_value=1,
                                                              format="%.0f%%"),
                })

    # Expandable detail view
    st.divider()
    st.subheader("Charity Detail View")
    charity_names = [c['name'] for c in filtered]
    selected_name = st.selectbox("Select a charity for details", charity_names)

    if selected_name:
        selected = next((c for c in filtered if c['name'] == selected_name), None)
        if selected:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"### {selected['name']}")
                if selected.get('abn'):
                    st.write(f"**ABN:** {selected['abn']}")
                st.write(f"**Sector:** {selected.get('sector', 'N/A')} / {selected.get('sub_sector', 'N/A')}")
                st.write(f"**Size:** {selected.get('charity_size', 'Unknown')}")
                if selected.get('purpose'):
                    st.write(f"**Purpose:** {selected['purpose']}")
                if selected.get('clients_served'):
                    st.write(f"**Clients Served:** {selected['clients_served']}")
                if selected.get('website'):
                    st.write(f"**Website:** {selected['website']}")
                if selected.get('email'):
                    st.write(f"**Email:** {selected['email']}")
                if selected.get('phone'):
                    st.write(f"**Phone:** {selected['phone']}")
                if selected.get('address'):
                    st.write(f"**Address:** {selected['address']}")

            with col2:
                st.markdown("#### Leadership")
                if selected.get('ceo_name'):
                    st.write(f"**{selected.get('ceo_title', 'CEO')}:** {selected['ceo_name']}")
                else:
                    st.write("*CEO: Not yet identified*")

                if selected.get('board_chair'):
                    st.write(f"**Board Chair:** {selected['board_chair']}")

                if isinstance(selected.get('board_members'), list) and selected['board_members']:
                    st.write("**Board Members:**")
                    for bm in selected['board_members']:
                        st.write(f"- {bm}")

                st.markdown("#### Core Functions")
                if isinstance(selected.get('core_functions'), list):
                    for fn in selected['core_functions']:
                        st.write(f"- {fn}")

                st.markdown("#### Funding Sources")
                if isinstance(selected.get('funding_sources'), list):
                    for fs in selected['funding_sources']:
                        st.write(f"- {fs}")


# ============================================================
# SEARCH & FILTER PAGE
# ============================================================
elif page == "Search & Filter":
    st.header("Advanced Search & Filter")

    col1, col2 = st.columns([2, 1])
    with col1:
        search_query = st.text_input("Search by name, purpose, or clients served",
                                     placeholder="e.g., mental health, disability, youth...")
    with col2:
        sector_filter = st.selectbox("Sector", ["All"] + [s[0] for s in sectors])

    col3, col4, col5, col6 = st.columns(4)
    with col3:
        has_ceo = st.checkbox("Has CEO identified")
    with col4:
        has_board = st.checkbox("Has Board info")
    with col5:
        hac_only = st.checkbox("HAC members only")
    with col6:
        min_completeness = st.slider("Min data completeness", 0.0, 1.0, 0.0, 0.1)

    results = cdb.search_charities(
        query=search_query if search_query else None,
        sector=sector_filter if sector_filter != "All" else None,
        has_ceo=has_ceo if has_ceo else None,
        has_board=has_board if has_board else None,
        hac_member=True if hac_only else None,
        min_completeness=min_completeness if min_completeness > 0 else None,
    )

    st.write(f"**{len(results)} results found**")

    if results:
        display_rows = []
        for c in results:
            display_rows.append({
                'Name': c['name'],
                'Sector': c.get('sector', ''),
                'Purpose': (c.get('purpose', '') or '')[:100] + ('...' if len(c.get('purpose', '') or '') > 100 else ''),
                'CEO': c.get('ceo_name', ''),
                'Board Chair': c.get('board_chair', ''),
                'Clients Served': c.get('clients_served', ''),
                'Website': c.get('website', ''),
                'HAC': 'Yes' if c.get('hac_member') else 'No',
            })
        st.dataframe(pd.DataFrame(display_rows), use_container_width=True, height=500)


# ============================================================
# SECTOR ANALYSIS PAGE
# ============================================================
elif page == "Sector Analysis":
    st.header("Sector Analysis")

    if not sectors:
        st.warning("No data available.")
        st.stop()

    # Sector breakdown
    df_sectors = pd.DataFrame(sectors, columns=['Sector', 'Count'])

    col1, col2 = st.columns(2)
    with col1:
        fig = px.treemap(df_sectors, path=['Sector'], values='Count',
                        color='Count', color_continuous_scale='RdYlGn')
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(df_sectors.sort_values('Count', ascending=False).head(15),
                      x='Sector', y='Count', color='Count',
                      color_continuous_scale='Blues')
        fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0), xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)

    # Per-sector detail
    st.divider()
    selected_sector = st.selectbox("Deep dive into sector", [s[0] for s in sectors])
    if selected_sector:
        sector_charities = [c for c in all_charities if c.get('sector') == selected_sector]
        st.write(f"**{len(sector_charities)} organisations in {selected_sector}**")

        sector_display = []
        for c in sector_charities:
            sector_display.append({
                'Name': c['name'],
                'Sub-Sector': c.get('sub_sector', ''),
                'Purpose': (c.get('purpose', '') or '')[:80],
                'CEO': c.get('ceo_name', ''),
                'Size': c.get('charity_size', ''),
                'Website': c.get('website', ''),
            })
        st.dataframe(pd.DataFrame(sector_display), use_container_width=True)


# ============================================================
# FUNCTIONS MAP PAGE
# ============================================================
elif page == "Functions Map":
    st.header("Organisational Functions Map")
    st.write("Cross-sector analysis of organisational functions - identifying shared innovation opportunities.")

    # Collect all functions
    function_counts = {}
    sector_function_matrix = {}

    for c in all_charities:
        funcs = c.get('core_functions', [])
        if isinstance(funcs, list):
            sector = c.get('sector', 'Unknown')
            if sector not in sector_function_matrix:
                sector_function_matrix[sector] = {}
            for f in funcs:
                function_counts[f] = function_counts.get(f, 0) + 1
                sector_function_matrix[sector][f] = sector_function_matrix[sector].get(f, 0) + 1

    if function_counts:
        # Bar chart of most common functions
        df_funcs = pd.DataFrame(list(function_counts.items()), columns=['Function', 'Count'])
        df_funcs = df_funcs.sort_values('Count', ascending=True)

        fig = px.bar(df_funcs, x='Count', y='Function', orientation='h',
                    color='Count', color_continuous_scale='Plasma')
        fig.update_layout(height=max(400, len(df_funcs) * 30), margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

        # Heatmap: sectors vs functions
        st.subheader("Sector x Function Heatmap")
        st.write("This shows which functions are most common in each sector - key for identifying shared capability building opportunities.")

        all_functions = sorted(function_counts.keys())
        all_sector_names = sorted(sector_function_matrix.keys())

        matrix_data = []
        for sector in all_sector_names:
            row = []
            for func in all_functions:
                row.append(sector_function_matrix.get(sector, {}).get(func, 0))
            matrix_data.append(row)

        fig_heat = go.Figure(data=go.Heatmap(
            z=matrix_data,
            x=all_functions,
            y=all_sector_names,
            colorscale='YlOrRd',
            hoverongaps=False
        ))
        fig_heat.update_layout(
            height=max(400, len(all_sector_names) * 30),
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        # Shared innovation opportunities
        st.divider()
        st.subheader("Shared Innovation Opportunities")
        st.write("Functions that appear across the most sectors represent the highest-value shared capability building targets.")

        func_sector_spread = {}
        for func in all_functions:
            sectors_with = [s for s in all_sector_names if sector_function_matrix.get(s, {}).get(func, 0) > 0]
            func_sector_spread[func] = len(sectors_with)

        df_spread = pd.DataFrame([
            {'Function': f, 'Sectors Using': c, 'Total Charities': function_counts[f]}
            for f, c in sorted(func_sector_spread.items(), key=lambda x: x[1], reverse=True)
        ])
        st.dataframe(df_spread, use_container_width=True)
    else:
        st.info("No function data available yet.")


# ============================================================
# BOARD & LEADERSHIP PAGE
# ============================================================
elif page == "Board & Leadership":
    st.header("Board & Leadership Directory")

    tab_ceo, tab_board, tab_gaps = st.tabs(["CEOs", "Board Chairs", "Data Gaps"])

    with tab_ceo:
        st.subheader("CEO / Executive Director Directory")
        ceo_data = []
        for c in all_charities:
            ceo_data.append({
                'Organisation': c['name'],
                'CEO/ED': c.get('ceo_name', '') or 'NOT IDENTIFIED',
                'Title': c.get('ceo_title', ''),
                'Sector': c.get('sector', ''),
                'Website': c.get('website', ''),
            })
        df_ceo = pd.DataFrame(ceo_data)

        # Filter
        show_only_identified = st.checkbox("Show only identified CEOs", value=False, key="ceo_filter")
        if show_only_identified:
            df_ceo = df_ceo[df_ceo['CEO/ED'] != 'NOT IDENTIFIED']

        st.write(f"{len(df_ceo)} organisations")
        st.dataframe(df_ceo, use_container_width=True, height=500)

    with tab_board:
        st.subheader("Board Chair Directory")
        board_data = []
        for c in all_charities:
            board_data.append({
                'Organisation': c['name'],
                'Board Chair': c.get('board_chair', '') or 'NOT IDENTIFIED',
                'Board Size': c.get('board_size', ''),
                'Sector': c.get('sector', ''),
            })
        df_board = pd.DataFrame(board_data)

        show_only_identified_board = st.checkbox("Show only identified Board Chairs", value=False, key="board_filter")
        if show_only_identified_board:
            df_board = df_board[df_board['Board Chair'] != 'NOT IDENTIFIED']

        st.write(f"{len(df_board)} organisations")
        st.dataframe(df_board, use_container_width=True, height=500)

    with tab_gaps:
        st.subheader("Leadership Data Gaps")
        st.write("Organisations where CEO or Board Chair has not yet been identified.")

        gaps = []
        for c in all_charities:
            missing = []
            if not c.get('ceo_name'):
                missing.append("CEO")
            if not c.get('board_chair'):
                missing.append("Board Chair")
            if missing:
                gaps.append({
                    'Organisation': c['name'],
                    'Sector': c.get('sector', ''),
                    'Missing': ', '.join(missing),
                    'Website': c.get('website', ''),
                })

        if gaps:
            st.write(f"**{len(gaps)} organisations** with leadership data gaps")
            st.dataframe(pd.DataFrame(gaps), use_container_width=True, height=500)
        else:
            st.success("All organisations have leadership data!")


# ============================================================
# TECHNOLOGY LANDSCAPE PAGE
# ============================================================
elif page == "Technology Landscape":
    st.header("Technology Landscape")
    st.write("Overview of technology systems used across the sector - identifying shared digital capability needs.")

    # Collect tech data
    crm_counts = {}
    accounting_counts = {}
    website_counts = {}
    case_mgmt_counts = {}

    for c in all_charities:
        if c.get('crm_system'):
            crm_counts[c['crm_system']] = crm_counts.get(c['crm_system'], 0) + 1
        if c.get('accounting_system'):
            accounting_counts[c['accounting_system']] = accounting_counts.get(c['accounting_system'], 0) + 1
        if c.get('website_platform'):
            website_counts[c['website_platform']] = website_counts.get(c['website_platform'], 0) + 1
        if c.get('case_management_system'):
            case_mgmt_counts[c['case_management_system']] = case_mgmt_counts.get(c['case_management_system'], 0) + 1

    col1, col2 = st.columns(2)

    with col1:
        if crm_counts:
            st.subheader("CRM Systems")
            df_crm = pd.DataFrame(list(crm_counts.items()), columns=['System', 'Count']).sort_values('Count', ascending=False)
            fig = px.bar(df_crm, x='System', y='Count', color='Count', color_continuous_scale='Teal')
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        if accounting_counts:
            st.subheader("Accounting Systems")
            df_acc = pd.DataFrame(list(accounting_counts.items()), columns=['System', 'Count']).sort_values('Count', ascending=False)
            fig2 = px.bar(df_acc, x='System', y='Count', color='Count', color_continuous_scale='Sunset')
            fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0), xaxis_tickangle=-45)
            st.plotly_chart(fig2, use_container_width=True)

    with col2:
        if website_counts:
            st.subheader("Website Platforms")
            df_web = pd.DataFrame(list(website_counts.items()), columns=['Platform', 'Count']).sort_values('Count', ascending=False)
            fig3 = px.pie(df_web, names='Platform', values='Count', hole=0.3)
            fig3.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig3, use_container_width=True)

        if case_mgmt_counts:
            st.subheader("Case Management Systems")
            df_cm = pd.DataFrame(list(case_mgmt_counts.items()), columns=['System', 'Count']).sort_values('Count', ascending=False)
            fig4 = px.bar(df_cm, x='System', y='Count', color='Count', color_continuous_scale='Magenta')
            fig4.update_layout(margin=dict(l=0, r=0, t=10, b=0), xaxis_tickangle=-45)
            st.plotly_chart(fig4, use_container_width=True)

    # Tech needs analysis
    st.divider()
    st.subheader("Technology Needs Analysis")
    tech_gaps = {'No CRM': 0, 'No Accounting System': 0, 'No Website Platform': 0, 'No Case Management': 0}
    for c in all_charities:
        if not c.get('crm_system'):
            tech_gaps['No CRM'] += 1
        if not c.get('accounting_system'):
            tech_gaps['No Accounting System'] += 1
        if not c.get('website_platform'):
            tech_gaps['No Website Platform'] += 1
        if not c.get('case_management_system'):
            tech_gaps['No Case Management'] += 1

    df_gaps = pd.DataFrame(list(tech_gaps.items()), columns=['Gap', 'Count'])
    fig5 = px.bar(df_gaps, x='Gap', y='Count', color='Count',
                 color_continuous_scale='Reds')
    fig5.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig5, use_container_width=True)


# ============================================================
# WORKSHOP TARGETING PAGE
# ============================================================
elif page == "Workshop Targeting":
    st.header("Workshop Targeting")
    st.write("Identify and prioritise organisations for AI capability building workshops.")

    st.subheader("Target Audience Builder")

    col1, col2, col3 = st.columns(3)
    with col1:
        target_sectors = st.multiselect("Target Sectors", [s[0] for s in sectors])
    with col2:
        target_size = st.multiselect("Organisation Size", ["Small", "Medium", "Large"])
    with col3:
        target_hac = st.checkbox("HAC Members Only", value=False)

    # Apply targeting
    targets = all_charities
    if target_sectors:
        targets = [c for c in targets if c.get('sector') in target_sectors]
    if target_size:
        targets = [c for c in targets if c.get('charity_size') in target_size]
    if target_hac:
        targets = [c for c in targets if c.get('hac_member')]

    st.write(f"**{len(targets)} organisations** match your targeting criteria")

    # Workshop contact list
    st.subheader("Workshop Contact List")
    contact_data = []
    for c in targets:
        contact_data.append({
            'Organisation': c['name'],
            'CEO/ED': c.get('ceo_name', '') or 'TBD',
            'CEO Title': c.get('ceo_title', ''),
            'Board Chair': c.get('board_chair', '') or 'TBD',
            'Email': c.get('email', ''),
            'Phone': c.get('phone', ''),
            'Website': c.get('website', ''),
            'Sector': c.get('sector', ''),
            'Size': c.get('charity_size', ''),
        })

    df_contacts = pd.DataFrame(contact_data)
    st.dataframe(df_contacts, use_container_width=True, height=400)

    # Sector breakdown of targets
    if targets:
        st.subheader("Target Breakdown by Sector")
        target_sectors_count = {}
        for c in targets:
            s = c.get('sector', 'Unknown')
            target_sectors_count[s] = target_sectors_count.get(s, 0) + 1

        df_ts = pd.DataFrame(list(target_sectors_count.items()), columns=['Sector', 'Count'])
        fig = px.pie(df_ts, names='Sector', values='Count', hole=0.4)
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    # Export targeting list
    st.divider()
    if targets and st.button("Download Workshop Target List as Excel"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_contacts.to_excel(writer, sheet_name='Workshop Targets', index=False)
            worksheet = writer.sheets['Workshop Targets']
            for i, col in enumerate(df_contacts.columns):
                max_len = max(df_contacts[col].astype(str).str.len().max(), len(col)) + 2
                worksheet.set_column(i, i, min(max_len, 40))
        st.download_button(
            "Download Excel",
            data=output.getvalue(),
            file_name="workshop_targets.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# ============================================================
# EXPORT DATA PAGE
# ============================================================
elif page == "Export Data":
    st.header("Export Data")
    st.write("Download the full database as a spreadsheet.")

    df_export = cdb.export_to_dataframe()

    if df_export.empty:
        st.warning("No data to export.")
        st.stop()

    st.write(f"**{len(df_export)} organisations** ready for export")

    # Preview
    st.subheader("Data Preview")
    st.dataframe(df_export.head(20), use_container_width=True)

    # Column selection
    st.subheader("Select Columns to Export")
    all_cols = list(df_export.columns)
    default_cols = ['name', 'abn', 'sector', 'sub_sector', 'purpose', 'clients_served',
                    'website', 'email', 'phone', 'address', 'suburb', 'postcode',
                    'ceo_name', 'ceo_title', 'board_chair', 'board_members',
                    'charity_size', 'staff_count', 'volunteer_count',
                    'core_functions', 'service_types', 'funding_sources',
                    'crm_system', 'accounting_system', 'website_platform',
                    'hac_member', 'data_completeness']
    selected_cols = st.multiselect("Columns", all_cols,
                                   default=[c for c in default_cols if c in all_cols])

    if selected_cols:
        df_selected = df_export[selected_cols]

        # Excel export
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Main data sheet
            df_selected.to_excel(writer, sheet_name='Charities', index=False)

            # Summary sheet
            summary_data = {
                'Metric': ['Total Organisations', 'With CEO', 'With Board Chair',
                          'With Website', 'With Email', 'HAC Members',
                          'Avg Data Completeness'],
                'Value': [stats['total_charities'], stats['with_ceo'], stats['with_board'],
                         stats['with_website'], stats['with_email'], stats['hac_members'],
                         f"{stats['avg_completeness']:.0%}"]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

            # Sector breakdown sheet
            if sectors:
                pd.DataFrame(sectors, columns=['Sector', 'Count']).to_excel(
                    writer, sheet_name='Sectors', index=False)

            # Format columns
            worksheet = writer.sheets['Charities']
            for i, col in enumerate(df_selected.columns):
                max_len = max(df_selected[col].astype(str).str.len().max(), len(col)) + 2
                worksheet.set_column(i, i, min(max_len, 50))

        st.download_button(
            "Download Full Database as Excel",
            data=output.getvalue(),
            file_name="canberra_charities_database.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

        # CSV option
        csv_data = df_selected.to_csv(index=False)
        st.download_button(
            "Download as CSV",
            data=csv_data,
            file_name="canberra_charities_database.csv",
            mime="text/csv"
        )
