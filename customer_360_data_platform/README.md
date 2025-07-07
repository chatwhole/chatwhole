# Customer 360 Data Platform for Personalized Financial Services

## Overview
This project demonstrates a high-impact Customer 360 Data Platform that integrates customer data, enables real-time personalization, and ensures compliance with data privacy laws (GDPR, CCPA). It showcases a scalable, cloud-native architecture using AWS, Kafka, Snowflake, FastAPI, and Streamlit.

## Features
- Data ingestion from mock CRM and transaction sources to AWS S3.
- Data integration with deduplication and enrichment using pandas.
- Real-time updates via Kafka streaming.
- Storage and analytics in Snowflake.
- Rule-based personalization engine with investment recommendations.
- Compliance with data anonymization and audit logging.
- Interactive Streamlit UI for customer profiles and recommendations.
- AI Analytics integration with AWS SageMaker, Comprehend, and Forecast.
- Modular Terraform infrastructure for scalable cloud deployment.

## Prerequisites
- AWS account with access to Lambda, S3, Redshift, SageMaker, Comprehend, and Forecast.
- Kafka setup (local or Confluent Cloud).
- Snowflake account with database and schema created.
- Python 3.8+ environment.

## Installation
1. Clone the repository.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure AWS credentials for boto3.
4. Update Snowflake connection details in `customer_360_pipeline.py`.
5. Set up Kafka and update bootstrap server and topic if needed.
6. Create an S3 bucket named `customer-360-raw`.

## Running the Project
1. Run the main pipeline and API server:
   ```
   python customer_360_pipeline.py
   ```
2. In a separate terminal, run the Streamlit UI:
   ```
   streamlit run customer_360_pipeline.py
   ```
3. Access the API at `http://localhost:8000/api/customer/C001`.
4. Access the UI at `http://localhost:8501`.

## Demo Tips
- Use realistic mock data for better demonstration.
- Simulate real-time events via Kafka to show live updates.
- Highlight compliance by showing the audit log file.
- Showcase personalized recommendations based on customer profiles.

## Future Enhancements
- Integrate ML models for advanced recommendations.
- Add OAuth2 authentication for API security.
- Implement multi-channel data ingestion.
- Add monitoring with Prometheus and Grafana.

## Contact
For questions or support, please contact the project maintainer.
