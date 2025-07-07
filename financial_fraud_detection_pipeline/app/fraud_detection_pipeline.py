import json
import boto3
import pandas as pd
from datetime import datetime
import numpy as np
from sklearn.ensemble import IsolationForest
import logging
from fastapi import FastAPI
import streamlit as st
import requests
import uvicorn

# Configure logging for audit trail (GDPR/CCPA compliance)
logging.basicConfig(filename='fraud_audit.log', level=logging.INFO)

# AWS clients
kinesis_client = boto3.client('kinesis')
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
sagemaker_runtime = boto3.client('sagemaker-runtime')
redshift_data = boto3.client('redshift-data')

# Configuration
KINESIS_STREAM = 'transaction-stream'
S3_BUCKET_RAW = 'fraud-detection-raw-bucket'
S3_BUCKET_PROCESSED = 'fraud-detection-processed-bucket'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:YOUR_ACCOUNT:fraud-alerts'
SAGEMAKER_ENDPOINT = 'fraud-detection-endpoint'
REDSHIFT_CLUSTER = 'fraud-detection-cluster'
REDSHIFT_DB = 'fraud_db'
REDSHIFT_USER = 'admin'

# FastAPI for demo API
app = FastAPI()

# Mock transaction data
mock_transactions = [
    {"customer_id": "C001", "amount": 5000, "timestamp": "2025-07-07T17:00:00Z", "merchant": "Retail"},
    {"customer_id": "C002", "amount": 15000, "timestamp": "2025-07-07T17:01:00Z", "merchant": "Online"},  # Suspicious
    {"customer_id": "C001", "amount": 200, "timestamp": "2025-07-07T17:02:00Z", "merchant": "Grocery"}
]

# Ingest transactions to Kinesis
def ingest_to_kinesis(transactions):
    for transaction in transactions:
        kinesis_client.put_record(
            StreamName=KINESIS_STREAM,
            Data=json.dumps(transaction),
            PartitionKey=transaction['customer_id']
        )
        logging.info(f"Ingested transaction: {transaction['customer_id']}")
    print("Transactions sent to Kinesis")

# Lambda handler for preprocessing (simulate locally)
def preprocess_lambda(event):
    transactions = [json.loads(record['kinesis']['data']) for record in event['Records']]
    df = pd.DataFrame(transactions)
    # Clean and normalize
    df['amount'] = df['amount'].astype(float)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # Store raw data in S3
    s3_key = f"transactions/{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    s3_client.put_object(
        Bucket=S3_BUCKET_RAW,
        Key=s3_key,
        Body=df.to_json(orient='records')
    )
    return df.to_dict(orient='records')

# Train and deploy SageMaker model (run in SageMaker notebook)
def train_sagemaker_model():
    # Sample training data
    X_train = np.array([[500], [200], [15000], [1000]])  # Amounts
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X_train)
    # Save model to S3 (simplified; use SageMaker for production)
    import joblib
    joblib.dump(model, '/tmp/model.joblib')
    s3_client.upload_file('/tmp/model.joblib', S3_BUCKET_PROCESSED, 'models/isolation_forest.joblib')
    print("Model trained and saved")

# Lambda handler for anomaly detection (simulate locally)
def detect_fraud_lambda(transactions):
    for transaction in transactions:
        # Call SageMaker endpoint
        payload = json.dumps({'amount': transaction['amount']})
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=SAGEMAKER_ENDPOINT,
            ContentType='application/json',
            Body=payload
        )
        prediction = json.loads(response['Body'].read().decode())['prediction']
        if prediction == -1:  # Anomaly detected
            transaction['fraud_flag'] = True
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=f"Fraud detected: {json.dumps(transaction)}"
            )
            logging.info(f"Fraud detected for transaction: {transaction['customer_id']}")
        else:
            transaction['fraud_flag'] = False
        # Store in Redshift
        store_in_redshift(transaction)
    return transactions

# Store in Redshift
def store_in_redshift(transaction):
    query = f"""
    INSERT INTO transactions (customer_id, amount, timestamp, merchant, fraud_flag)
    VALUES ('{transaction['customer_id']}', {transaction['amount']}, '{transaction['timestamp']}',
            '{transaction['merchant']}', {transaction['fraud_flag']})
    """
    redshift_data.execute_statement(
        ClusterIdentifier=REDSHIFT_CLUSTER,
        Database=REDSHIFT_DB,
        DbUser=REDSHIFT_USER,
        Sql=query
    )
    logging.info(f"Stored transaction in Redshift: {transaction['customer_id']}")

# FastAPI endpoint for demo
@app.get("/api/fraud/transactions")
async def get_fraud_transactions():
    query = """
    SELECT customer_id, amount, timestamp, merchant, fraud_flag
    FROM transactions
    WHERE fraud_flag = true
    """
    response = redshift_data.execute_statement(
        ClusterIdentifier=REDSHIFT_CLUSTER,
        Database=REDSHIFT_DB,
        DbUser=REDSHIFT_USER,
        Sql=query
    )
    # Wait for query completion (simplified)
    result = redshift_data.get_statement_result(Id=response['Id'])
    transactions = [
        {
            'customer_id': record[0]['stringValue'],
            'amount': record[1]['doubleValue'],
            'timestamp': record[2]['stringValue'],
            'merchant': record[3]['stringValue'],
            'fraud_flag': record[4]['booleanValue']
        } for record in result['Records']
    ]
    return transactions

# Streamlit UI for demo
def run_streamlit():
    st.title("Real-Time Financial Fraud Detection")
    st.write("Live Fraud Alerts")
    if st.button("Simulate Transactions"):
        ingest_to_kinesis(mock_transactions)
        st.write("Transactions sent to pipeline")
    # Fetch and display flagged transactions
    response = requests.get("http://localhost:8000/api/fraud/transactions")
    if response.status_code == 200:
        fraud_transactions = response.json()
        st.write("**Flagged Transactions**")
        df = pd.DataFrame(fraud_transactions)
        st.dataframe(df)
        # Simple chart
        if not df.empty:
            st.line_chart(df[['amount']].set_index(df['timestamp']))
    else:
        st.error("Error fetching fraud transactions")

# Main execution (for demo)
if __name__ == "__main__":
    # Simulate model training (run in SageMaker for production)
    train_sagemaker_model()
    # Ingest mock data
    ingest_to_kinesis(mock_transactions)
    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
