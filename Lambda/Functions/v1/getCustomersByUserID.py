import json
import boto3
import time

client = boto3.client('athena')
def lambda_handler(event, context):
    my_query='SELECT * FROM "projectdatabase"."customers" WHERE userid = \''+event['userid']+'\''
    # return my_query
    response = client.start_query_execution(
        QueryString = my_query,
        # QueryString = 'SELECT id,name,email,phone,userid FROM "projectdatabase"."customers" limit 100',
        QueryExecutionContext={
            'Database': 'projectdatabase'
        },
        ResultConfiguration={
        'OutputLocation': 's3://aws-project-athena-results/'
        }
    ) 
    
    queryExecutionId = response['QueryExecutionId']
    
    time.sleep(35)
    results = client.get_query_results(QueryExecutionId=queryExecutionId)
    final_result=[]
    for row in results['ResultSet']['Rows'][1:]:
        row_data=[]
        for item in row['Data']:
            row_data.append(item['VarCharValue'])
        final_result.append({"id":row_data[0],"name":row_data[1],"email":row_data[2],"phone":row_data[3],"userid":row_data[4]})
    return final_result