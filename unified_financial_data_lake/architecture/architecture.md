# Architecture of Unified Financial Data Lake for Cross-Product Analytics

```
[Data Sources: CRM, Transactions, Web Logs, APIs]
         ↓
[AWS Kinesis Data Streams] → [AWS Lambda (Preprocessing)]
         ↓                           ↓
[AWS Kinesis Firehose]    [AWS Glue (ETL)]
         ↓                           ↓
[Amazon S3 (Data Lake: Raw Zone)] → [S3 (Processed Zone)]
         ↓                           ↓
[AWS Glue (Catalog)]        [S3 (Curated Zone)]
         ↓                           ↓
[Amazon Athena (Ad-Hoc Queries)]  [Amazon Redshift (Analytics)]
         ↓                           ↓
[AWS Step Functions (Orchestration)] ← [Amazon API Gateway (REST API)]
         ↓                           ↓
[Amazon QuickSight (Dashboards)]    [Streamlit (Demo UI)]
[AWS CloudWatch (Monitoring)]      [AWS KMS (Encryption)]
```

## Components

- **Data Sources**: CRM systems, transaction databases, web logs, and APIs.
- **Kinesis Data Streams**: Real-time ingestion of streaming data.
- **Lambda (Preprocessing)**: Cleans and normalizes incoming data.
- **Kinesis Firehose**: Buffers and delivers raw data to S3.
- **S3 Data Lake**: Zoned storage for raw, processed, and curated data.
- **Glue**: ETL jobs and data catalog management.
- **Athena**: Ad-hoc SQL queries on data lake.
- **Redshift**: Data warehouse for complex analytics.
- **Step Functions**: Orchestrates ETL and analytics workflows.
- **API Gateway**: Exposes curated data via REST API.
- **QuickSight**: Enterprise dashboards.
- **Streamlit UI**: Demo interface for analytics and recommendations.
- **CloudWatch**: Monitoring and audit logging.
- **KMS**: Data encryption for compliance.

## Security & Compliance

- Data encryption using AWS KMS.
- Audit logging with CloudWatch.
- IAM roles with least privilege access.

## Scalability

- Zoned S3 storage for efficient data management.
- Serverless components for cost-effective scaling.
- Redshift and Athena for scalable analytics.

## Monitoring

- CloudWatch dashboards and alarms for pipeline health.
