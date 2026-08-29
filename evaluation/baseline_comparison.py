import pandas as pd
import numpy as np


np.random.seed(42)


# ============================================================
# LOAD DATA
# ============================================================

transactions = pd.read_csv(
    "data/raw/transactions.csv"
)

scenarios = pd.read_csv(
    "data/raw/recovery_scenarios.csv"
)

v2_results = pd.read_csv(
    "data/processed/v2_results.csv"
)


# ============================================================
# SIMULATE ALWAYS-RETRY BASELINE
# ============================================================

def simulate_retry(transaction):

    scenario = scenarios[
        (scenarios["transaction_id"] ==
         transaction["transaction_id"])
        &
        (scenarios["action"] == "retry")
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


baseline_revenue = 0.0
baseline_successes = 0


for _, transaction in transactions.iterrows():

    recovered = simulate_retry(transaction)

    if recovered > 0:
        baseline_successes += 1

    baseline_revenue += recovered


# ============================================================
# RECOVERAI V2 RESULTS
# ============================================================

agent_successes = v2_results["success"].sum()

agent_revenue = v2_results[
    "recovered_amount"
].sum()


# ============================================================
# METRICS
# ============================================================

total_revenue = transactions[
    "amount"
].sum()


baseline_recovery_rate = (
    baseline_successes
    / len(transactions)
    * 100
)


agent_recovery_rate = (
    agent_successes
    / len(v2_results)
    * 100
)


baseline_revenue_rate = (
    baseline_revenue
    / total_revenue
    * 100
)


agent_revenue_rate = (
    agent_revenue
    / total_revenue
    * 100
)


additional_revenue = (
    agent_revenue
    - baseline_revenue
)


revenue_lift = (
    additional_revenue
    / baseline_revenue
    * 100
)


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n" + "=" * 60)

print("           BASELINE vs RECOVERAI V2")

print("=" * 60)


print(
    f"\nRevenue at risk: "
    f"₹{total_revenue:,.2f}"
)


print("\n--- ALWAYS RETRY BASELINE ---")


print(
    f"Successful recoveries: "
    f"{baseline_successes:,}"
)


print(
    f"Transaction recovery rate: "
    f"{baseline_recovery_rate:.2f}%"
)


print(
    f"Revenue recovered: "
    f"₹{baseline_revenue:,.2f}"
)


print(
    f"Revenue recovery rate: "
    f"{baseline_revenue_rate:.2f}%"
)


print("\n--- RECOVERAI V2 ---")


print(
    f"Successful recoveries: "
    f"{agent_successes:,}"
)


print(
    f"Transaction recovery rate: "
    f"{agent_recovery_rate:.2f}%"
)


print(
    f"Revenue recovered: "
    f"₹{agent_revenue:,.2f}"
)


print(
    f"Revenue recovery rate: "
    f"{agent_revenue_rate:.2f}%"
)


print("\n--- BUSINESS IMPACT ---")


print(
    f"Additional revenue recovered: "
    f"₹{additional_revenue:,.2f}"
)


print(
    f"Revenue lift vs baseline: "
    f"{revenue_lift:.2f}%"
)


print("=" * 60)