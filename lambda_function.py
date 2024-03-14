import json
import boto3
import pandas as pd

# Initialize S3 and SNS clients
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')

def lambda_handler(event, context):
    # print(event)
    # Extracting S3 bucket and key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Read JSON file into pandas DataFrame
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    df = pd.read_json(obj['Body'])
    
    # Filter records where status is "delivered"
    filtered_df = df[df['status'] == 'delivered']
    
    # Convert filtered DataFrame to JSON string
    filtered_json = filtered_df.to_json(orient='records')
    
    # Write filtered DataFrame to new JSON file in S3
    target_bucket = 'doordash-target-zn'
    target_key = key.split('/')[-1].split('.')[0] + '_filtered.json'
    s3_client.put_object(Bucket=target_bucket, Key=target_key, Body=filtered_json)
    
    # Publish success message to SNS topic
    sns_topic_arn = 'arn:aws:sns:us-east-1:123456789012:doordash-topic'
    sns_client.publish(TopicArn=sns_topic_arn, Message='Successfully processed file {}'.format(key))
    
    return {
        'statusCode': 200,
        'body': json.dumps('File processed successfully!')
    }


