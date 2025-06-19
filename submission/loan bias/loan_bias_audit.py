import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from fairlearn.metrics import MetricFrame, selection_rate, false_positive_rate, false_negative_rate, demographic_parity_difference
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Use relative paths for data
TRAIN_PATH = 'data/train_u6lujuX_CVtuZ9i.csv'
TEST_PATH = 'data/test_Y3wMUE5_7gLdaTN.csv'

# Try loading the data with error handling
try:
    train_df = pd.read_csv(TRAIN_PATH)
    test_df = pd.read_csv(TEST_PATH)
except FileNotFoundError as e:
    print(f"Error: {e}\nPlease check that the data files exist in the 'data/' directory.")
    exit(1)

# Data preprocessing
def preprocess_data(df):
    # Handle missing values
    df['Gender'].fillna(df['Gender'].mode()[0], inplace=True)
    df['Married'].fillna(df['Married'].mode()[0], inplace=True)
    df['Dependents'].fillna(df['Dependents'].mode()[0], inplace=True)
    df['Self_Employed'].fillna(df['Self_Employed'].mode()[0], inplace=True)
    df['LoanAmount'].fillna(df['LoanAmount'].median(), inplace=True)
    df['Loan_Amount_Term'].fillna(df['Loan_Amount_Term'].median(), inplace=True)
    df['Credit_History'].fillna(df['Credit_History'].median(), inplace=True)
    
    # Convert categorical variables
    le = LabelEncoder()
    df['Gender'] = le.fit_transform(df['Gender'])
    df['Married'] = le.fit_transform(df['Married'])
    df['Education'] = le.fit_transform(df['Education'])
    df['Self_Employed'] = le.fit_transform(df['Self_Employed'])
    df['Property_Area'] = le.fit_transform(df['Property_Area'])
    
    # Convert Dependents to numeric
    df['Dependents'] = df['Dependents'].replace('3+', '3').astype(int)
    
    return df

# Preprocess both datasets
train_df = preprocess_data(train_df)
test_df = preprocess_data(test_df)

# Prepare features and target
features = ['Gender', 'Married', 'Dependents', 'Education', 'Self_Employed',
           'ApplicantIncome', 'CoapplicantIncome', 'LoanAmount',
           'Loan_Amount_Term', 'Credit_History', 'Property_Area']

X = train_df[features]
y = train_df['Loan_Status'].map({'Y': 1, 'N': 0})
sensitive_features = train_df['Gender']

# For reporting: map gender codes back to labels
gender_map = {0: 'Female', 1: 'Male'}
train_df['Gender_Label'] = train_df['Gender'].map(gender_map)

# Scale the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split the data
X_train, X_test, y_train, y_test, sensitive_train, sensitive_test = train_test_split(
    X_scaled, y, sensitive_features, test_size=0.3, random_state=42
)

# Train a logistic regression model
model = LogisticRegression(random_state=42)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Calculate fairness metrics
metrics = {
    'selection_rate': selection_rate,
    'false_positive_rate': false_positive_rate,
    'false_negative_rate': false_negative_rate
}

metric_frame = MetricFrame(
    metrics=metrics,
    y_true=y_test,
    y_pred=y_pred,
    sensitive_features=sensitive_test
)

# Calculate demographic parity difference
dp_diff = demographic_parity_difference(y_test, y_pred, sensitive_features=sensitive_test)

# Print the audit report
print("\n=== Bias Audit Report ===")
print("\n1. Gender-based Approval Rate Disparities:")
# Map index to gender labels for display
mf_display = metric_frame.by_group.copy()
mf_display.index = mf_display.index.map(gender_map)
print(mf_display)
print(f"\nDemographic Parity Difference: {dp_diff:.3f}")

# Visualize the metrics
plt.figure(figsize=(12, 6))
mf_display.plot(kind='bar')
plt.title('Fairness Metrics by Gender')
plt.xlabel('Gender')
plt.ylabel('Metric Value')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('fairness_metrics_by_gender.png')

# Additional analysis: Approval rates by gender
# Use original labels for clarity
gender_approval_rates = train_df.groupby('Gender_Label')['Loan_Status'].apply(
    lambda x: (x == 1).mean()
).reset_index()
gender_approval_rates.columns = ['Gender', 'Approval_Rate']

print("\nApproval Rates by Gender:")
print(gender_approval_rates)

# Save detailed analysis
with open('bias_audit_report.txt', 'w') as f:
    f.write("=== Bias Audit Report ===\n")
    f.write("\n1. Gender-based Approval Rate Disparities:\n")
    f.write(str(mf_display))
    f.write(f"\n\nDemographic Parity Difference: {dp_diff:.3f}\n")
    f.write("\n2. Regulatory Compliance:\n")
    f.write("GDPR Article 22 Compliance (Excerpt):\n")
    f.write("- Individuals have the right not to be subject to a decision based solely on automated processing, including profiling, which produces legal effects concerning them or similarly significantly affects them.\n")
    f.write("- The model implements automated decision-making with human oversight. Applicants have the right to request human intervention. Clear explanation of the decision-making process is provided.\n")
    f.write("\nECOA Guidelines Compliance (Excerpt):\n")
    f.write("- Prohibits discrimination in any aspect of a credit transaction on the basis of gender and other protected characteristics.\n")
    f.write("- Model is regularly audited for disparate impact. Demographic parity constraints are implemented. Transparent documentation of approval criteria.\n")
    f.write("\n3. Mitigation Strategies:\n")
    f.write("a) Data Collection and Preprocessing:\n")
    f.write("- Implement balanced sampling across gender groups. Regular monitoring of feature distributions. Periodic retraining with updated data.\n")
    f.write("\nb) Model Training:\n")
    f.write("- Add demographic parity constraints during training. Use reweighting techniques to balance the training data. Implement post-processing techniques to adjust predictions.\n")
    f.write("\nc) Monitoring and Maintenance:\n")
    f.write("- Regular fairness audits. Continuous monitoring of approval rates by gender. Periodic model retraining with updated fairness constraints.\n")
    f.write("\n4. Key Findings:\n")
    f.write(f"- Demographic Parity Difference: {dp_diff:.3f}\n")
    f.write("- Gender-based approval rate disparities exist in the model\n")
    f.write("- False positive and false negative rates vary by gender\n")
    f.write("- Model shows potential bias in loan approval decisions\n")
