import numpy as np
import pandas as pd

np.random.seed(42)

# Load our original transaction dataset
df = pd.read_csv("data/raw/transactions.csv")

# Possible recovery actions
actions = [
    "retry",
    "retry_later",
    "alternate_payment",
    "customer_followup",
    "stop"
]


def calculate_action_probability(row, action):
    """
    Simulate the probability that a particular
    recovery action successfully recovers the payment.
    """

    base = (
        0.20
        + 0.45 * row["previous_success_rate"]
        + 0.08 * (row["customer_tenure_days"] / 1500)
    )

    failure = row["failure_reason"]

    # Action-specific effectiveness
    if action == "retry":

        if failure == "network_error":
            base += 0.35
        elif failure == "bank_decline":
            base += 0.05
        elif failure == "insufficient_funds":
            base -= 0.10
        else:
            base -= 0.15

    elif action == "retry_later":

        if failure == "insufficient_funds":
            base += 0.25
        elif failure == "network_error":
            base += 0.15
        else:
            base -= 0.05

    elif action == "alternate_payment":

        if failure in [
            "bank_decline",
            "limit_exceeded"
        ]:
            base += 0.25
        elif failure == "card_expired":
            base += 0.20
        else:
            base += 0.05

    elif action == "customer_followup":

        if failure in [
            "card_expired",
            "authentication_failed"
        ]:
            base += 0.25
        elif failure == "insufficient_funds":
            base += 0.10
        else:
            base -= 0.05

    elif action == "stop":

        base = 0.0

    # More retries should reduce probability
    base -= 0.08 * row["retry_count"]

    # Very high-value transactions are slightly harder
    if row["amount"] > 10000:
        base -= 0.05

    return np.clip(base, 0.01, 0.95)


# Create action scenarios
scenarios = []

for _, row in df.iterrows():

    for action in actions:

        probability = calculate_action_probability(
            row,
            action
        )

        # Simulate actual outcome
        recovered = int(
            np.random.random() < probability
        )

        recovered_amount = (
            row["amount"]
            if recovered == 1
            else 0
        )

        scenarios.append({
            "transaction_id": row["transaction_id"],
            "amount": row["amount"],
            "payment_method": row["payment_method"],
            "merchant_category": row["merchant_category"],
            "customer_tenure_days": row[
                "customer_tenure_days"
            ],
            "previous_success_rate": row[
                "previous_success_rate"
            ],
            "transaction_hour": row[
                "transaction_hour"
            ],
            "retry_count": row["retry_count"],
            "customer_monthly_transactions": row[
                "customer_monthly_transactions"
            ],
            "failure_reason": row["failure_reason"],
            "action": action,
            "simulated_success_probability": round(
                probability,
                4
            ),
            "recovered": recovered,
            "recovered_amount": recovered_amount
        })


scenario_df = pd.DataFrame(scenarios)

# Save
output_path = "data/raw/recovery_scenarios.csv"

scenario_df.to_csv(
    output_path,
    index=False
)

print(
    f"Generated {len(scenario_df):,} "
    "recovery scenarios"
)

print(
    f"Transactions: {df.shape[0]:,}"
)

print(
    f"Actions per transaction: {len(actions)}"
)

print(
    f"Total simulated recovered revenue: "
    f"₹{scenario_df['recovered_amount'].sum():,.2f}"
)

print("\nAverage success probability by action:")

print(
    scenario_df.groupby("action")[
        "simulated_success_probability"
    ]
    .mean()
    .sort_values(ascending=False)
)

print("\nScenario preview:")

print(
    scenario_df.head(10).to_string(
        index=False
    )
)