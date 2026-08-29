import pandas as pd
import joblib

from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split


# Load data and trained model
df = pd.read_csv("data/raw/transactions.csv")
pipeline = joblib.load("ml/recovery_model.pkl")


features = [
    "amount",
    "payment_method",
    "merchant_category",
    "customer_tenure_days",
    "previous_success_rate",
    "transaction_hour",
    "retry_count",
    "customer_monthly_transactions",
    "failure_reason"
]

X = df[features]
y = df["recovered"]


# Same test split used during training
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ---------------------------------------
# 1. Permutation feature importance
# ---------------------------------------

print("\n===== FEATURE IMPORTANCE =====")

result = permutation_importance(
    pipeline,
    X_test,
    y_test,
    n_repeats=5,
    random_state=42,
    scoring="roc_auc"
)

importance = pd.DataFrame({
    "feature": X_test.columns,
    "importance": result.importances_mean
})

importance = importance.sort_values(
    "importance",
    ascending=False
)

print(importance.to_string(index=False))


# ---------------------------------------
# 2. Example predictions
# ---------------------------------------

print("\n===== SAMPLE PREDICTIONS =====")

samples = X_test.head(10).copy()

probabilities = pipeline.predict_proba(
    samples
)[:, 1]

for i, probability in enumerate(probabilities):
    print(
        f"{samples.iloc[i]['failure_reason']:25s}"
        f" | Amount: ₹{samples.iloc[i]['amount']:,.2f}"
        f" | Recovery probability: {probability:.2%}"
    )


# ---------------------------------------
# 3. Business-level metrics
# ---------------------------------------

df["predicted_recovery_probability"] = pipeline.predict_proba(
    df[features]
)[:, 1]

print("\n===== BUSINESS SEGMENTS =====")

print(
    df.groupby("failure_reason")[
        "predicted_recovery_probability"
    ].mean().sort_values(ascending=False)
)


print("\nAnalysis complete.")