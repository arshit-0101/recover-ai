import pandas as pd
import numpy as np

from decision_engine import choose_action


# --------------------------------------------
# Load scenarios
# --------------------------------------------

scenarios = pd.read_csv(
    "data/raw/recovery_scenarios.csv"
)


def execute_action(transaction):
    """
    Execute the action selected by the
    Recovery Decision Agent.
    """

    # Get agent's decision
    decision = choose_action(transaction)

    selected_action = decision["action"]

    # Find the scenario corresponding
    # to the selected action
    scenario = scenarios[
        (scenarios["transaction_id"] ==
         transaction["transaction_id"])
        &
        (scenarios["action"] ==
         selected_action)
    ]

    if scenario.empty:
        return {
            "transaction_id":
                transaction["transaction_id"],
            "action": "stop",
            "success": False,
            "recovered_amount": 0.0,
            "message":
                "No valid action scenario found"
        }

    scenario = scenario.iloc[0]

    probability = scenario[
        "simulated_success_probability"
    ]

    # Simulate actual execution
    success = np.random.random() < probability

    if success:
        recovered_amount = transaction["amount"]
        status = "recovered"
    else:
        recovered_amount = 0.0
        status = "failed"

    return {
        "transaction_id":
            transaction["transaction_id"],

        "action":
            selected_action,

        "probability":
            probability,

        "status":
            status,

        "success":
            bool(success),

        "recovered_amount":
            recovered_amount,

        "expected_revenue":
            decision["expected_revenue"]
    }


# --------------------------------------------
# Test executor
# --------------------------------------------

transactions = (
    scenarios
    .drop_duplicates("transaction_id")
)


print("\n===== ACTION EXECUTOR TEST =====\n")


for _, transaction in transactions.head(10).iterrows():

    result = execute_action(transaction)

    print(
        f"Transaction: "
        f"{result['transaction_id']}"
    )

    print(
        f"Action: "
        f"{result['action']}"
    )

    print(
        f"Success probability: "
        f"{result['probability']:.2%}"
    )

    print(
        f"Status: "
        f"{result['status']}"
    )

    print(
        f"Recovered: "
        f"₹{result['recovered_amount']:,.2f}"
    )

    print("-" * 55)