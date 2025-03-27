import json
import boto3
import time

client = boto3.client('athena')
def lambda_handler(event, context):
    
    #'SELECT * FROM "projectdatabase"."messages" WHERE "userid" = \''1'\' AND customerid = '15459' ORDER BY time ASC
    my_query='SELECT "type", "time", "body" FROM "projectdatabase"."messages" WHERE userid = \''+event['userid']+'\'AND customerid =\''+event['customerid']+'\' ORDER BY time ASC'
    print(my_query)
    # return my_query
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
    
    time.sleep(8)
    results = client.get_query_results(QueryExecutionId=queryExecutionId)
    print(results['ResultSet']['Rows'])
    final_result=[]
    for row in results['ResultSet']['Rows'][1:]:
        row_data=[]
        for item in row['Data']:
            row_data.append(item['VarCharValue'])
        final_result.append({"type":row_data[0],"time":row_data[1],"body":row_data[2]})
        #final_result.append({"id":row_data[0],"userid":row_data[1],"customerid":row_data[2],"type":row_data[3],"time":row_data[4],"body":row_data[5]})

    return final_result
    #  [{'VarCharValue': 'id'}, {'VarCharValue': 'userid'}, {'VarCharValue': 'customerid'}, {'VarCharValue': 'type'}, {'VarCharValue': 'time'}, {'VarCharValue': 'body'}]}