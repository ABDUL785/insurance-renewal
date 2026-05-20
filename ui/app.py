"""
Streamlit UI for Insurance Renewal Agent Demo
Provides a chat-like interface to interact with the agent
"""

import streamlit as st
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agent"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mcp_servers"))

from renewal_agent import RenewalAgent
from document_mcp import DocumentMCPServer
from communication_mcp import CommunicationMCPServer


st.set_page_config(
    page_title="Insurance Renewal Agent",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a365d;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f7fafc;
        border-left: 4px solid #2c5282;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .success-card {
        background: #f0fff4;
        border-left: 4px solid #276749;
        padding: 1rem;
        border-radius: 5px;
    }
    .step-card {
        background: #edf2f7;
        padding: 0.75rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .agent-message {
        background: #e2e8f0;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background: #2c5282;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    if 'agent' not in st.session_state:
        st.session_state.agent = RenewalAgent()
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'processing_log' not in st.session_state:
        st.session_state.processing_log = []
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None


def format_currency(amount):
    try:
        return f"${float(amount):,.2f}"
    except:
        return str(amount)


def display_step_result(step_num, skill, action, result):
    status = result.get("status", "unknown")
    status_color = "green" if status == "success" else "red"

    with st.expander(f"Step {step_num}: {skill.upper()} - {action}", expanded=True):
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"**Status:** :{status_color}[{status.upper()}]")
        with col2:
            if result.get("data"):
                if isinstance(result["data"], dict):
                    for key, value in list(result["data"].items())[:5]:
                        st.text(f"{key}: {value}")
                elif isinstance(result["data"], list):
                    st.text(f"Returned {len(result['data'])} records")


def display_final_result(result):
    if not result or not result.get("final_response"):
        st.error("No result to display")
        return

    fr = result["final_response"]

    st.markdown("---")
    st.markdown("### Renewal Processing Complete")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Current Premium",
            value=fr.get("current_premium", "N/A")
        )
    with col2:
        st.metric(
            label="Renewal Premium",
            value=fr.get("renewal_premium", "N/A"),
            delta=fr.get("premium_change", "N/A")
        )
    with col3:
        st.metric(
            label="Risk Tier",
            value=fr.get("risk_tier", "N/A")
        )
    with col4:
        st.metric(
            label="Status",
            value=fr.get("status", "N/A")
        )

    st.markdown("---")

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:
        st.markdown("**Policy Information**")
        st.text(f"Policy Holder: {fr.get('policy_holder', 'N/A')}")
        st.text(f"Expiration Date: {fr.get('expiration_date', 'N/A')}")
        st.text(f"Agent ID: {fr.get('agent', 'N/A')}")

    with detail_col2:
        st.markdown("**Discounts & Adjustments**")
        st.text(f"Loyalty Discount: {fr.get('loyalty_discount', 'N/A')}")
        st.text(f"Claims History: {fr.get('claims_history', 'N/A')}")
        st.text(f"Quote Document: {fr.get('quote_document', 'N/A')}")

    if result.get("steps_completed"):
        st.markdown("---")
        st.markdown("### Processing Steps")

        for idx, step in enumerate(result["steps_completed"]):
            step_num = idx + 1
            skill = step.get("skill", "unknown")
            result_data = step.get("result", {})
            action = "process"

            with st.expander(f"Step {step_num}: {skill.upper()}", expanded=False):
                st.json(result_data)


