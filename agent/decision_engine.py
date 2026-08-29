import pandas as pd


# ------------------------------------------------
# Load recovery scenarios
# ------------------------------------------------

df = pd.read_csv(
    "data/raw/recovery_scenarios.csv"
)


# ------------------------------------------------
# Guardrails
# ------------------------------------------------

MAX_RETRIES = 2
HIGH_VALUE_LIMIT = 15000


def choose_action(transaction):
    """
    Select the recovery action with the highest
    expected recovered value while respecting
    business guardrails.
    """

    # Filter scenarios for this transaction
    scenarios = df[
        df["transaction_id"]
        == transaction["transaction_id"]
    ].copy()

    # --------------------------------------------
    # Guardrail 1: too many retries
    # --------------------------------------------

    if transaction["retry_count"] >= MAX_RETRIES:

        scenarios = scenarios[
            scenarios["action"] != "retry"
        ]

    # --------------------------------------------
    # Guardrail 2: authentication failures
    # --------------------------------------------

    if transaction["failure_reason"] == "authentication_failed":

        scenarios = scenarios[
            scenarios["action"].isin([
                "customer_followup",
                "alternate_payment",
                "stop"
            ])
        ]

    # --------------------------------------------
    # Guardrail 3: expired card
    # --------------------------------------------

    if transaction["failure_reason"] == "card_expired":

        scenarios = scenarios[
            scenarios["action"].isin([
                "customer_followup",
                "alternate_payment",
                "stop"
            ])
        ]

    # --------------------------------------------
    # Guardrail 4: high-value transactions
    # --------------------------------------------

    if transaction["amount"] >= HIGH_VALUE_LIMIT:

        scenarios = scenarios[
            scenarios["action"] != "retry"
        ]

    # --------------------------------------------
    # Safety fallback
    # --------------------------------------------

    if scenarios.empty:

        return {
            "action": "stop",
            "probability": 0.0,
            "expected_revenue": 0.0,
            "reason": "No safe recovery action available"
        }

    # --------------------------------------------
    # Expected recovery value
    # --------------------------------------------

    scenarios["expected_revenue"] = (
        scenarios["amount"]
        * scenarios["simulated_success_probability"]
    )

    # Choose action with highest expected value
    best = scenarios.loc[
        scenarios["expected_revenue"].idxmax()
    ]

    return {
        "action": best["action"],
        "probability": best[
            "simulated_success_probability"
        ],
        "expected_revenue": best[
            "expected_revenue"
        ],
        "reason": (
            f"Highest expected recovery value "
            f"among allowed actions"
        )
    }


# ------------------------------------------------
# Test on first transactions
# ------------------------------------------------
if __name__ == "__main__":
    transactions = pd.read_csv(
        "data/raw/transactions.csv"
    )


    print("\n===== RECOVERY AGENT DECISIONS =====\n")


    for _, transaction in transactions.head(10).iterrows():

        decision = choose_action(transaction)

        print(
            f"Transaction: "
            f"{transaction['transaction_id']}"
        )

        print(
            f"Failure: "
            f"{transaction['failure_reason']}"
        )

        print(
            f"Amount: "
            f"₹{transaction['amount']:,.2f}"
        )

        print(
            f"Selected action: "
            f"{decision['action']}"
        )

        print(
            f"Success probability: "
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