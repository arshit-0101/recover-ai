from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib

from agent.decision_engine_v2 import choose_action


# ------------------------------------------------
# Create API
# ------------------------------------------------

app = FastAPI(
    title="RecoverAI API",
    description="AI-powered revenue recovery agent",
    version="2.0"
)


# ------------------------------------------------
# Load transaction dataset
# ------------------------------------------------

transactions = pd.read_csv(
    "data/raw/transactions.csv"
)


# ------------------------------------------------
# Request schema
# ------------------------------------------------

class TransactionRequest(BaseModel):

    transaction_id: str


# ------------------------------------------------
# Health check
# ------------------------------------------------

@app.get("/")
def home():

    return {
        "status": "online",
        "service": "RecoverAI",
        "version": "2.0"
    }


# ------------------------------------------------
# Get recovery decision
# ------------------------------------------------

@app.post("/recover")
def recover(transaction: TransactionRequest):

    matching = transactions[
        transactions["transaction_id"]
        == transaction.transaction_id
    ]

    if matching.empty:

        return {
            "error": "Transaction not found"
        }

    transaction_data = (
        matching.iloc[0].to_dict()
    )

    decision = choose_action(
        transaction_data
    )

    return {
        "transaction_id":
            transaction.transaction_id,

        "failure_reason":
            transaction_data["failure_reason"],

        "amount":
            transaction_data["amount"],

        "selected_action":
            decision["action"],

        "recovery_probability":
            decision["probability"],

        "expected_recovery":
            decision["expected_revenue"],

        "reason":
            decision["reason"]
    }
# ------------------------------------------------
# Dashboard metrics
# ------------------------------------------------

@app.get("/metrics")
def metrics():

    revenue_at_risk = transactions["amount"].sum()

    successful_recoveries = transactions[
        transactions["recovered"] == 1
    ]

    revenue_recovered = successful_recoveries[
        "recovered_amount"
    ].sum()

    transaction_count = len(transactions)

    recovery_rate = (
        revenue_recovered / revenue_at_risk * 100
        if revenue_at_risk > 0
        else 0
    )

    return {
        "transactions": transaction_count,
        "revenue_at_risk": round(
            revenue_at_risk, 2
        ),
        "revenue_recovered": round(
            revenue_recovered, 2
        ),
        "revenue_recovery_rate": round(
            recovery_rate, 2
        )
    }