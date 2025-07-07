import json
import boto3
import base64
import pandas as pd
from datetime import datetime

s3_client = boto3.client('s3')
S3_BUCKET = 'regulatory-data-lake-bucket'  # Update with your bucket name or use environment variable

def handler(event, context):
    records = event['Records']
    transactions = []
    for record in records:
        payload = record['kinesis']['data']
        decoded_payload = base64.b64decode(payload)
        transaction = json.loads(decoded_payload)
        transactions.append(transaction)

    df = pd.DataFrame(transactions)
    # Clean and normalize
    df['amount'] = df['amount'].astype(float)
    df['date'] = pd.to_datetime(df['date'])

    # Store raw data in S3
    s3_key = f"raw/transactions/{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=df.to_json(orient='records')
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Preprocessing complete', 'records_processed': len(transactions)})
    }
