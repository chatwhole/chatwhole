import json
import boto3
import logging
import xml.etree.ElementTree as ET
from datetime import datetime

s3_client = boto3.client('s3')
redshift_data = boto3.client('redshift-data')
sns_client = boto3.client('sns')

S3_BUCKET = 'regulatory-data-lake-bucket'  # Update accordingly
REDSHIFT_CLUSTER = 'regulatory-cluster'
REDSHIFT_DB = 'regulatory_db'
REDSHIFT_USER = 'admin'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:YOUR_ACCOUNT:regulatory-alerts'  # Update accordingly

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    # Fetch data from Redshift
    query = """
    SELECT customer_id, name, kyc_status, total_spend, product_types
    FROM regulatory_data
    """
    response = redshift_data.execute_statement(
        ClusterIdentifier=REDSHIFT_CLUSTER,
        Database=REDSHIFT_DB,
        DbUser=REDSHIFT_USER,
        Sql=query
    )
    result = redshift_data.get_statement_result(Id=response['Id'])
    data = [
        {
            'customer_id': r[0]['stringValue'],
            'name': r[1]['stringValue'],
            'kyc_status': r[2]['stringValue'],
            'total_spend': r[3]['doubleValue'],
            'product_types': r[4]['stringValue']
        } for r in result['Records']
    ]
    
    # Generate XBRL report (simplified example)
    xbrl_root = ET.Element("xbrl")
    for record in data:
        item = ET.SubElement(xbrl_root, "report")
        ET.SubElement(item, "customer_id").text = record['customer_id']
        ET.SubElement(item, "total_spend").text = str(record['total_spend'])
        ET.SubElement(item, "kyc_status").text = record['kyc_status']
    
    xbrl_str = ET.tostring(xbrl_root, encoding='unicode')
    s3_key = f"reports/sec_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.xml"
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=xbrl_str
    )
    
    # Notify stakeholders
    sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=f"Regulatory report generated: s3://{S3_BUCKET}/{s3_key}"
    )
    logger.info(f"Report generated: {s3_key}")
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Report generated', 's3_key': s3_key})
    }
