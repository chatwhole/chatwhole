import json
import boto3
import pandas as pd
from confluent_kafka import Consumer, Producer
from fastapi import FastAPI
from snowflake.connector import connect
import streamlit as st
from hashlib import sha256
import logging
from datetime import datetime
import requests
import threading
import uvicorn
import matplotlib.pyplot as plt
import numpy as np

# Configure logging for audit trail (GDPR/CCPA compliance)
logging.basicConfig(filename='audit.log', level=logging.INFO)

# AWS clients
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')

# Snowflake connection
snowflake_conn = connect(
    user='YOUR_USER',
    password='YOUR_PASSWORD',
    account='YOUR_ACCOUNT',
    warehouse='YOUR_WAREHOUSE',
    database='CUSTOMER_360',
    schema='PUBLIC'
)

# Kafka configuration
KAFKA_BOOTSTRAP = 'localhost:9092'
KAFKA_TOPIC = 'customer_events'

# FastAPI for exposing customer profiles
app = FastAPI()

# Mock CRM and transaction data
mock_crm_data = [
    {"customer_id": "C001", "name": "Jane Doe", "age": 30, "income": 80000},
    {"customer_id": "C002", "name": "John Smith", "age": 45, "income": 120000}
]
mock_transactions = [
    {"customer_id": "C001", "amount": 5000, "type": "investment", "date": "2025-07-01"},
    {"customer_id": "C002", "amount": 2000, "type": "savings", "date": "2025-07-02"}
]

# Ingest data to S3
def ingest_to_s3(data, bucket='customer-360-raw', key_prefix='raw/'):
    key = f"{key_prefix}{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    s3_client.put_object(Bucket=bucket, Key=key, Body=json.dumps(data))
    logging.info(f"Ingested data to S3: {key}")
    return key

# Deduplicate and enrich customer data
def integrate_customer_data(crm_data, transactions):
    crm_df = pd.DataFrame(crm_data)
    trans_df = pd.DataFrame(transactions)
    # Deduplicate by customer_id
    crm_df = crm_df.drop_duplicates(subset=['customer_id'])
    # Enrich with transaction summary
    trans_summary = trans_df.groupby('customer_id').agg({
        'amount': ['sum', 'count'],
        'type': lambda x: list(set(x))
    }).reset_index()
    trans_summary.columns = ['customer_id', 'total_spend', 'trans_count', 'trans_types']
    # Merge data
    customer_profile = crm_df.merge(trans_summary, on='customer_id', how='left')
    # Calculate risk score (simple rule-based)
    customer_profile['risk_score'] = customer_profile['income'].apply(
        lambda x: 'high' if x > 100000 else 'medium' if x > 50000 else 'low'
    )
    return customer_profile

# Store profiles in Snowflake
def store_in_snowflake(df):
    cursor = snowflake_conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS customer_profiles (customer_id STRING, name STRING, age INT, income FLOAT, total_spend FLOAT, trans_count INT, trans_types STRING, risk_score STRING)")
    for _, row in df.iterrows():
        cursor.execute(
            "INSERT INTO customer_profiles VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (row['customer_id'], row['name'], row['age'], row['income'], row['total_spend'], row['trans_count'], str(row['trans_types']), row['risk_score'])
        )
    snowflake_conn.commit()
    logging.info("Stored customer profiles in Snowflake")

# Kafka producer for real-time events
def produce_event(event):
    producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP})
    producer.produce(KAFKA_TOPIC, json.dumps(event).encode('utf-8'))
    producer.flush()
    logging.info(f"Produced event: {event}")

# Kafka consumer for real-time updates
def consume_events():
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP,
        'group.id': 'customer_360_group',
        'auto.offset.reset': 'latest'
    })
    consumer.subscribe([KAFKA_TOPIC])
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        event = json.loads(msg.value().decode('utf-8'))
        update_customer_profile(event)

# Update customer profile in real time
def update_customer_profile(event):
    cursor = snowflake_conn.cursor()
    customer_id = event['customer_id']
    amount = event['amount']
    cursor.execute(
        f"UPDATE customer_profiles SET total_spend = total_spend + {amount}, trans_count = trans_count + 1 WHERE customer_id = '{customer_id}'"
    )
    snowflake_conn.commit()
    logging.info(f"Updated profile for customer {customer_id}")

# Recommendation engine
def recommend_service(customer):
    if customer['risk_score'] == 'high':
        return "Invest in our aggressive growth portfolio (8% expected return)."
    elif customer['risk_score'] == 'medium':
        return "Consider our balanced investment fund (5% expected return)."
    else:
        return "Try our high-yield savings account (2% interest)."

# FastAPI endpoint to get customer profile
@app.get("/api/customer/{customer_id}")
async def get_customer_profile(customer_id: str):
    cursor = snowflake_conn.cursor()
    cursor.execute(f"SELECT * FROM customer_profiles WHERE customer_id = '{customer_id}'")
    result = cursor.fetchone()
    if result:
        profile = {
            'customer_id': result[0], 'name': result[1], 'age': result[2], 'income': result[3],
            'total_spend': result[4], 'trans_count': result[5], 'trans_types': result[6], 'risk_score': result[7]
        }
        profile['recommendation'] = recommend_service(profile)
        return profile
    return {"error": "Customer not found"}

# Streamlit UI for demo with AI analytics enhancements
def run_streamlit():
    st.title("Customer 360 Data Platform with AI Analytics")
    customer_id = st.text_input("Enter Customer ID (e.g., C001)")
    if customer_id:
        response = requests.get(f"http://localhost:8000/api/customer/{customer_id}")
        if response.status_code == 200:
            profile = response.json()
            st.write(f"**Name**: {profile['name']}")
            st.write(f"**Age**: {profile['age']}")
            st.write(f"**Income**: ${profile['income']}")
            st.write(f"**Total Spend**: ${profile['total_spend']}")
            st.write(f"**Transaction Count**: {profile['trans_count']}")
            st.write(f"**Risk Score**: {profile['risk_score']}")
            st.write(f"**Recommendation**: {profile['recommendation']}")

            # AI Analytics: Spending trend chart (mock data)
            days = np.arange(1, 31)
            spending = np.random.normal(loc=profile['total_spend']/30, scale=50, size=30)
            st.line_chart(pd.DataFrame({'Daily Spend': spending}, index=days))

            # AI Analytics: Risk profile pie chart
            risk_labels = ['High Risk', 'Medium Risk', 'Low Risk']
            risk_sizes = [0, 0, 0]
            if profile['risk_score'] == 'high':
                risk_sizes[0] = 1
            elif profile['risk_score'] == 'medium':
                risk_sizes[1] = 1
            else:
                risk_sizes[2] = 1
            fig, ax = plt.subplots()
            ax.pie(risk_sizes, labels=risk_labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)

        else:
            st.error("Customer not found")

# Main execution
if __name__ == "__main__":
    # Ingest mock data
    ingest_to_s3(mock_crm_data, key_prefix='crm/')
    ingest_to_s3(mock_transactions, key_prefix='transactions/')
    # Integrate data
    customer_profiles = integrate_customer_data(mock_crm_data, mock_transactions)
    # Store in Snowflake
    store_in_snowflake(customer_profiles)
    # Simulate real-time event
    produce_event({"customer_id": "C001", "amount": 1000, "type": "investment", "date": "2025-07-07"})
    # Start Kafka consumer in a separate thread
    threading.Thread(target=consume_events, daemon=True).start()
    # Run FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
