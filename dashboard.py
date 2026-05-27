import requests
import streamlit as st

FASTAPI_URL = "http://127.0.0.1:8000"

STATUS_OPTIONS = ["new", "contacted", "replied", "qualified", "closed", "lost"]


st.set_page_config(page_title="AI Sales Lead Agent", layout="wide")

st.title("AI Sales Lead Agent")

st.markdown("Generate, qualify, score, and strategize sales leads using AI agents.")

# Sidebar Inputs
st.sidebar.header("Business Context")

industry = st.sidebar.text_input("Industry", value="Luxury Automotive")

ideal_customer = st.sidebar.text_input(
    "Ideal Customer", value="High net worth car enthusiasts"
)

product = st.sidebar.text_input("Product", value="Porsche GT3 RS inventory")

generate_button = st.sidebar.button("Generate Leads")


if generate_button:

    # Step 1 — Send Business Context
    context_payload = {
        "industry": industry,
        "ideal_customer": ideal_customer,
        "product": product,
    }

    requests.post(f"{FASTAPI_URL}/business-context", json=context_payload)

    # Step 2 — Trigger Full Pipeline
    with st.spinner("Running AI pipeline..."):
        response = requests.post(f"{FASTAPI_URL}/generate-strategies")

    data = response.json()

    # Store leads in session state so they survive re-renders from status updates
    st.session_state["final_leads"] = data.get("final_leads", [])

    st.success("Lead generation completed.")


# Render leads from session state (persists across re-renders)
final_leads = st.session_state.get("final_leads", [])

if final_leads:

    st.subheader("Generated Leads")

    for i, lead in enumerate(final_leads):

        with st.expander(
            f"{lead['company']} — Score: {lead['lead_score']} ({lead.get('priority', 'N/A')})"
        ):

            # ==================================================
            # Lead Status
            # ==================================================

            lead_id = lead.get("id")
            if lead_id:
                current_status = lead.get("status", "new")
                new_status = st.selectbox(
                    "Status",
                    STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(current_status) if current_status in STATUS_OPTIONS else 0,
                    key=f"status_{lead_id}",
                )
                if new_status != current_status:
                    update_col, revert_col = st.columns(2)
                    with update_col:
                        if st.button("Update", key=f"update_{lead_id}"):
                            r = requests.patch(
                                f"{FASTAPI_URL}/leads/{lead_id}/status",
                                json={"status": new_status},
                            )
                            if r.ok:
                                st.session_state["final_leads"][i]["status"] = new_status
                                st.success(f"Status updated to '{new_status}'")
                            else:
                                st.error("Update failed")
                    with revert_col:
                        if st.button("Revert", key=f"revert_{lead_id}"):
                            st.session_state[f"status_{lead_id}"] = current_status
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

            sources = lead.get("sources", [])

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

            st.write(f"**Purchase Likelihood:** " f"{lead.get('purchase_likelihood')}")

            st.write("**Qualification Signals:**")

            for signal in lead.get("qualification_signals", []):
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

            for objection in lead.get("likely_objections", []):
                st.write(f"- {objection}")

            st.write("**Recommended Next Action:**")

            st.error(lead.get("recommended_next_action"))
