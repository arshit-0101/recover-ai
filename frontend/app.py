import streamlit as st
import pandas as pd
import requests


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="RecoverAI",
    page_icon="💰",
    layout="wide"
)


# ============================================================
# LOAD RESULTS
# ============================================================

RESULTS_FILE = "data/processed/v2_results.csv"
API_URL = "http://127.0.0.1:8000/recover"


@st.cache_data
def load_results():
    return pd.read_csv(RESULTS_FILE)


df = load_results()


# ============================================================
# TITLE
# ============================================================

st.title("💰 RecoverAI")

st.subheader("AI-Powered Revenue Recovery Dashboard")

st.caption(
    "ML-powered recovery decisions with business guardrails"
)

st.divider()


# ============================================================
# BUSINESS METRICS
# ============================================================

total_transactions = len(df)

revenue_at_risk = df["amount"].sum()

revenue_recovered = df["recovered_amount"].sum()

successful_recoveries = df["success"].sum()

recovery_rate = (
    successful_recoveries / total_transactions * 100
)


# ============================================================
# BUSINESS OVERVIEW
# ============================================================

st.header("📊 Business Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Transactions",
        f"{total_transactions:,}"
    )

with col2:
    st.metric(
        "Revenue at Risk",
        f"₹{revenue_at_risk:,.0f}"
    )

with col3:
    st.metric(
        "Revenue Recovered",
        f"₹{revenue_recovered:,.0f}"
    )

with col4:
    st.metric(
        "Recovery Rate",
        f"{recovery_rate:.2f}%"
    )


st.divider()


# ============================================================
# RECOVERY PERFORMANCE
# ============================================================

st.header("📈 Recovery Performance")

col1, col2 = st.columns(2)

