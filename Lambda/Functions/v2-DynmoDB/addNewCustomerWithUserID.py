import json
import boto3
import time

db_resource = boto3.resource('dynamodb', region_name="us-east-1")
db_client = boto3.client('dynamodb')
def lambda_handler(event, context):
    user_id=event['userid']
    new_customer_id=event['id']
    try:
        table = db_resource.Table('Users')

        
        try:
            response = db_client.transact_write_items(
                TransactItems=[
                    {
                        'ConditionCheck': {
                            'Key': {
                                'UserID': {
                                    'S': user_id
                                }
                            },
                            'ConditionExpression': 'attribute_exists(#UserID)',
                            'ExpressionAttributeNames': {
                                '#UserID': 'UserID'
                            },
                            'TableName': 'Users'
                        }
                    }
                ]
            )
            
            print ("it is there!")
        :
            table.put_item(
            	Item={
            		'UserID': user_id,
        
            	}
            )
            print("not found")

        db_client.update_item(TableName="Users",
               Key={'UserID':{'S':user_id}},
               UpdateExpression="ADD CustomersID :element",
               ExpressionAttributeValues={":element":{"SS":[new_customer_id]}}
           )
        table = db_resource.Table('Customers')
        table.put_item(
        	Item={
        		'CustomerID': new_customer_id,
        		'name': event['name'],
        		'email': event['email'],
        		'phone': event['phone'],
        		'userID':user_id,
        		'deleted':0
        	}
        )
        # return response
        response = db_client.get_item(TableName='Users', Key={'UserID': {'S':user_id }})
        return "->>>" + str(response['Item']['CustomersID']['SS']) + ""
        # for item in 
    
    except Exception as e:
    	return "Failure! " + str(e), 400

    
    
    