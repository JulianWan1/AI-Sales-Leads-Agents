import requests
import streamlit as st

FASTAPI_URL = "http://127.0.0.1:8000"


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
    response = requests.post(f"{FASTAPI_URL}/generate-strategies")

    data = response.json()

    st.success("Lead generation completed.")

    final_leads = data.get("final_leads", [])

    st.subheader("Generated Leads")

    for lead in final_leads:

        with st.expander(f"{lead['company']} — Score: {lead['lead_score']}"):

            st.write(f"**Contact:** {lead['contact']}")
            st.write(f"**Role:** {lead['role']}")
            st.write(f"**Interest:** {lead['interest']}")

            st.write(f"**Estimated Budget:** ${lead['estimated_budget']}")

            st.write(f"**Purchase Likelihood:** {lead['purchase_likelihood']}")

            st.write(f"**Lead Score:** {lead['lead_score']}")

            st.write(f"**Score Reasoning:** {lead['score_reasoning']}")

            st.write(f"**Recommended Sales Angle:**")

            st.info(lead["recommended_sales_angle"])

            st.write("**Qualification Signals:**")

            for signal in lead["qualification_signals"]:
                st.write(f"- {signal}")

            st.write("**Outreach Strategy:**")

            st.success(lead["outreach_strategy"])

            st.write(f"**Conversation Starter:**")

            st.code(lead["conversation_starter"])

            st.write("**Likely Objections:**")

            for objection in lead["likely_objections"]:
                st.write(f"- {objection}")

            st.write(f"**Recommended Next Action:**")

            st.warning(lead["recommended_next_action"])
