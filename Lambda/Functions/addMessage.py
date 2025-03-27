import json
import boto3
import time
import uuid
from boto3.dynamodb.conditions import Key, Attr

db_resource = boto3.resource('dynamodb', region_name="us-east-1")
db_client = boto3.client('dynamodb')
def lambda_handler(event, context):
    table = db_resource.Table('Messages')
    response = table.scan(
	    FilterExpression = (Attr('ReceiverID').eq(event['receiverID'])| Attr('SenderID').eq(event['receiverID']))&(Attr('ReceiverID').eq(event['senderID'])| Attr('SenderID').eq(event['senderID']))
	    
    )
    message_index=len(response['Items'])+1
    random_id=str(uuid.uuid4().fields[-1])[:5]
    
    
    result = table.put_item(
        Item={
            "MessageID": random_id,
            "Time":event['time'],
            "Body":event['body'],
            "ReceiverID": event['receiverID'],
            "SenderID": event['senderID'],
            "Replied":"0",
            "Index":message_index
        }
    )
    return random_id
        	
