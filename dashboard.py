import requests
import streamlit as st

FASTAPI_URL = "http://127.0.0.1:8000"

STATUS_OPTIONS = ["new", "contacted", "replied", "qualified", "closed", "lost"]
PRIORITY_OPTIONS = ["All", "High", "Medium", "Low"]


st.set_page_config(page_title="AI Sales Lead Agent", layout="wide")

st.title("AI Sales Lead Agent")

st.markdown("Generate, qualify, score, and strategize sales leads using AI agents.")


def render_lead_card(lead, i, session_list_key, key_prefix):
    """Render a single lead expander card. key_prefix prevents widget key collisions across tabs."""

    with st.expander(
        f"{lead['company']} — Score: {lead.get('lead_score', 'N/A')} ({lead.get('priority', 'N/A')})"
    ):

        # ==================================================
        # Lead Status
        # ==================================================

        lead_id = lead.get("id")
        if lead_id:
            current_status = lead.get("status", "new")
            widget_key = f"status_{key_prefix}_{lead_id}"
            reset_key = f"reset_{key_prefix}_{lead_id}"

            # Restore widget to current_status if a revert was requested
            if reset_key in st.session_state:
                del st.session_state[reset_key]
                st.session_state[widget_key] = current_status

            new_status = st.selectbox(
                "Status",
                STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(current_status) if current_status in STATUS_OPTIONS else 0,
                key=widget_key,
            )
            if new_status != current_status:
                update_col, revert_col = st.columns(2)
                with update_col:
                    if st.button("Update", key=f"update_{key_prefix}_{lead_id}"):
                        r = requests.patch(
                            f"{FASTAPI_URL}/leads/{lead_id}/status",
                            json={"status": new_status},
                        )
                        if r.ok:
                            st.session_state[session_list_key][i]["status"] = new_status
                            st.toast(f"Status updated to '{new_status}'", icon="✅")
                            st.rerun()
                        else:
                            st.error("Update failed")
                with revert_col:
                    if st.button("Revert", key=f"revert_{key_prefix}_{lead_id}"):
                        st.session_state[reset_key] = True
                        st.rerun()

        st.divider()

        # ==================================================
        # Lead Identity
        # ==================================================

        st.subheader("Lead Identity")

        st.write(f"**Contact:** {lead.get('contact')}")
        st.write(f"**Role:** {lead.get('role')}")

        st.write("**Company Summary:**")
        st.info(lead.get("company_summary"))

        st.divider()

        # ==================================================
        # Research Intelligence
        # ==================================================

        st.subheader("Research Intelligence")

        st.write(f"**Detected Industry:** {lead.get('detected_industry')}")
        st.write(f"**Specialization:** {lead.get('specialization')}")
        st.write(f"**Research Confidence:** {lead.get('research_confidence')}")
        st.write(f"**Interest:** {lead.get('interest')}")
        st.write(f"**Budget Signal:** {lead.get('budget_signal')}")
        st.write(f"**Estimated Budget:** ${lead.get('estimated_budget')}")

        sources = lead.get("sources") or []
        if sources:
            st.write("**Sources:**")
            for url in sources:
                st.markdown(f"- [{url}]({url})")

        st.divider()

        # ==================================================
        # Scoring & Qualification
        # ==================================================

        st.subheader("Scoring & Qualification")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Lead Score", lead.get("lead_score"))
        with col2:
            st.metric("Priority", lead.get("priority"))

        st.write(f"**Purchase Likelihood:** {lead.get('purchase_likelihood')}")

        st.write("**Qualification Signals:**")
        for signal in lead.get("qualification_signals") or []:
            st.write(f"- {signal}")

        st.write("**Score Reasoning:**")
        st.warning(lead.get("score_reasoning"))

        st.divider()

        # ==================================================
        # Outreach Strategy
        # ==================================================

        st.subheader("Outreach Strategy")

        st.write("**Recommended Sales Angle:**")
        st.success(lead.get("recommended_sales_angle"))

        st.write("**Outreach Strategy:**")
        st.success(lead.get("outreach_strategy"))

        st.write("**Conversation Starter:**")
        st.code(lead.get("conversation_starter"), language="text")

        st.write("**Likely Objections:**")
        for objection in lead.get("likely_objections") or []:
            st.write(f"- {objection}")

        st.write("**Recommended Next Action:**")
        st.error(lead.get("recommended_next_action"))


# ==============================================================
# Tabs
# ==============================================================

tab1, tab2 = st.tabs(["Generate Leads", "History"])


# ==============================================================
# Tab 1 — Generate Leads
# ==============================================================

with tab1:

    st.sidebar.header("Business Context")

    industry = st.sidebar.text_input("Industry", value="Luxury Automotive")
    ideal_customer = st.sidebar.text_input("Ideal Customer", value="High net worth car enthusiasts")
    product = st.sidebar.text_input("Product", value="Porsche GT3 RS inventory")
    generate_button = st.sidebar.button("Generate Leads")

    if generate_button:
        context_payload = {
            "industry": industry,
            "ideal_customer": ideal_customer,
            "product": product,
        }
        requests.post(f"{FASTAPI_URL}/business-context", json=context_payload)

        with st.spinner("Running AI pipeline..."):
            response = requests.post(f"{FASTAPI_URL}/generate-strategies")

        data = response.json()
        st.session_state["final_leads"] = data.get("final_leads", [])
        st.success("Lead generation completed.")

    final_leads = st.session_state.get("final_leads", [])

    if final_leads:
        st.subheader(f"Generated Leads ({len(final_leads)})")
        for i, lead in enumerate(final_leads):
            render_lead_card(lead, i, "final_leads", "gen")


# ==============================================================
# Tab 2 — History
# ==============================================================

with tab2:

    st.subheader("Lead History")

    # Filters
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
        f_industry = st.text_input("Industry", key="hist_industry")
    with f_col2:
        f_priority = st.selectbox("Priority", PRIORITY_OPTIONS, key="hist_priority")
    with f_col3:
        f_status = st.selectbox("Status", ["All"] + STATUS_OPTIONS, key="hist_status")
    with f_col4:
        f_score = st.slider("Score range", 0, 100, (0, 100), key="hist_score")

    if st.button("Load Leads", key="hist_load"):
        params = {
            "score_min": f_score[0],
            "score_max": f_score[1],
        }
        if f_industry:
            params["industry"] = f_industry
        if f_priority != "All":
            params["priority"] = f_priority
        if f_status != "All":
            params["status"] = f_status

        r = requests.get(f"{FASTAPI_URL}/leads/", params=params)
        st.session_state["history_leads"] = r.json() if r.ok else []

    history_leads = st.session_state.get("history_leads", [])

    if history_leads:
        st.caption(f"{len(history_leads)} lead(s) found")
        for i, lead in enumerate(history_leads):
            render_lead_card(lead, i, "history_leads", "hist")
    elif "history_leads" in st.session_state:
        st.info("No leads match the selected filters.")
