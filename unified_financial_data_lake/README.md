# Unified Financial Data Lake for Cross-Product Analytics

## Project Overview

This project builds a centralized financial data lake on AWS to ingest, store, transform, and analyze data from diverse financial products, enabling unified analytics, personalized recommendations, and regulatory compliance.

## Architecture

The architecture includes AWS Kinesis for real-time ingestion, Lambda for preprocessing and batch ingestion, Glue for ETL and cataloging, S3 for zoned data storage, Athena and Redshift for analytics, API Gateway and FastAPI for data access, Step Functions for orchestration, and Streamlit for demo UI.

## Folder Structure

- `infra/` - Terraform code to provision AWS infrastructure.
- `app/` - Python application code for ingestion, ETL, analytics API, and demo UI.
- `architecture/` - Architecture documentation and diagrams.

## Setup and Usage

1. Provision AWS resources using Terraform in the `infra/` folder.
2. Configure AWS credentials for boto3.
3. Run the Python app in `app/` to simulate data ingestion, ETL, and analytics.
4. Access the Streamlit UI and FastAPI endpoints for real-time analytics.

## AWS Services Used

- Amazon S3 (Raw, Processed, Curated zones)
- AWS Kinesis Data Streams & Firehose
- AWS Glue (ETL and Data Catalog)
- Amazon Athena
- Amazon Redshift
- AWS Lambda
- AWS Step Functions
- Amazon API Gateway
- AWS KMS
- AWS CloudWatch
- Amazon QuickSight (optional)
- Streamlit (local demo UI)

## Notes

- Designed for demonstration and extensible for production.
- Follow best practices for security, monitoring, and scalability.
