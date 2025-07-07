import boto3
import sagemaker
from sagemaker.sklearn.estimator import SKLearn
import os

# Initialize SageMaker session and role
sagemaker_session = sagemaker.Session()
role = os.environ.get('SAGEMAKER_ROLE_ARN')  # Set this environment variable with your SageMaker execution role ARN

# Script to train Isolation Forest model
script_path = 'train_isolation_forest.py'

# Define SKLearn estimator
sklearn_estimator = SKLearn(
    entry_point=script_path,
    role=role,
    instance_type='ml.m5.large',
    framework_version='0.23-1',
    sagemaker_session=sagemaker_session,
    base_job_name='fraud-isolation-forest'
)

# Launch training job
sklearn_estimator.fit()

# Deploy model endpoint
predictor = sklearn_estimator.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.large',
    endpoint_name='fraud-detection-endpoint'
)

print("Model training and deployment complete.")