with col1:

    st.subheader("Recovery by Action")

    action_recovery = (
        df.groupby("action")["recovered_amount"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(action_recovery)


with col2:

    st.subheader("Transactions by Action")

    action_count = (
        df["action"]
        .value_counts()
    )

    st.bar_chart(action_count)


st.divider()


# ============================================================
# BASELINE COMPARISON
# ============================================================

st.header("⚖️ Baseline vs RecoverAI")

# Always-Retry baseline
baseline_recovered = 13_250_550.42
baseline_successful = 4_621

# RecoverAI results
recoverai_recovered = revenue_recovered
recoverai_successful = successful_recoveries

# Business impact
additional_revenue = (
    recoverai_recovered - baseline_recovered
)

revenue_lift = (
    additional_revenue / baseline_recovered * 100
)

additional_transactions = (
    recoverai_successful - baseline_successful
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Always-Retry Baseline",
        f"₹{baseline_recovered:,.0f}"
    )

with col2:
    st.metric(
        "RecoverAI",
        f"₹{recoverai_recovered:,.0f}",
        f"+₹{additional_revenue:,.0f}"
    )

with col3:
    st.metric(
        "Revenue Lift",
        f"{revenue_lift:.2f}%"
    )

st.subheader("Revenue Recovery Comparison")

comparison = pd.DataFrame({
    "System": [
        "Always Retry",
        "RecoverAI"
    ],
    "Revenue Recovered": [
        baseline_recovered,
        recoverai_recovered
    ]
})

st.bar_chart(
    comparison.set_index("System")
)

st.info(
    f"💡 RecoverAI recovered ₹{additional_revenue:,.0f} "
    f"more revenue than the always-retry baseline, "
    f"a {revenue_lift:.2f}% improvement."
)
st.divider()

# ============================================================
# FAILURE REASON ANALYSIS
# ============================================================

st.header("🔍 Recovery by Failure Reason")

failure_analysis = (
    df.groupby("failure_reason")
    .agg(
        transactions=("transaction_id", "count"),
        revenue_at_risk=("amount", "sum"),
        revenue_recovered=("recovered_amount", "sum"),
        successful_recoveries=("success", "sum")
    )
    .reset_index()
)

failure_analysis["recovery_rate"] = (
    failure_analysis["successful_recoveries"]
    / failure_analysis["transactions"]
    * 100
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue at Risk by Failure")

    st.bar_chart(
        failure_analysis.set_index("failure_reason")[
            "revenue_at_risk"
        ]
    )

with col2:
    st.subheader("Recovery Rate by Failure")

    st.bar_chart(
        failure_analysis.set_index("failure_reason")[
            "recovery_rate"
        ]
    )

st.subheader("Failure Reason Performance")

st.dataframe(
    failure_analysis[
        [
            "failure_reason",
            "transactions",
            "revenue_at_risk",
            "revenue_recovered",
            "recovery_rate"
        ]
    ],
    use_container_width=True
)
# ============================================================
# TRANSACTION ANALYSIS
# ============================================================

st.header("🔎 Analyze Transaction")
st.caption(
    "Let RecoverAI evaluate a failed transaction and recommend "
    "the best recovery strategy."
)

col1, col2 = st.columns([3, 1])

with col1:
    transaction_id = st.text_input(
        "Transaction ID",
        value="TXN_000001",
        placeholder="e.g. TXN_000001"
    )

with col2:
    st.write("")
    st.write("")
    analyze = st.button(
        "🚀 Analyze & Recover",
        use_container_width=True
    )

if analyze:

    try:
        response = requests.post(
            API_URL,
            json={
                "transaction_id": transaction_id
            },
            timeout=10
        )

        if response.status_code == 200:

            result = response.json()

            st.success(
                "RecoverAI generated a recovery decision."
            )

            st.divider()

            # ------------------------------------------------
            # DECISION SUMMARY
            # ------------------------------------------------

            st.subheader("🤖 RecoverAI Decision")

            col1, col2, col3 = st.columns([1.5, 1, 1])

            with col1:
                st.caption("Selected Recovery Action")
                st.metric(
                    "Selected Action",
                    result["selected_action"]
                )

            with col2:
                st.caption("Recovery Probability")
                st.metric(
                    "Probability",
                    f"{result['recovery_probability']:.2%}"
                )

            with col3:
                st.caption("Expected Recovery")
                st.metric(
                    "Revenue",
                    f"₹{result['expected_recovery']:,.2f}"
                )

            st.divider()

            # ------------------------------------------------
            # TRANSACTION DETAILS
            # ------------------------------------------------

            st.subheader("📋 Transaction Details")

            detail_col1, detail_col2 = st.columns(2)

            with detail_col1:

                st.write(
                    f"**Transaction ID:** "
                    f"{result['transaction_id']}"
                )

                st.write(
                    f"**Failure Reason:** "
                    f"{result['failure_reason']}"
                )

            with detail_col2:

                st.write(
                    f"**Transaction Amount:** "
                    f"₹{result['amount']:,.2f}"
                )

                st.write(
                    f"**Potential Revenue at Risk:** "
                    f"₹{result['amount']:,.2f}"
                )

            st.divider()

            # ------------------------------------------------
            # BUSINESS GUARDRAIL
            # ------------------------------------------------

            st.subheader("🛡️ Business Guardrail")

            st.info(
                f"**Decision rationale:** "
                f"{result['reason']}"
            )

            st.caption(
                "RecoverAI combines ML-based recovery propensity "
                "with action-specific recovery signals and "
                "business rules to select the recovery action."
            )

        else:

            st.error(
                f"Transaction not found. "
                f"API returned {response.status_code}"
            )

    except requests.exceptions.ConnectionError:

        st.error(
            "Could not connect to RecoverAI API."
        )

        st.info(
            "Make sure FastAPI is running on "
            "http://127.0.0.1:8000"
        )

    except Exception as e:

        st.error(
            f"An unexpected error occurred: {e}"
        )


st.divider()
# ============================================================
# DATASET EXPLORER
# ============================================================

st.header("📋 Recovery Results")

st.dataframe(
    df,
    use_container_width=True,
    height=400
)
# ============================================================
# KEY BUSINESS INSIGHTS
# ============================================================

st.divider()

st.header("💡 Key Business Insights")

additional_revenue = revenue_recovered - baseline_recovered
revenue_lift = (additional_revenue / baseline_recovered) * 100

insight_col1, insight_col2, insight_col3 = st.columns(3)

with insight_col1:
    st.metric(
        "Additional Revenue",
        f"₹{additional_revenue:,.0f}",
        "vs Always-Retry"
    )

with insight_col2:
    st.metric(
        "Recovery Improvement",
        f"{recovery_rate:.2f}%",
        f"+{recovery_rate - (baseline_successful / total_transactions * 100):.2f} pp"
    )

with insight_col3:
    st.metric(
        "Revenue Lift",
        f"{revenue_lift:.2f}%",
        "vs baseline"
    )

st.info(
    f"RecoverAI recovered ₹{additional_revenue:,.0f} more revenue "
    f"than the Always-Retry baseline while using ML-powered "
    f"recovery decisions and business guardrails."
)
# ============================================================
# RECOVERY STRATEGY ANALYSIS
# ============================================================

st.divider()

st.header("🎯 Recovery Strategy Analysis")
st.caption(
    "Performance of each recovery action selected by RecoverAI"
)

# Group performance by recovery action
action_performance = (
    df.groupby("action")
    .agg(
        transactions=("transaction_id", "count"),
        revenue_recovered=("recovered_amount", "sum"),
        success_rate=("success", "mean")
    )
    .sort_values("revenue_recovered", ascending=False)
)

action_performance["success_rate"] = (
    action_performance["success_rate"] * 100
)

# Display metrics
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Revenue Recovered by Strategy")

    st.bar_chart(
        action_performance["revenue_recovered"]
    )

with col2:
    st.subheader("📈 Success Rate by Strategy")

    st.bar_chart(
        action_performance["success_rate"]
    )

# Detailed table
st.subheader("📋 Strategy Performance")

display_df = action_performance.copy()

display_df["revenue_recovered"] = (
    display_df["revenue_recovered"]
    .map(lambda x: f"₹{x:,.2f}")
)

display_df["success_rate"] = (
    display_df["success_rate"]
    .map(lambda x: f"{x:.2f}%")
)

display_df = display_df.rename(
    columns={
        "transactions": "Transactions",
        "revenue_recovered": "Revenue Recovered",
        "success_rate": "Success Rate"
    }
)

st.dataframe(
    display_df,
    use_container_width=True
)
