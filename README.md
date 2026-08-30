# 💰 RecoverAI

### AI-Powered Payment Revenue Recovery Agent

RecoverAI is an AI-powered payment recovery agent that intelligently decides **what to do after a payment fails**.

Instead of blindly retrying every failed payment, RecoverAI evaluates transaction and customer signals, predicts recovery probability, and selects the recovery action with the highest expected revenue while applying business guardrails.

---

## 🚨 Problem

Payment failures can result in significant revenue loss..

A simple recovery strategy such as:

> "Payment failed → retry"

does not work equally well for every failure.

For example:

- A `network_error` may be recovered effectively through an immediate retry.
- An `insufficient_funds` failure may be better handled by retrying later.
- A `card_expired` failure may require customer follow-up or an alternate payment method.
- A `limit_exceeded` failure may be better recovered through an alternate payment method.

RecoverAI treats recovery as a **decision problem**, rather than a one-size-fits-all retry.

---

## 💡 Solution

RecoverAI combines:

- Machine learning recovery propensity
- Failure-specific recovery signals
- Customer behavior
- Transaction characteristics
- Action-specific effectiveness
- Business guardrails

to select the recovery strategy that maximizes expected revenue.

### Available Recovery Actions

| Action | Example Use Case |
|---|---|
| `retry` | Temporary/network failures |
| `retry_later` | Insufficient funds or temporary issues |
| `alternate_payment` | Bank declines or transaction limits |
| `customer_followup` | Authentication or expired card issues |
| `stop` | When further recovery is not appropriate |

---

## 🧠 How RecoverAI Works

```text
                Failed Transaction
                        │
                        ▼
              ┌───────────────────┐
              │ Transaction Data  │
              │ + Customer Signals│
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ ML Recovery Model │
              │ Random Forest     │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Action Evaluation │
              │ + Business        │
              │   Guardrails      │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Best Recovery     │
              │ Action            │
              └─────────┬─────────┘
                        │
                        ▼
                 Expected Revenue
```

---

## 🤖 Machine Learning

RecoverAI uses a **Random Forest Classifier** to estimate the probability that a failed transaction can be successfully recovered.

### Features

The model uses:

- Transaction amount
- Payment method
- Merchant category
- Customer tenure
- Previous success rate
- Transaction hour
- Retry count
- Customer monthly transaction frequency
- Failure reason

### Model Configuration

```text
Algorithm: Random Forest Classifier
Estimators: 300
Maximum depth: 12
Minimum samples per leaf: 5
Class weighting: Balanced
Random state: 42
```

Categorical variables are handled using one-hot encoding and missing values are handled through the preprocessing pipeline.

---

## 📊 Model Performance

The model was evaluated using a held-out test set.

| Metric | Result |
|---|---:|
| Accuracy | 73% |
| ROC-AUC | **0.8072** |
| Recovery-class Precision | 0.37 |
| Recovery-class Recall | 0.72 |
| Recovery-class F1 | 0.49 |

The model is designed to identify potentially recoverable transactions while accounting for the class imbalance in the dataset.

---

## 💰 Business Impact

RecoverAI was evaluated against an **always-retry baseline**.

### Evaluation Results

| Metric | Result |
|---|---:|
| Transactions | 10,000 |
| Revenue at Risk | ₹29,885,510 |
| Revenue Recovered | **₹21,258,690** |
| Transaction Recovery Rate | **73.20%** |
| Always-Retry Revenue Recovered | ₹13,250,550 |
| Additional Revenue | **₹8,008,140** |
| Revenue Lift | **60.44%** |

### Key Result

> On the simulated evaluation dataset, RecoverAI recovered ₹8,008,140 more revenue than the always-retry baseline, representing a 60.44% improvement in recovered revenue.

---

## 🔬 Evaluation Methodology

The project includes a recovery-scenario simulation framework.

For each transaction, multiple possible recovery actions are evaluated.

The simulation incorporates:

- Previous customer success rate
- Customer tenure
- Failure reason
- Retry history
- Transaction value
- Action-specific recovery effectiveness

This allows RecoverAI to compare different recovery strategies instead of assuming that retrying is always optimal.

> **Note:** The current evaluation uses synthetic transaction data and simulated recovery outcomes generated by the project's scenario-generation framework. The reported business results demonstrate the decisioning approach and are not claims about production payment-network performance.

---

## 🛡️ Business Guardrails

RecoverAI does not allow the decision engine to select every action in every situation.

Examples include:

### Retry Limit

Transactions that have already reached the retry threshold are prevented from receiving another retry.

### Authentication Failures

