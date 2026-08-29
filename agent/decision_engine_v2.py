import pandas as pd
import joblib


# ------------------------------------------------
# Load recovery scenarios
# ------------------------------------------------

scenarios_df = pd.read_csv(
    "data/raw/recovery_scenarios.csv"
)


# ------------------------------------------------
# Load ML recovery model
# ------------------------------------------------

model = joblib.load(
    "ml/recovery_model.pkl"
)


# ------------------------------------------------
# Guardrails
# ------------------------------------------------

MAX_RETRIES = 2
HIGH_VALUE_LIMIT = 15000


# ------------------------------------------------
# Candidate actions
# ------------------------------------------------

ACTIONS = [
    "retry",
    "retry_later",
    "alternate_payment",
    "customer_followup",
    "stop"
]


def get_allowed_actions(transaction):

    allowed = ACTIONS.copy()

    # Too many retries
    if transaction["retry_count"] >= MAX_RETRIES:
        allowed.remove("retry")

    # Authentication failure
    if transaction["failure_reason"] == "authentication_failed":
        allowed = [
            action for action in allowed
            if action in [
                "customer_followup",
                "alternate_payment",
                "stop"
            ]
        ]

    # Expired card
    if transaction["failure_reason"] == "card_expired":
        allowed = [
            action for action in allowed
            if action in [
                "customer_followup",
                "alternate_payment",
                "stop"
            ]
        ]

    # High-value transaction
    if transaction["amount"] >= HIGH_VALUE_LIMIT:
        allowed = [
            action for action in allowed
            if action != "retry"
        ]

    return allowed


def choose_action(transaction):

    # ------------------------------------------------
    # Get ML recovery probability
    # ------------------------------------------------

    features = pd.DataFrame([{
        "amount": transaction["amount"],
        "payment_method":
            transaction["payment_method"],
        "merchant_category":
            transaction["merchant_category"],
        "customer_tenure_days":
            transaction["customer_tenure_days"],
        "previous_success_rate":
            transaction["previous_success_rate"],
        "transaction_hour":
            transaction["transaction_hour"],
        "retry_count":
            transaction["retry_count"],
        "customer_monthly_transactions":
            transaction[
                "customer_monthly_transactions"
            ],
        "failure_reason":
            transaction["failure_reason"]
    }])

    ml_probability = model.predict_proba(
        features
    )[0][1]


    # ------------------------------------------------
    # Get allowed actions
    # ------------------------------------------------

    allowed_actions = get_allowed_actions(
        transaction
    )

    if not allowed_actions:

        return {
            "action": "stop",
            "probability": 0.0,
            "expected_revenue": 0.0,
            "reason":
                "No safe recovery action available"
        }


    # ------------------------------------------------
    # Evaluate candidate actions
    # ------------------------------------------------

    candidates = []

    for action in allowed_actions:

        scenario = scenarios_df[
            (scenarios_df["transaction_id"]
             == transaction["transaction_id"])
            &
            (scenarios_df["action"] == action)
        ]

        if scenario.empty:
            continue

        scenario = scenario.iloc[0]

        scenario_probability = (
            scenario[
                "simulated_success_probability"
            ]
        )

        # Combine ML signal with action-specific
        # simulation signal
        final_probability = (
            0.6 * ml_probability
            +
            0.4 * scenario_probability
        )

        expected_revenue = (
            transaction["amount"]
            * final_probability
        )

        candidates.append({
            "action": action,
            "probability": final_probability,
            "expected_revenue":
                expected_revenue
        })


    # ------------------------------------------------
    # Safety fallback
    # ------------------------------------------------

    if not candidates:

        return {
            "action": "stop",
            "probability": 0.0,
            "expected_revenue": 0.0,
            "reason":
                "No valid recovery scenario found"
        }


    # ------------------------------------------------
    # Choose highest expected value
    # ------------------------------------------------

    best = max(
        candidates,
        key=lambda x: x["expected_revenue"]
    )


    return {
        "action": best["action"],
        "probability": best["probability"],
        "expected_revenue":
            best["expected_revenue"],
        "reason":
            "ML recovery propensity + "
            "action-specific recovery signal "
            "under business guardrails"
    }


# ------------------------------------------------
# Test
# ------------------------------------------------

if __name__ == "__main__":
    transactions = pd.read_csv(
        "data/raw/transactions.csv"
    )

    print(
        "\n===== RECOVERAI V2 =====\n"
    )

    for _, transaction in (
        transactions.head(10).iterrows()
    ):

        decision = choose_action(
            transaction
        )

        print(
            f"Transaction: "
            f"{transaction['transaction_id']}"
        )

        print(
            f"Failure: "
            f"{transaction['failure_reason']}"
        )

        print(
            f"Selected action: "
            f"{decision['action']}"
        )

        print(
            f"Probability: "
            f"{decision['probability']:.2%}"
        )

        print(
            f"Expected recovery: "
            f"₹{decision['expected_revenue']:,.2f}"
        )

        print(
            f"Reason: "
            f"{decision['reason']}"
        )

        print("-" * 60)