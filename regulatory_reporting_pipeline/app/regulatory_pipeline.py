import json
import boto3
import pandas as pd
from datetime import datetime
import logging
from fastapi import FastAPI
import streamlit as st
import requests
from great_expectations.dataset import PandasDataset
from awsglue.context import GlueContext
from pyspark.sql import SparkSession
import xml.etree.ElementTree as ET

# Configure logging for audit trail (GDPR/CCPA compliance)
logging.basicConfig(filename='regulatory_audit.log', level=logging.INFO)

# AWS clients
kinesis_client = boto3.client('kinesis')
s3_client = boto3.client('s3')
glue_client = boto3.client('glue')
redshift_data = boto3.client('redshift-data')
sns_client = boto3.client('sns')

# Configuration
KINESIS_STREAM = 'regulatory-stream'
S3_BUCKET = 'regulatory-data-lake-bucket'
REDSHIFT_CLUSTER = 'regulatory-cluster'
REDSHIFT_DB = 'regulatory_db'
REDSHIFT_USER = 'admin'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:YOUR_ACCOUNT:regulatory-alerts'

# FastAPI for report access
app = FastAPI()

# Mock data
mock_transactions = [
    {"customer_id": "C001", "amount": 5000, "type": "investment", "date": "2025-07-01", "account_id": "A001"},
    {"customer_id": "C002", "amount": 2000, "type": "savings", "date": "2025-07-02", "account_id": "A002"}
]
mock_crm_data = [
    {"customer_id": "C001", "name": "Jane Doe", "kyc_status": "verified"},
    {"customer_id": "C002", "name": "John Smith", "kyc_status": "verified"}
]

# Ingest data to Kinesis
def ingest_to_kinesis(data, stream_name=KINESIS_STREAM):
    for record in data:
        kinesis_client.put_record(
            StreamName=stream_name,
            Data=json.dumps(record),
            PartitionKey=record['customer_id']
        )
        logging.info(f"Ingested transaction: {record['customer_id']}")
    print("Transactions sent to Kinesis")

# Lambda handler for batch ingestion to S3
def batch_ingest_lambda(event, context):
    data = event.get('data', mock_crm_data)
    s3_key = f"raw/crm/{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=json.dumps(data)
    )
    logging.info(f"Ingested batch data to S3: {s3_key}")
    return {"status": "success", "s3_key": s3_key}

# AWS Glue ETL and validation job
def run_glue_etl():
    spark = SparkSession.builder.appName("RegulatoryReporting").getOrCreate()
    glue_context = GlueContext(spark.sparkContext)
    
    # Read raw data from S3
    trans_df = glue_context.create_dynamic_frame.from_options(
        format_options={"json": {"multiline": True}},
        connection_type="s3",
        format="json",
        connection_options={"paths": [f"s3://{S3_BUCKET}/raw/transactions/"], "recurse": True}
    )
    crm_df = glue_context.create_dynamic_frame.from_options(
        format_options={"json": {"multiline": True}},
        connection_type="s3",
        format="json",
        connection_options={"paths": [f"s3://{S3_BUCKET}/raw/crm/"], "recurse": True}
    )
    
    # Transform: Join and enrich
    trans_spark_df = trans_df.toDF().groupBy('customer_id').agg({
        'amount': 'sum',
        'type': 'collect_set'
    }).withColumnRenamed('sum(amount)', 'total_spend').withColumnRenamed('collect_set(type)', 'product_types')
    crm_spark_df = crm_df.toDF().dropDuplicates(['customer_id'])
    enriched_df = crm_spark_df.join(trans_spark_df, 'customer_id', 'left')
    
    # Convert to Pandas for Great Expectations
    pandas_df = enriched_df.toPandas()
    ge_df = PandasDataset(pandas_df)
    
    # Validate data (e.g., completeness, KYC status)
    ge_df.expect_column_values_to_not_be_null('customer_id')
    ge_df.expect_column_values_to_be_in_set('kyc_status', ['verified', 'pending', 'unverified'])
    validation_results = ge_df.validate()
    if validation_results['success']:
        logging.info("Data validation passed")
    else:
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=f"Data validation failed: {json.dumps(validation_results)}"
        )
        logging.error(f"Data validation failed: {validation_results}")
        return
    
    # Write to processed zone (Parquet)
    glue_context.write_dynamic_frame.from_options(
        frame=glue_context.create_dynamic_frame.from_df(enriched_df),
        connection_type="s3",
        format="parquet",
        connection_options={"path": f"s3://{S3_BUCKET}/processed/", "partitionKeys": ["customer_id"]}
    )
    
    # Write to Redshift
    glue_context.write_dynamic_frame.from_options(
        frame=glue_context.create_dynamic_frame.from_df(enriched_df),
        connection_type="redshift",
        connection_options={
            "url": f"jdbc:redshift://{REDSHIFT_CLUSTER}.redshift.amazonaws.com:5439/{REDSHIFT_DB}",
            "dbtable": "regulatory_data",
            "user": REDSHIFT_USER,
            "password": "YOUR_PASSWORD"
        }
    )
    logging.info("ETL job completed")

