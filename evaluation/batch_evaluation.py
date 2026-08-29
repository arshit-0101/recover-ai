import pandas as pd
import numpy as np

from agent.decision_engine import choose_action


# --------------------------------------------
# Load transactions
# --------------------------------------------

transactions = pd.read_csv(
    "data/raw/transactions.csv"
)

scenarios = pd.read_csv(
    "data/raw/recovery_scenarios.csv"
)


# --------------------------------------------
# Execute agent over all transactions
# --------------------------------------------

results = []

np.random.seed(42)

print("Running RecoverAI on 10,000 transactions...\n")

for _, transaction in transactions.iterrows():

    decision = choose_action(transaction)

    action = decision["action"]

    # Find corresponding action scenario
    scenario = scenarios[
        (scenarios["transaction_id"]
         == transaction["transaction_id"])
        &
        (scenarios["action"] == action)
    ]

    if scenario.empty:
        success = False
        recovered_amount = 0.0

    else:
        scenario = scenario.iloc[0]

        probability = (
            scenario[
                "simulated_success_probability"
            ]
        )

        success = (
            np.random.random() < probability
        )

        recovered_amount = (
            transaction["amount"]
            if success
            else 0.0
        )

    results.append({
        "transaction_id":
            transaction["transaction_id"],

        "amount":
            transaction["amount"],

        "failure_reason":
            transaction["failure_reason"],

        "action":
            action,

        "success_probability":
            decision["probability"],

        "expected_revenue":
            decision["expected_revenue"],

        "success":
            int(success),

        "recovered_amount":
            recovered_amount
    })


# --------------------------------------------
# Create results dataframe
# --------------------------------------------

results_df = pd.DataFrame(results)


# --------------------------------------------
# Business metrics
# --------------------------------------------

total_revenue = results_df["amount"].sum()

recovered_revenue = (
    results_df["recovered_amount"].sum()
)

successful_recoveries = (
    results_df["success"].sum()
)

total_transactions = len(results_df)

recovery_rate = (
    successful_recoveries
    / total_transactions
    * 100
)

revenue_recovery_rate = (
    recovered_revenue
    / total_revenue
    * 100
)


# --------------------------------------------
# Print results
# --------------------------------------------

print("=" * 60)
print("             RECOVERAI BATCH RESULTS")
print("=" * 60)

print(
    f"\nTransactions processed: "
    f"{total_transactions:,}"
)

print(
    f"Revenue at risk: "
    f"₹{total_revenue:,.2f}"
)

print(
    f"Successful recoveries: "
    f"{successful_recoveries:,}"
)

print(
    f"Transaction recovery rate: "
    f"{recovery_rate:.2f}%"
)

print(
    f"\nRevenue recovered: "
    f"₹{recovered_revenue:,.2f}"
)

print(
    f"Revenue recovery rate: "
    f"{revenue_recovery_rate:.2f}%"
)


# --------------------------------------------
# Action distribution
# --------------------------------------------

print("\n===== ACTION DISTRIBUTION =====")

print(
    results_df["action"]
    .value_counts()
)


# --------------------------------------------
# Revenue by action
# --------------------------------------------

print("\n===== RECOVERY BY ACTION =====")

action_summary = (
    results_df
    .groupby("action")
    .agg(
        transactions=("transaction_id", "count"),
        successful=("success", "sum"),
        revenue_recovered=(
            "recovered_amount",
            "sum"
        )
    )
    .sort_values(
        "revenue_recovered",
        ascending=False
    )
)

print(action_summary)


# --------------------------------------------
# Save results
# --------------------------------------------

results_df.to_csv(
    "data/processed/agent_results.csv",
    index=False
)

print(
    "\nResults saved to:"
    " data/processed/agent_results.csv"
)