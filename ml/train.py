import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    confusion_matrix
)


# ---------------------------------------
# 1. Load data
# ---------------------------------------

df = pd.read_csv("data/raw/transactions.csv")


# ---------------------------------------
# 2. Define features and target
# ---------------------------------------

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

# Actual outcome of the recovery simulation
y = df["recovered"]


# ---------------------------------------
# 3. Train / test split
# ---------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ---------------------------------------
# 4. Identify feature types
# ---------------------------------------

categorical_features = [
    "payment_method",
    "merchant_category",
    "failure_reason"
]

numeric_features = [
    "amount",
    "customer_tenure_days",
    "previous_success_rate",
    "transaction_hour",
    "retry_count",
    "customer_monthly_transactions"
]


# ---------------------------------------
# 5. Preprocessing
# ---------------------------------------

numeric_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        )
    ]
)

categorical_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "num",
            numeric_transformer,
            numeric_features
        ),
        (
            "cat",
            categorical_transformer,
            categorical_features
        )
    ]
)


# ---------------------------------------
# 6. Model
# ---------------------------------------

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_leaf=5,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)


# ---------------------------------------
# 7. Complete ML pipeline
# ---------------------------------------

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# ---------------------------------------
# 8. Train
# ---------------------------------------

print("Training Recovery Probability Model...")

pipeline.fit(X_train, y_train)


# ---------------------------------------
# 9. Evaluate
# ---------------------------------------

predictions = pipeline.predict(X_test)

probabilities = pipeline.predict_proba(X_test)[:, 1]

print("\n===== CLASSIFICATION REPORT =====")
print(
    classification_report(
        y_test,
        predictions
    )
)

print("\n===== ROC-AUC =====")

auc = roc_auc_score(
    y_test,
    probabilities
)

print(f"ROC-AUC: {auc:.4f}")

print("\n===== CONFUSION MATRIX =====")

print(
    confusion_matrix(
        y_test,
        predictions
    )
)


# ---------------------------------------
# 10. Save model
# ---------------------------------------

joblib.dump(
    pipeline,
    "ml/recovery_model.pkl"
)

print(
    "\nModel saved to "
    "ml/recovery_model.pkl"
)