# Lambda handler for report generation
def generate_report_lambda(event, context):
    # Fetch data from Redshift
    query = """
    SELECT customer_id, name, kyc_status, total_spend, product_types
    FROM regulatory_data
    """
    response = redshift_data.execute_statement(
        ClusterIdentifier=REDSHIFT_CLUSTER,
        Database=REDSHIFT_DB,
        DbUser=REDSHIFT_USER,
        Sql=query
    )
    result = redshift_data.get_statement_result(Id=response['Id'])
    data = [
        {
            'customer_id': r[0]['stringValue'],
            'name': r[1]['stringValue'],
            'kyc_status': r[2]['stringValue'],
            'total_spend': r[3]['doubleValue'],
            'product_types': r[4]['stringValue']
        } for r in result['Records']
    ]
    
    # Generate XBRL report (simplified example)
    xbrl_root = ET.Element("xbrl")
    for record in data:
        item = ET.SubElement(xbrl_root, "report")
        ET.SubElement(item, "customer_id").text = record['customer_id']
        ET.SubElement(item, "total_spend").text = str(record['total_spend'])
        ET.SubElement(item, "kyc_status").text = record['kyc_status']
    
    xbrl_str = ET.tostring(xbrl_root, encoding='unicode')
    s3_key = f"reports/sec_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.xml"
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=xbrl_str
    )
    
    # Notify stakeholders
    sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=f"Regulatory report generated: s3://{S3_BUCKET}/{s3_key}"
    )
    logging.info(f"Report generated: {s3_key}")
    return {"status": "success", "s3_key": s3_key}

# FastAPI endpoint for report access
@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=f"reports/{report_id}")
        report_content = response['Body'].read().decode('utf-8')
        return {"report_id": report_id, "content": report_content}
    except Exception as e:
        logging.error(f"Error fetching report {report_id}: {str(e)}")
        return {"error": str(e)}

# Streamlit UI for demo
def run_streamlit():
    st.title("Regulatory Reporting Automation Pipeline")
    st.write("Generate and View Regulatory Reports")
    if st.button("Generate Sample SEC Report"):
        generate_report_lambda({}, None)
        st.write("Report generation triggered")
    
    report_id = st.text_input("Enter Report ID (e.g., sec_report_20250707123456.xml)")
    if report_id:
        response = requests.get(f"http://localhost:8000/api/reports/{report_id}")
        if response.status_code == 200:
            report = response.json()
            st.write("**Report Content**")
            st.code(report['content'])
            # Simple chart
            df = pd.DataFrame(mock_transactions)
            st.bar_chart(df[['amount']].set_index(df['customer_id']))
        else:
            st.error("Report not found")
    
    if st.button("Simulate Real-Time Transaction"):
        ingest_to_kinesis([{"customer_id": "C001", "amount": 1000, "type": "investment", "date": "2025-07-07", "account_id": "A001"}])
        st.write("Transaction sent to pipeline")

# Main execution
if __name__ == "__main__":
    # Ingest mock data
    ingest_to_kinesis(mock_transactions)
    batch_ingest_lambda({'data': mock_crm_data}, None)
    # Run Glue ETL (simulated; deploy as Glue job)
    run_glue_etl()
    # Start FastAPI server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
