import json
import boto3
import time
import uuid
from boto3.dynamodb.conditions import Key, Attr

db_resource = boto3.resource('dynamodb', region_name="us-east-1")
db_client = boto3.client('dynamodb')
def lambda_handler(event, context):
    random_id=str(uuid.uuid4().fields[-1])[:5]
    time_stamp=time.strftime('%Y-%m-%d %H:%M:%S')

    
    message_response = db_client.get_item(TableName='Messages', Key={'MessageID': {'S':event['message_id']}})
    response =  db_resource.Table('Messages').scan(
	    FilterExpression = (Attr('ReceiverID').eq(message_response['Item']['ReceiverID']['S'])| Attr('SenderID').eq(message_response['Item']['ReceiverID']['S']))&
	    (Attr('ReceiverID').eq(message_response['Item']['SenderID']['S'])| Attr('SenderID').eq(message_response['Item']['SenderID']['S']))
	    
    )
    message_index=len(response['Items'])+1
    
    
    print(message_response)
    #add the reply to database
    result = db_resource.Table('Messages').put_item(
        Item={
            "MessageID": random_id,
            "Time":time_stamp,
            "Body":event['reply_body'],
            "ReceiverID": message_response['Item']['SenderID']['S'],
            "SenderID":  message_response['Item']['ReceiverID']['S'],
            "Replied":"0",
            "Index":message_index
        }
    )
    
    reply_response =  db_resource.Table('NewReplies').scan(
	    FilterExpression = Attr('UserID').eq(message_response['Item']['SenderID']['S'])
	    
    )
    new_reply_index=len(reply_response['Items'])+1
    #add the reply to notifications table
    result = db_resource.Table('NewReplies').put_item(
        Item={
            "UserID":  message_response['Item']['SenderID']['S'],
            "CustomerID":message_response['Item']['ReceiverID']['S'],
            "Reply":event['reply_body'],
            "Message": message_response['Item']['Body']['S'],
            "Index":new_reply_index
        }
    )
    
    #update sent message to have reply set to true
    db_client.update_item(TableName="Messages",
               Key={'MessageID':{'S':event['message_id']}},
               UpdateExpression="set Replied = :element",
               ExpressionAttributeValues={":element":{"S":"1"}}
           )
    
    
    body='<!DOCTYPE html> <html lang="en"> <head> <meta charset="UTF-8"> <meta http-equiv="X-UA-Compatible" content="IE=edge"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>Confirm</title> <style> body { font-family: Arial, Helvetica, sans-serif; display: flex; align-items: center; justify-content: center; background-color: grey; } p{ font-size: 3vw; } #main{ margin-top: 25vh; background-color: white; border-radius: 10px; width: 35vw; height: 50vh; display: flex; flex-direction: column; align-items: center; justify-content: center; } </style> </head> <body> <div id="main"> <p>Thank you!</p> </div> </body> </html>'
    return body
    return {
        'statusCode': 200,
        'headers': {"Content-Type":"text/html"},
        'body':body
    }
