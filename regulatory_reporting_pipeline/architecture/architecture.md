# Architecture of Regulatory Reporting Automation Pipeline

```
[Data Sources: Transactions, CRM, APIs]
         ↓
[AWS Kinesis Data Streams] → [AWS Lambda (Preprocessing)]
         ↓                           ↓
[AWS Kinesis Firehose]    [AWS Glue (ETL & Validation)]
         ↓                           ↓
[Amazon S3 (Data Lake: Raw Zone)] → [S3 (Processed Zone)]
         ↓                           ↓
[AWS Glue (Catalog & Great Expectations)] ← [S3 (Curated Zone)]
         ↓                           ↓
[Amazon Redshift (Analytics & Reporting)] ← [AWS Step Functions (Orchestration)]
         ↓                           ↓
[Amazon Athena (Ad-Hoc Queries)]    [AWS Lambda (Report Generation)]
         ↓                           ↓
[Amazon QuickSight (Dashboards)]    [Amazon SNS (Notifications)]
         ↓                           ↓
[Streamlit (Demo UI)]              [AWS KMS (Encryption)]
[AWS CloudWatch (Monitoring & Audit)]
```

## Components

- **Data Sources**: Transaction databases, CRM systems, and APIs.
- **Kinesis Data Streams**: Real-time ingestion of streaming data.
- **Lambda (Preprocessing)**: Cleans and normalizes incoming data.
- **Kinesis Firehose**: Buffers and delivers raw data to S3.
- **S3 Data Lake**: Zoned storage for raw, processed, curated data, and reports.
- **Glue**: ETL jobs, data catalog, and data validation with Great Expectations.
- **Redshift**: Data warehouse for analytics and report generation.
- **Step Functions**: Orchestrates ETL, validation, and report generation workflows.
- **Lambda (Report Generation)**: Generates regulatory reports (PDF, XBRL).
- **SNS**: Sends notifications on report status and validation results.
- **Athena**: Ad-hoc SQL queries on data lake.
- **QuickSight**: Compliance dashboards.
- **Streamlit UI**: Demo interface for report generation and compliance metrics.
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