Authentication failures prioritize customer follow-up, alternate payment, or stopping instead of blindly retrying.

### Expired Cards

Expired cards are handled through customer follow-up, alternate payment, or stopping.

### High-Value Transactions

High-value transactions are prevented from using immediate retry and are evaluated using safer alternatives.

These guardrails make the recovery system more aligned with real-world business constraints.

---

## 🧮 Decision Logic

RecoverAI combines the ML prediction with action-specific recovery signals.

```text
Final Probability
=
0.6 × ML Recovery Probability
+
0.4 × Action-Specific Probability
```

Expected recovery is then estimated as:

```text
Expected Recovery
=
Transaction Amount × Final Probability
```

The action with the highest expected recovery value among the allowed actions is selected.

---

## 🏗️ Project Architecture

```text
recover-ai/
│
├── agent/
│   ├── decision_engine.py
│   ├── decision_engine_v2.py
│   └── action_executor.py
│
├── backend/
│   └── Backend services
│
├── data/
│   └── raw/
│       ├── transactions.csv
│       ├── recovery_scenarios.csv
│       ├── generate_data.py
│       └── generate_scenarios.py
│
├── database/
│   └── Database components
│
├── evaluation/
│   ├── v2_evaluation.py
│   ├── baseline_comparison.py
│   ├── rule_based_baseline.py
│   └── batch_evaluation.py
│
├── frontend/
│   └── app.py
│
└── ml/
    ├── train.py
    ├── model_analysis.py
    └── recovery_model.pkl
```

---

## 🖥️ Dashboard

RecoverAI includes an interactive Streamlit dashboard for monitoring recovery performance and analyzing individual transactions.

### Business Overview

The dashboard displays:

- Total transactions
- Revenue at risk
- Revenue recovered
- Recovery rate

### Recovery Performance

Users can compare:

- Recovery revenue by action
- Transaction distribution by action
- RecoverAI vs always-retry baseline
- Revenue lift

### Transaction Analysis

A failed transaction can be analyzed individually to obtain:

- Recommended recovery action
- Recovery probability
- Expected recovery revenue
- Failure reason
- Transaction details
- Recovery outcome

---

## 🔎 Example Decision

```text
Transaction: TXN_000001

Failure:
authentication_failed

Selected action:
customer_followup

Recovery probability:
70.36%

Expected recovery:
₹2,090.49
```

The decision is based on ML recovery propensity, action-specific recovery signals, and business guardrails.

---

## ⚙️ Tech Stack

- Python
- Pandas
- NumPy
- Scikit-learn
- Random Forest
- Joblib
- Streamlit
- FastAPI
- CSV-based transaction and scenario data
- Git & GitHub

---

## 🚀 Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/arshit-0101/recover-ai.git
cd recover-ai
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate the datasets

```bash
python data/raw/generate_data.py
python data/raw/generate_scenarios.py
```

### 5. Train the recovery model

```bash
python ml/train.py
```

This generates:

```text
ml/recovery_model.pkl
```

### 6. Start the application

```bash
streamlit run frontend/app.py
```

The dashboard will be available at:

```text
http://localhost:8501
```

---

## 📁 Key Components

### `ml/`

Contains the machine learning pipeline used to predict recovery probability.

### `agent/`

Contains the recovery decision engine responsible for selecting the optimal recovery action.

### `evaluation/`

Contains evaluation scripts and comparison against baseline strategies.

### `data/`

Contains transaction data and recovery scenario generation.

### `frontend/`

Contains the Streamlit dashboard.

### `backend/`

Contains backend services connecting the application and decision logic.

---

## 🎯 Why RecoverAI?

Traditional recovery:

```text
Payment fails
      ↓
Retry
```

RecoverAI:

```text
Payment fails
      ↓
Understand failure
      ↓
Evaluate customer + transaction signals
      ↓
Predict recovery probability
      ↓
Evaluate possible actions
      ↓
Apply business guardrails
      ↓
Choose highest-value recovery strategy
```

The goal is not simply to retry more.

The goal is to **recover more revenue with smarter decisions.**

---

## 🔮 Future Improvements

Potential production extensions include:

- Online learning from real recovery outcomes
- Real-time payment gateway integrations
- More sophisticated uplift modeling
- Contextual bandits for action selection
- Customer-level recovery policies
- Real-time monitoring and alerts
- Automated experimentation of recovery strategies
- Explainable AI for recovery decisions

---

## 👨‍💻 Project

**RecoverAI — AI-Powered Revenue Recovery Agent**

Built as a payment recovery decisioning system combining machine learning, action-specific signals, and business guardrails.
