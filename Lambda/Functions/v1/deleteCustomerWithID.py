import json
import boto3
import time

client = boto3.client('athena')
def lambda_handler(event, context):
    # my_query='insert into "customers"  VALUES ('+event['id']+',\''+event['name']+'\',\''+event['email']+'\',\''+event['phone']+'\',\''+event['userid']+'\')'
    # my_query='SELECT * FROM "projectdatabase"."customers" WHERE userid = \''+event['userid']+'\''
    my_query='DELETE FROM "customers" WHERE id='+event['id']
    print(my_query)
    response = client.start_query_execution(
        QueryString = my_query,
        QueryExecutionContext={
            'Database': 'projectdatabase'
        },
        ResultConfiguration={
        'OutputLocation': 's3://aws-project-athena-results/'
        }
    ) 
    queryExecutionId = response['QueryExecutionId']
    time.sleep(15)
    # results=client.get_query_execution(QueryExecutionId = queryExecutionId)
    # return results