import pandas as pd
import numpy as np

from agent.decision_engine_v2 import choose_action


np.random.seed(42)

# Load data
transactions = pd.read_csv(
    "data/raw/transactions.csv"
)

scenarios = pd.read_csv(
    "data/raw/recovery_scenarios.csv"
)


def simulate_action(transaction, action):

    scenario = scenarios[
        (scenarios["transaction_id"]
         == transaction["transaction_id"])
        &
        (scenarios["action"] == action)
    ]

    if scenario.empty:
        return 0.0

    probability = scenario.iloc[0][
        "simulated_success_probability"
    ]

    success = np.random.random() < probability

    if success:
        return transaction["amount"]

    return 0.0


# --------------------------------------------
# Run RecoverAI V2
# --------------------------------------------

results = []

for _, transaction in transactions.iterrows():

    decision = choose_action(transaction)

    recovered = simulate_action(
        transaction,
        decision["action"]
    )

    results.append({
        "transaction_id":
            transaction["transaction_id"],

        "amount":
            transaction["amount"],

        "failure_reason":
            transaction["failure_reason"],

        "action":
            decision["action"],

        "success_probability":
            decision["probability"],

        "expected_revenue":
            decision["expected_revenue"],

        "recovered_amount":
            recovered,

        "success":
            int(recovered > 0)
    })


results_df = pd.DataFrame(results)


# --------------------------------------------
# Metrics
# --------------------------------------------

total_revenue = transactions["amount"].sum()

successful = results_df["success"].sum()

recovered_revenue = (
    results_df["recovered_amount"].sum()
)

transaction_recovery_rate = (
    successful
    / len(transactions)
    * 100
)

revenue_recovery_rate = (
    recovered_revenue
    / total_revenue
    * 100
)


# --------------------------------------------
# Results
# --------------------------------------------

print("\n" + "=" * 60)
print("              RECOVERAI V2 EVALUATION")
print("=" * 60)

print(
    f"\nTransactions processed: "
    f"{len(transactions):,}"
)

print(
    f"Revenue at risk: "
    f"₹{total_revenue:,.2f}"
)

print(
    f"Successful recoveries: "
    f"{successful:,}"
)

print(
    f"Transaction recovery rate: "
    f"{transaction_recovery_rate:.2f}%"
)

print(
    f"Revenue recovered: "
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
# Save results
# --------------------------------------------

results_df.to_csv(
    "data/processed/v2_results.csv",
    index=False
)

print(
    "\nResults saved to:"
    " data/processed/v2_results.csv"
)

print("=" * 60)