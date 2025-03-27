import json
import boto3
def lambda_handler(event, context):
    db_resource = boto3.resource('dynamodb', region_name="us-east-1")
    db_client = boto3.client('dynamodb')
    delete_response = db_client.delete_item(
            TableName='NewReplies',
            Key={
                'UserID': {'S': event['id']},
                'Index':{'N': str(event['index'])}
                
            })
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
