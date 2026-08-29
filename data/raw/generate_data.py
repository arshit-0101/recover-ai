import numpy as np
import pandas as pd

np.random.seed(42)

N = 10000

payment_methods = ["card", "upi", "netbanking", "wallet"]
failure_reasons = [
    "insufficient_funds",
    "bank_decline",
    "network_error",
    "card_expired",
    "authentication_failed",
    "limit_exceeded",
]

merchant_categories = [
    "ecommerce",
    "saas",
    "education",
    "travel",
    "food",
]

data = pd.DataFrame({
    "transaction_id": [f"TXN_{i:06d}" for i in range(1, N + 1)],
    "amount": np.round(np.random.lognormal(7.5, 1.0, N), 2),
    "payment_method": np.random.choice(
        payment_methods,
        N,
        p=[0.40, 0.40, 0.12, 0.08]
    ),
    "merchant_category": np.random.choice(
        merchant_categories,
        N
    ),
    "customer_tenure_days": np.random.randint(1, 1500, N),
    "previous_success_rate": np.round(
        np.random.beta(8, 2, N), 3
    ),
    "transaction_hour": np.random.randint(0, 24, N),
    "retry_count": np.random.randint(0, 4, N),
    "customer_monthly_transactions": np.random.randint(
        1, 30, N
    ),
    "failure_reason": np.random.choice(
        failure_reasons,
        N
    ),
})

# Create realistic recovery probability
recovery_score = (
    0.35 * data["previous_success_rate"]
    + 0.20 * (data["customer_tenure_days"] / 1500)
    + 0.15 * (data["retry_count"] == 0)
    + 0.15 * (data["failure_reason"] == "network_error")
    + 0.10 * (data["failure_reason"] == "insufficient_funds")
    + 0.05 * (data["failure_reason"] == "bank_decline")
)

# Add controlled randomness
recovery_score += np.random.normal(0, 0.08, N)

data["recovery_probability"] = np.clip(
    recovery_score, 0, 1
).round(3)

data["recovery_possible"] = (
    data["recovery_probability"] >= 0.50
).astype(int)

# Define recovery action
def choose_action(row):
    if row["recovery_probability"] < 0.25:
        return "stop"

    if row["failure_reason"] == "network_error":
        return "retry"

    if row["failure_reason"] == "insufficient_funds":
        return "retry_later"

    if row["failure_reason"] in [
        "card_expired",
        "authentication_failed"
    ]:
        return "customer_followup"

    if row["failure_reason"] == "limit_exceeded":
        return "alternate_payment"

    if row["failure_reason"] == "bank_decline":
        return "alternate_payment"

    return "customer_followup"


data["recommended_action"] = data.apply(
    choose_action,
    axis=1
)

# Simulate whether the recovery action succeeded
success_probability = (
    data["recovery_probability"] * 0.75
)

data["recovered"] = (
    (data["recovery_possible"] == 1)
    & (np.random.random(N) < success_probability)
).astype(int)

data["recovered_amount"] = np.where(
    data["recovered"] == 1,
    data["amount"],
    0
)

# Save dataset
output_path = "data/raw/transactions.csv"
data.to_csv(output_path, index=False)

print(f"Generated {len(data):,} transactions")
print(f"Revenue at risk: ₹{data['amount'].sum():,.2f}")
print(
    f"Potentially recoverable: "
    f"{data['recovery_possible'].sum():,}"
)
print(
    f"Recovered revenue in simulation: "
    f"₹{data['recovered_amount'].sum():,.2f}"
)

print("\nDataset preview:")
print(data.head())
