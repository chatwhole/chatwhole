import json
import boto3
import logging

sns_client = boto3.client('sns')
sagemaker_runtime = boto3.client('sagemaker-runtime')
redshift_data = boto3.client('redshift-data')

SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:YOUR_ACCOUNT:fraud-alerts'  # Update accordingly
SAGEMAKER_ENDPOINT = 'fraud-detection-endpoint'  # Update accordingly
REDSHIFT_CLUSTER = 'fraud-detection-cluster'
REDSHIFT_DB = 'fraud_db'
REDSHIFT_USER = 'admin'

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    transactions = event.get('transactions', [])
    for transaction in transactions:
        amount = transaction.get('amount')
        payload = json.dumps({'amount': amount})
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=SAGEMAKER_ENDPOINT,
            ContentType='application/json',
            Body=payload
        )
        result = json.loads(response['Body'].read().decode())
        prediction = result.get('prediction')
        if prediction == -1:
            transaction['fraud_flag'] = True
            message = f"Fraud detected: {json.dumps(transaction)}"
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=message
            )
            logger.info(f"Fraud detected for transaction: {transaction.get('customer_id')}")
        else:
            transaction['fraud_flag'] = False

        # Store in Redshift
        store_in_redshift(transaction)

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Fraud detection complete', 'transactions_processed': len(transactions)})
    }

def store_in_redshift(transaction):
    query = f"""
    INSERT INTO transactions (customer_id, amount, timestamp, merchant, fraud_flag)
    VALUES ('{transaction.get('customer_id')}', {transaction.get('amount')}, '{transaction.get('timestamp')}',
            '{transaction.get('merchant')}', {str(transaction.get('fraud_flag')).lower()})
    """
    redshift_data.execute_statement(
        ClusterIdentifier=REDSHIFT_CLUSTER,
        Database=REDSHIFT_DB,
        DbUser=REDSHIFT_USER,
        Sql=query
    )
    logger.info(f"Stored transaction in Redshift: {transaction.get('customer_id')}")
