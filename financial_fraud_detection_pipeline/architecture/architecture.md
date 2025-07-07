# Architecture of Real-Time Financial Fraud Detection Pipeline

```
[Transaction Sources (CRM, Payment Systems)]
         ↓
[AWS Kinesis Data Streams] → [AWS Lambda (Preprocessing)]
         ↓                           ↓
[AWS Kinesis Firehose]    [Amazon SageMaker (Anomaly Detection)]
         ↓                           ↓
[Amazon S3 (Raw Data)]    [AWS Lambda (Fraud Flagging)]
         ↓                           ↓
[Amazon Redshift (Analytics)] ← [AWS SNS (Alerts)]
         ↓                           ↓
[AWS Glue (ETL)]            [Amazon QuickSight (Dashboards)]
         ↓
[AWS Step Functions (Orchestration)]
[Streamlit (Demo UI)]
```

## Components

- **Transaction Sources**: CRM systems, payment gateways, and other financial transaction sources.
- **Kinesis Data Streams**: Real-time ingestion of transaction data.
- **Lambda (Preprocessing)**: Cleans and normalizes incoming data.
- **Kinesis Firehose**: Buffers and delivers raw data to S3.
- **S3**: Stores raw transaction data.
- **SageMaker**: Hosts anomaly detection ML model for fraud detection.
- **Lambda (Fraud Flagging)**: Calls SageMaker endpoint, flags suspicious transactions, and triggers alerts.
- **SNS**: Sends notifications to fraud teams.
- **Redshift**: Stores processed data for analytics.
- **Glue**: ETL jobs to transform data for Redshift.
- **QuickSight**: Visualizes fraud trends and analytics.
- **Step Functions**: Orchestrates batch jobs like model retraining.
- **Streamlit UI**: Provides a demo interface for real-time fraud alerts.

## Security & Compliance

- Data encryption using AWS KMS.
- Audit logging with CloudWatch.
- IAM roles with least privilege access.

## Scalability

- Kinesis shards for high throughput.
- Serverless Lambda functions.
- Scalable Redshift cluster.

## Monitoring

- CloudWatch dashboards and alarms for pipeline health.
