# Regulatory Reporting Automation Pipeline

## Project Overview

This project builds an enterprise-grade pipeline on AWS to automate the ingestion, transformation, validation, and generation of regulatory reports for financial institutions, ensuring compliance with regulations like SEC, AML, KYC, GDPR, and CCPA, while integrating with your finance AI agent for enhanced analytics and reporting.

## Architecture

The architecture includes AWS Kinesis for real-time ingestion, Lambda for preprocessing and batch ingestion, Glue for ETL and validation with Great Expectations, S3 for zoned data storage, Redshift for analytics and reporting, Step Functions for orchestration, SNS for notifications, Athena for ad-hoc queries, QuickSight for dashboards, and Streamlit for demo UI.

## Folder Structure

- `infra/` - Terraform code to provision AWS infrastructure.
- `app/` - Python application code for ingestion, ETL, validation, report generation, API, and demo UI.
- `architecture/` - Architecture documentation and diagrams.

## Setup and Usage

1. Provision AWS resources using Terraform in the `infra/` folder.
2. Configure AWS credentials for boto3.
3. Run the Python app in `app/` to simulate data ingestion, ETL, validation, and report generation.
4. Access the Streamlit UI and FastAPI endpoints for real-time report viewing.

## AWS Services Used

- Amazon S3 (Raw, Processed, Curated, Reports zones)
- AWS Kinesis Data Streams & Firehose
- AWS Glue (ETL, Data Catalog, Great Expectations validation)
- Amazon Redshift
- AWS Lambda
- AWS Step Functions
- Amazon Athena
- Amazon SNS
- Amazon QuickSight
- AWS KMS
- AWS CloudWatch
- Streamlit (local demo UI)

## Notes

- Designed for demonstration and extensible for production.
- Follow best practices for security, monitoring, and scalability.
