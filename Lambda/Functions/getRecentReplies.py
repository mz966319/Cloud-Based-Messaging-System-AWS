import json
import boto3
import time
import uuid
from boto3.dynamodb.conditions import Key, Attr

db_resource = boto3.resource('dynamodb', region_name="us-east-1")
db_client = boto3.client('dynamodb')
def lambda_handler(event, context):
    
    
    response =  db_resource.Table('NewReplies').query(
        KeyConditionExpression=Key('UserID').eq(event['userid']) 

    )
    print(response['Items'])
    # { "UserID": "baiumy", "Message": "Body:  try me out pls", "Index": 1, "CustomerID": "17370", "Reply": "Works well with me" }
    final_result=[]
    for item in response['Items']:
        customer_response=response = db_client.get_item(
            TableName='Customers',
            Key={
                'CustomerID': {'S': item['CustomerID']}
            }
        )
        final_result.append({"id":item['CustomerID'],"userid":item['UserID'],"name":customer_response['Item']['name']['S'],"message":item['Message'],"reply":item['Reply'],"index":item['Index']})
        
    

    
    return final_result

    
    

