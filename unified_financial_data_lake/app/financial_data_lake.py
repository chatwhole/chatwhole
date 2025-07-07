import json
import boto3
import pandas as pd
from datetime import datetime
import logging
from fastapi import FastAPI
import streamlit as st
import requests

# Configure logging for audit trail (GDPR/CCPA compliance)
logging.basicConfig(filename='data_lake_audit.log', level=logging.INFO)

# AWS clients
kinesis_client = boto3.client('kinesis')
s3_client = boto3.client('s3')
glue_client = boto3.client('glue')
redshift_data = boto3.client('redshift-data')

# Configuration
KINESIS_STREAM = 'financial-stream'
S3_BUCKET = 'financial-data-lake-bucket'
REDSHIFT_CLUSTER = 'financial-cluster'
REDSHIFT_DB = 'financial_db'
REDSHIFT_USER = 'admin'

# FastAPI for API access
app = FastAPI()

# Mock data
mock_crm_data = [
    {"customer_id": "C001", "name": "Jane Doe", "age": 30, "income": 80000},
    {"customer_id": "C002", "name": "John Smith", "age": 45, "income": 120000}
]
mock_transactions = [
    {"customer_id": "C001", "amount": 5000, "type": "investment", "date": "2025-07-01"},
    {"customer_id": "C002", "amount": 2000, "type": "savings", "date": "2025-07-02"}
]

# Ingest data to Kinesis
def ingest_to_kinesis(data, stream_name=KINESIS_STREAM):
    for record in data:
        kinesis_client.put_record(
            StreamName=stream_name,
            Data=json.dumps(record),
            PartitionKey=record['customer_id']
        )
        logging.info(f"Ingested record: {record['customer_id']}")
    print("Data sent to Kinesis")

# Lambda handler for batch ingestion to S3
def batch_ingest_lambda(event, context):
    data = event.get('data', mock_crm_data)  # Replace with actual source
    s3_key = f"raw/crm/{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=json.dumps(data)
    )
    logging.info(f"Ingested batch data to S3: {s3_key}")
    return {"status": "success", "s3_key": s3_key}

# FastAPI endpoint for analytics
@app.get("/api/customer/{customer_id}")
async def get_customer_analytics(customer_id: str):
    query = f"""
    SELECT customer_id, name, age, income, total_spend, product_types
    FROM enriched_data
    WHERE customer_id = '{customer_id}'
    """
    response = redshift_data.execute_statement(
        ClusterIdentifier=REDSHIFT_CLUSTER,
        Database=REDSHIFT_DB,
        DbUser=REDSHIFT_USER,
        Sql=query
    )
    result = redshift_data.get_statement_result(Id=response['Id'])
    if result['Records']:
        record = result['Records'][0]
        analytics = {
            'customer_id': record[0]['stringValue'],
            'name': record[1]['stringValue'],
            'age': record[2]['longValue'],
            'income': record[3]['doubleValue'],
            'total_spend': record[4]['doubleValue'],
            'product_types': record[5]['stringValue'],
            'recommendation': recommend_service(record[3]['doubleValue'], record[4]['doubleValue'])
        }
        return analytics
    return {"error": "Customer not found"}

# Recommendation engine
def recommend_service(income, total_spend):
    if income > 100000 and total_spend > 10000:
        return "Premium Investment Portfolio (8% expected return)"
    elif income > 50000:
        return "Balanced Investment Fund (5% expected return)"
    else:
        return "High-Yield Savings Account (2% interest)"

# Streamlit UI for demo
def run_streamlit():
    st.title("Unified Financial Data Lake")
    st.write("Cross-Product Analytics Demo")
    customer_id = st.text_input("Enter Customer ID (e.g., C001)")
    if customer_id:
        response = requests.get(f"http://localhost:8000/api/customer/{customer_id}")
        if response.status_code == 200:
            analytics = response.json()
            st.write(f"**Name**: {analytics['name']}")
            st.write(f"**Age**: {analytics['age']}")
            st.write(f"**Income**: ${analytics['income']}")
            st.write(f"**Total Spend**: ${analytics['total_spend']}")
            st.write(f"**Products Used**: {analytics['product_types']}")
            st.write(f"**Recommendation**: {analytics['recommendation']}")
            # Simple chart
            st.bar_chart(pd.DataFrame({'total_spend': [analytics['total_spend']]}, index=[analytics['name']]))
        else:
            st.error("Customer not found")
    if st.button("Simulate Real-Time Transaction"):
        ingest_to_kinesis([{"customer_id": "C001", "amount": 1000, "type": "investment", "date": "2025-07-07"}])
        st.write("Transaction sent to pipeline")

# Main execution
if __name__ == "__main__":
    # Ingest mock data
    ingest_to_kinesis(mock_transactions)
    batch_ingest_lambda({'data': mock_crm_data}, None)
    # Start FastAPI server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
