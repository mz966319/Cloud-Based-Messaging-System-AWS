import json
import boto3
import time

db_resource = boto3.resource('dynamodb', region_name="us-east-1")
db_client = boto3.client('dynamodb')
def lambda_handler(event, context):
    user_id=event['userid']
    final_result=[]

    try:
        if(event['search_type']=="All"):
            print("-------------------->>>>>")
            customer_response = db_resource.Table('Customers').scan()

            for item in customer_response['Items']:
                print (item)
                if(item['deleted']==0):
                    final_result.append(
                    {
                        "id":item['CustomerID'],
                        "name":item['name'],
                        "email":item['email'],
                        "phone":item['phone'],
                        "deleted":item['deleted'],
                        "userid":item['userID']
                        
                    })
            return final_result
            
            
            
        #if not All get customers ids 
        try:
            user_response = db_client.get_item(TableName='Users', Key={'UserID': {'S':user_id }})
            print(user_response['Item']['CustomersID']['SS'])
            for item in user_response['Item']['CustomersID']['SS']:
                customer_response = db_client.get_item(TableName='Customers', Key={'CustomerID': {'S':item}})
                print(customer_response["Item"]['deleted']['N'])
                if (event['search_type']=="Available"):
                    check_deleted="0"
                elif (event['search_type']=="Deleted"):
                    check_deleted="1"
                if(customer_response["Item"]['deleted']['N']==check_deleted):
                    final_result.append(
                    {
                        "id":customer_response["Item"]['CustomerID']['S'],
                        "name":customer_response["Item"]['name']['S'],
                        "email":customer_response["Item"]['email']['S'],
                        "phone":customer_response["Item"]['phone']['S'],
                        "deleted":customer_response["Item"]['deleted']['N'],
                        "userid":user_id
                        
                    })
        except:
            db_resource.Table('Users').put_item(
            	Item={
            		'UserID': user_id,
        
            	}
            )
            print("didnt work")
        return final_result

# response['Item']['CustomersID']['SS']
        
        # dynamodb = boto3.client('dynamodb')
        # response = dynamodb.get_item(TableName='Customers', Key={'CustomerID': {'S': "15459"}})
    except Exception as e:
    	return "Failure! " + str(e), 400
