import pandas as pd

# Load dataset
df = pd.read_csv("data/raw/transactions.csv")

print("\n===== DATASET SHAPE =====")
print(df.shape)

print("\n===== COLUMNS =====")
print(df.columns.tolist())

print("\n===== FIRST 5 ROWS =====")
print(df.head())

print("\n===== DATA TYPES =====")
print(df.dtypes)

print("\n===== MISSING VALUES =====")
print(df.isnull().sum())

print("\n===== RECOVERY DISTRIBUTION =====")
print(df["recovery_possible"].value_counts())

print("\n===== FAILURE REASONS =====")
print(df["failure_reason"].value_counts())

print("\n===== PAYMENT METHODS =====")
print(df["payment_method"].value_counts())

print("\n===== RECOMMENDED ACTIONS =====")
print(df["recommended_action"].value_counts())

print("\n===== REVENUE METRICS =====")
print(f"Total revenue at risk: ₹{df['amount'].sum():,.2f}")

recoverable = df.loc[
    df["recovery_possible"] == 1,
    "amount"
].sum()

recovered = df["recovered_amount"].sum()

print(f"Potentially recoverable: ₹{recoverable:,.2f}")
print(f"Actually recovered: ₹{recovered:,.2f}")

print("\n===== RECOVERY RATE =====")
print(
    f"{recovered / df['amount'].sum() * 100:.2f}%"
)