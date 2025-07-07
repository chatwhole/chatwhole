import sagemaker
from sagemaker import get_execution_role
from sagemaker.sklearn.estimator import SKLearn

# Example script to train and deploy a simple sklearn model on SageMaker

role = get_execution_role()
session = sagemaker.Session()

# Define the sklearn estimator
sklearn_estimator = SKLearn(
    entry_point='train.py',  # Your training script
    role=role,
    instance_type='ml.m5.large',
    framework_version='0.23-1',
    py_version='py3',
    sagemaker_session=session,
    output_path='s3://your-bucket/output'
)

# Launch training job
sklearn_estimator.fit({'train': 's3://your-bucket/train-data/'})

# Deploy the model
predictor = sklearn_estimator.deploy(initial_instance_count=1, instance_type='ml.m5.large')

# Use the predictor for inference
data = [[5.1, 3.5, 1.4, 0.2]]  # Example input
result = predictor.predict(data)
print("Prediction result:", result)

# Cleanup
# predictor.delete()
