import json
import boto3
import time
from collections import OrderedDict
from boto3.dynamodb.conditions import Key, Attr

client = boto3.client('athena')
def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Messages')
    
    response = table.scan(
	    FilterExpression = (Attr('ReceiverID').eq(event['receiverID'])| Attr('SenderID').eq(event['receiverID']))&(Attr('ReceiverID').eq(event['senderID'])| Attr('SenderID').eq(event['senderID']))
	    
    )
    # print(len(response['Items']))

    # final_result=[]
    final_result={}

    # for x in range(1, (len(response['Items'])+1)):
    #     print(response['Items'][])
    
    for item in response['Items']:
        # print(item['Index'])
        if(event['senderID']==item['SenderID']):
            m_type='sent'
        else:
            m_type='received'
        final_result[int(str(item['Index']))]={"type":m_type,"time":item['Time'],"body":item['Body'],'index':item['Index']}
        #final_result.append({int(str(item['Index'])):{"type":m_type,"time":item['Time'],"body":item['Body']}})
    print(final_result)
    print("___________-________________")
    

    final_final=[]
    for x in range(1, (len(final_result)+1)):
        print(final_result[x])
        final_final.append(final_result[x])
    return final_final
    
    
