import json
import boto3
import time

db_resource = boto3.resource('dynamodb', region_name="us-east-1")
db_client = boto3.client('dynamodb')
def lambda_handler(event, context):
	response = db_resource.Table('Customers').update_item(
    Key={'CustomerID': event['customer_id']},
    UpdateExpression="set deleted = :d",
    ExpressionAttributeValues={
        ':d': 1,
    },
    ReturnValues="UPDATED_NEW"
)
	
	
	