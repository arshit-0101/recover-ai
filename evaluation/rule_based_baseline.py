import pandas as pd
import numpy as np


np.random.seed(42)

# Load data
transactions = pd.read_csv(
    "data/raw/transactions.csv"
)

scenarios = pd.read_csv(
    "data/raw/recovery_scenarios.csv"
)


# --------------------------------------------
# Rule-based action selection
# --------------------------------------------

def choose_rule_based_action(transaction):

    failure = transaction["failure_reason"]

    if failure == "network_error":
        return "retry"

    elif failure == "insufficient_funds":
        return "retry_later"

    elif failure == "bank_decline":
        return "alternate_payment"

    elif failure == "card_expired":
        return "customer_followup"

    elif failure == "limit_exceeded":
        return "alternate_payment"

    elif failure == "authentication_failed":
        return "customer_followup"

    return "stop"


# --------------------------------------------
# Simulate action
# --------------------------------------------

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

    success = (
        np.random.random() < probability
    )

    if success:
        return transaction["amount"]

    return 0.0


# --------------------------------------------
# Run baseline
# --------------------------------------------

recovered_revenue = 0.0
successful_recoveries = 0

for _, transaction in transactions.iterrows():

    action = choose_rule_based_action(
        transaction
    )

    recovered = simulate_action(
        transaction,
        action
    )

    if recovered > 0:
        successful_recoveries += 1

    recovered_revenue += recovered


# --------------------------------------------
# Metrics
# --------------------------------------------

total_revenue = transactions["amount"].sum()

recovery_rate = (
    successful_recoveries
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
print("          RULE-BASED BASELINE")
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
    f"{successful_recoveries:,}"
)

print(
    f"Transaction recovery rate: "
    f"{recovery_rate:.2f}%"
)

print(
    f"Revenue recovered: "
    f"₹{recovered_revenue:,.2f}"
)

print(
    f"Revenue recovery rate: "
    f"{revenue_recovery_rate:.2f}%"
)

print("=" * 60)