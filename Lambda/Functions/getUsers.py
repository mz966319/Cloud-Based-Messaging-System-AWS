import json
import boto3
import time

db_resource = boto3.resource('dynamodb', region_name="us-east-1")
db_client = boto3.client('dynamodb')
def lambda_handler(event, context):
    users_response = db_resource.Table('Users').scan()
    print(users_response['Items'])
    local_user_id=event['userid']
    final_result=[]

    for item in users_response['Items']:
        print(item)
        if(item['UserID']!=local_user_id):
            try:
                count=len(item['CustomersID'])
            except:
                count=0
            final_result.append(
                {
                    "id":item['UserID'],
                    "customersCount":count,
    
                })

    return final_result