def main():
    init_session_state()

    st.markdown('<div class="main-header">Insurance Renewal Intelligence Agent</div>', unsafe_allow_html=True)

    st.sidebar.markdown("### Agent Configuration")
    st.sidebar.markdown("---")

    demo_mode = st.sidebar.radio(
        "Select Demo Mode:",
        ["Single Policy Renewal", "Batch Renewal Processing", "View System Logs"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### MCP Servers Connected")
    st.sidebar.success("✓ Snowflake MCP")
    st.sidebar.success("✓ Document MCP")
    st.sidebar.success("✓ Communication MCP")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Skills Available")
    st.sidebar.info("📋 Policy Verification")
    st.sidebar.info("📊 Experience Rating")
    st.sidebar.info("💰 Pricing Engine")
    st.sidebar.info("📄 Document Generation")
    st.sidebar.info("📧 Communication")

    st.markdown("---")

    if demo_mode == "Single Policy Renewal":
        st.markdown("### Process Single Policy Renewal")

        col1, col2 = st.columns([3, 1])

        with col1:
            policy_input = st.text_input(
                "Enter Policy Number",
                placeholder="e.g., HW-88712",
                value="HW-88712"
            )

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            process_button = st.button("Process Renewal", type="primary", use_container_width=True)

        if process_button and policy_input:
            with st.spinner("Processing renewal... This may take a few seconds."):
                result = st.session_state.agent.process_renewal(policy_input)
                st.session_state.last_result = result
                st.session_state.processing_log = st.session_state.agent.get_processing_log()

                st.rerun()

        if st.session_state.last_result:
            display_final_result(st.session_state.last_result)

    elif demo_mode == "Batch Renewal Processing":
        st.markdown("### Batch Renewal Processing")

        st.info("Process multiple policy renewals at once. Enter policy numbers separated by commas.")

        batch_input = st.text_area(
            "Policy Numbers (one per line or comma-separated)",
            placeholder="HW-88712\nHW-44521\nAU-99234",
            height=150
        )

        if st.button("Process Batch", type="primary"):
            policies = [p.strip() for p in batch_input.replace(",", "\n").split("\n") if p.strip()]

            if not policies:
                st.warning("Please enter at least one policy number")
            else:
                st.markdown(f"**Processing {len(policies)} policies...**")

                results_container = st.container()

                with results_container:
                    for policy_num in policies:
                        with st.spinner(f"Processing {policy_num}..."):
                            try:
                                result = st.session_state.agent.process_renewal(policy_num)
                                if result.get("error"):
                                    st.error(f"{policy_num}: {result['error']}")
                                else:
                                    fr = result.get("final_response", {})
                                    st.success(f"{policy_num}: {fr.get('renewal_premium', 'N/A')} (Status: {fr.get('status', 'N/A')})")
                            except Exception as e:
                                st.error(f"{policy_num}: {str(e)}")

    elif demo_mode == "View System Logs":
        st.markdown("### Agent Processing Logs")

        if st.session_state.processing_log:
            for entry in st.session_state.processing_log:
                with st.expander(f"[{entry.get('step', 0)}] {entry.get('skill', 'N/A').upper()} - {entry.get('action', 'N/A')}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text(f"Timestamp: {entry.get('timestamp', 'N/A')}")
                        st.text(f"Status: {entry.get('status', 'N/A')}")
                    with col2:
                        st.text(f"Summary: {entry.get('summary', 'N/A')}")
        else:
            st.info("No processing logs yet. Process a renewal to see logs here.")

    st.markdown("---")
    st.markdown("### How It Works")

    how_col1, how_col2, how_col3, how_col4, how_col5 = st.columns(5)

    with how_col1:
        st.markdown("""
        <div class="step-card">
        <strong>1. Verify Policy</strong><br>
        <small>Check eligibility & fetch details from Snowflake</small>
        </div>
        """, unsafe_allow_html=True)

    with how_col2:
        st.markdown("""
        <div class="step-card">
        <strong>2. Experience Rating</strong><br>
        <small>Analyze claims history & risk tier</small>
        </div>
        """, unsafe_allow_html=True)

    with how_col3:
        st.markdown("""
        <div class="step-card">
        <strong>3. Calculate Premium</strong><br>
        <small>Market rates + adjustments = renewal quote</small>
        </div>
        """, unsafe_allow_html=True)

    with how_col4:
        st.markdown("""
        <div class="step-card">
        <strong>4. Generate Documents</strong><br>
        <small>Create quote PDF via Document MCP</small>
        </div>
        """, unsafe_allow_html=True)

    with how_col5:
        st.markdown("""
        <div class="step-card">
        <strong>5. Notify</strong><br>
        <small>Send email/SMS/portal via Communication MCP</small>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()