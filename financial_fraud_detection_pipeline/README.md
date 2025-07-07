# Real-Time Financial Fraud Detection Pipeline

## Project Overview

This project implements a scalable, real-time financial fraud detection pipeline using AWS services. It ingests transaction data, applies anomaly detection with machine learning, flags suspicious activities, and provides actionable insights for fraud prevention.

## Architecture

The architecture includes AWS Kinesis for ingestion, Lambda for preprocessing and alerting, SageMaker for anomaly detection, S3 and Redshift for storage and analytics, SNS for notifications, Step Functions for orchestration, and a Streamlit demo UI.

## Folder Structure

- `infra/` - Terraform code to provision AWS infrastructure.
- `app/` - Python application code for ingestion, processing, detection, alerting, and demo UI.
- `architecture/` - Architecture documentation and diagrams.

## Setup and Usage

1. Provision AWS resources using Terraform in the `infra/` folder.
2. Configure AWS credentials for boto3.
3. Run the Python app in `app/` to simulate transactions and demo fraud detection.
4. Access the Streamlit UI and FastAPI endpoints for real-time monitoring.

## AWS Services Used

- Kinesis Data Streams & Firehose
- Lambda
- S3
- Redshift
- Glue
- SageMaker
- Step Functions
- SNS
- CloudWatch
- KMS

## Notes

- This project is designed for demonstration and can be extended for production use.
- Follow best practices for security, monitoring, and scalability when deploying.
