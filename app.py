from flask import Flask, session,redirect, url_for, render_template, request, jsonify
from waitress import serve
import boto3
import json
import time

app = Flask(__name__)

app.secret_key = "SecretKeyForapp"


aws_access_key_id=""
aws_secret_access_key=""
aws_session_token=""
boto_client = boto3.Session(
	aws_access_key_id = aws_access_key_id,
	aws_secret_access_key = aws_secret_access_key,
	aws_session_token=aws_session_token,
	region_name="us-east-1"
) 

lambda_client = boto_client.client('lambda')
cognito_client = boto_client.client('cognito-idp')
sns_client = boto_client.client('sns')
db_resource = boto_client.resource('dynamodb', region_name="us-east-1")
db_client = boto_client.client('dynamodb')

@app.route("/")
def welcomePage():
	#print(Attribute_from_response(session['response'], 'sub') )
	if session.get('access_token_isValid') is None:
		return render_template("welcome.html")
	elif session['access_token_isValid'] == True:
		return redirect(url_for('viewCustomers'))

@app.route("/landing",methods=['GET','POST'])
def landing():
    if request.method == 'GET':
        return render_template("landing.html")
    if request.method == 'POST':
        try:
            session['id_token'] = request.form['id_token']
            session['access_token'] = request.form['access_token']
            session['expires_in'] = request.form['expires_in']
            session['token_type'] = request.form['token_type']
            
            try:
                response = cognito_client.get_user(
                    AccessToken = session['access_token']
                )
                session['access_token_isValid'] = True
                session['response'] = response
                session.permanent = True
                return redirect(url_for('viewCustomers'))
            except Exception as e:
                print("reached raised exception:")
                print(e)
                return render_template("Error.html",value="Error: Failed in validating the access token provided.")
        except Exception as e:
            print("reached raised exception:")
            print(e)
            return render_template("Error.html",value="Error: Could not find the required access token.")

@app.route("/logout")
def logout():
	session.clear()
	return redirect(url_for('welcomePage'))

@app.route("/sendMessage", methods=["GET","POST"])
def sendMessage():
	if request.method == "GET":
		if session.get('access_token_isValid') is None:
			return redirect(url_for('welcomePage'))
		return render_template("sendMessage.html",Status = "",value=getCustomers(Attribute_from_response(session['response'], 'sub'),"Available"))


	elif request.method == "POST":
		form = request.form
		print(form)
		customers= form['customers']
		message_body= form['body']
		message_subject = form['subject']
		reply_type= form['replyOption']
		ifEmail = "no"
		ifSMS = "no"
		if form['sendEmail'] == 'true':
			ifEmail = "email"

		if form['sendSMS'] == 'true':
			ifSMS = "sms"


		payload = {
			"UserID": Attribute_from_response(session['response'], 'sub'),
			"CustomersID": customers,
			"Subject": message_subject,
			"Body": message_body,
			"ifEmail": ifEmail,
			"ifSMS": ifSMS,
			"replyType": reply_type
		}
		print(payload)
		sendResult = lambda_client.invoke(
			FunctionName='sendMessageToCustomers',InvocationType='RequestResponse',Payload=json.dumps(payload)
		)
		if "FunctionError" not in sendResult and 'statusCode' not in sendResult: 
			sendResultData = json.loads(sendResult['Payload'].read())
			
			print(sendResultData)
			return render_template("sendMessage.html",Status = sendResultData[0],value=getCustomers(Attribute_from_response(session['response'], 'sub'),"Available"))

		else:
			return render_template("Error.html",value=("An error occured when send message to customers lambda function was invoked. Error: " + sendResult["FunctionError"]))


@app.route("/addNewCustomer")
def addCustomer():
	if session.get('access_token_isValid') is None:
		return redirect(url_for('welcomePage'))

	return render_template("addNewCustomer.html")

@app.route("/add_new_customer_form_handler", methods=['POST'])
def add_new_customer_form_handler():
	customer_name = request.form['newCustomerName']
	customer_phone = request.form['newCutomperPhoneNumber']
	customer_email = request.form['newCustomerEmail']

	payload = {
		"UserID": Attribute_from_response(session['response'], 'sub'),
		"phone": customer_phone,
		"email": customer_email,
		"name": customer_name
	}
	payload = json.dumps(payload)
	result = lambda_client.invoke(FunctionName='addNewCustomerWithUserID',InvocationType="RequestResponse", Payload=payload)
	if "FunctionError" not in result: 
		customer_id = json.loads(result['Payload'].read())
		return redirect(url_for('viewCustomers'))
	else:
		return render_template("Error.html",value=("An error occured when add new customer lambda function was invoked. Error: " + result["FunctionError"]))

@app.route("/viewCustomers", methods=['GET','POST'])
def viewCustomers():
	if session.get('access_token_isValid') is None:
		return redirect(url_for('welcomePage'))

	if request.method == 'GET':
		searchType="Available"
	elif request.method == 'POST':
		searchType = request.form['filter_options']
		print(searchType)
	customer_data=getCustomers(Attribute_from_response(session['response'], 'sub'),searchType)
	# print(customer_data)
	return render_template("viewCustomers.html",data = customer_data, type=searchType, currentUser = Attribute_from_response(session['response'], 'sub'))

@app.route("/viewUsers")
def viewUsers():
	if session.get('access_token_isValid') is None:
		return redirect(url_for('welcomePage'))
	users_data=getUsers()
	return render_template("viewUsers.html",data=users_data)

@app.route("/userProfile")
def userProfile():
	if session.get('access_token_isValid') is None:
		return redirect(url_for('welcomePage'))
	return render_template("userProfile.html")



@app.route("/showMessages",methods=['GET'])
def showMessages():
	if session.get('access_token_isValid') is None:
		return redirect(url_for('welcomePage'))

	id=request.args.get('id')
	this_user_id=request.args.get('userid')
	name=request.args.get('name')
	try:
		index=request.args.get('index')
		deleteFromRecent(this_user_id,index)
	except:
		pass

	# return render_template("showMessages.html",data=getMessagesBycustomerAndUserIDs(id),customer=name)
	return render_template("showMessages.html",data=getMessagesBySenderAndReceiverID(this_user_id,id),customer=name,hide="hide-")

@app.route("/viewRecentReplies")
def viewRecentReplies():
	if session.get('access_token_isValid') is None:
		return redirect(url_for('welcomePage'))
	reply_data=getRepliesUsingUserID(Attribute_from_response(session['response'], 'sub'))
	#reply_data=[]
	hide="hide-"
	if(len(reply_data)==0):
		hide=""
        # print(customer_data)
	return render_template("viewRecentReplies.html",data = reply_data,hide=hide)


@app.route("/editCustomerInfo")
def editCustomerInfo():
	if session.get('access_token_isValid') is None:
		return redirect(url_for('welcomePage'))

	return render_template("editCustomerInfo.html")

@app.route("/update_customer_info_handler", methods=['POST'])
def update_customer_info_handler():
	customer_id= request.form['id']
	name= request.form['name']
	email = request.form['email']
	phone=request.form['phone']
	updateCustomer(customer_id,name,email,phone)
	return redirect(url_for('viewCustomers'))

@app.route("/update_customer_from_list_handler", methods=['POST'])
def update_customer_from_list_handler():
	customer_id = request.form['customerID']
	customer_name = request.form['customerName']
	customer_phone = request.form['customerPhone']
	customer_email = request.form['customerEmail']
	customer_data={"id":customer_id,"name":customer_name,"phone":customer_phone,"email":customer_email}
	if request.form['action'] == 'Delete':
		deleteCustomerFromDB(customer_id)
		return redirect(url_for('viewCustomers'))
	elif request.form['action'] == 'Edit':
		return render_template("editCustomerInfo.html", data=customer_data)
	elif request.form['action'] == 'Add':
		if request.form['searchType'] == "Deleted":
			response = db_resource.Table('Customers').update_item(
				Key={'CustomerID': customer_id},
				UpdateExpression="set deleted = :d",
				ExpressionAttributeValues={
				':d': 0,
				},
				ReturnValues="UPDATED_NEW"
			)
		elif request.form['searchType'] == "All":
			if addExistingUser(Attribute_from_response(session['response'], 'sub'),customer_data) != True:
				return render_template("Error.html",value="Error: Failed in adding existing customer.")
		return redirect(url_for('viewCustomers'))
		

@app.route("/users_list_buttons_handler", methods=['POST'])
def users_list_buttons_handler():
	row_user_id = request.form['userID']
	user_data={"id":row_user_id}
	if request.form['action'] == 'View Customers':
		print("view customers button clicked")
		return viewCustomersForUser(row_user_id)
	elif request.form['action'] == 'Contact':
		print("contact button clicked")
		return render_template("editCustomerInfo.html", data=customer_data)

def viewCustomersForUser(user):
	if session.get('access_token_isValid') is None:
		return redirect(url_for('welcomePage'))
	searchType="Available"
	customer_data=getCustomers(user,searchType)
	return render_template("viewCustomers.html",data = customer_data, type=user,hide="hide-")

def getCustomers(the_user_id,searchType):
	payload = {"userid": the_user_id,"search_type":searchType}
	payload = json.dumps(payload)
	result = lambda_client.invoke(
		FunctionName='getCustomersByUserID',InvocationType='RequestResponse',Payload=payload
	)
	range = result['Payload'].read()
	data = json.loads(range)
	#print(data)
	return data

def getUsers():
	payload = {"userid": Attribute_from_response(session['response'], 'sub')}
	payload = json.dumps(payload)
	result = lambda_client.invoke(
		FunctionName='getUsers',InvocationType='RequestResponse',
		Payload=payload
	)
	range = result['Payload'].read()
	data = json.loads(range)
	#print(data)
	return data

def updateCustomer(customer_id,name,email,phone):
        payload = {"id": customer_id, "name": name, "email": email, "phone": phone}
        payload = json.dumps(payload)
        result = lambda_client.invoke(FunctionName='updateCustomer',InvocationType="RequestResponse", Payload=payload)
        return


def deleteCustomerFromDB(customer_id):
	payload = {"customer_id": customer_id,"user_id":Attribute_from_response(session['response'], 'sub')}
	payload = json.dumps(payload)
	result = lambda_client.invoke(FunctionName='deleteCustomerWithID',InvocationType="RequestResponse", Payload=payload)
	#print(json.loads(result['Payload'].read()))
	return result

def deleteFromRecent(id,index):
	payload = {"id": id,"index":index}
	payload = json.dumps(payload)
	result = lambda_client.invoke(FunctionName='deleteFromRecentRepliesTable',InvocationType="RequestResponse", Payload=payload)
	#print(json.loads(result['Payload'].read()))
	return result


def storeSentToCustomerMessage(customer_id,body):
	time_stamp=time.strftime('%Y-%m-%d %H:%M:%S')
	payload = {"customerid": customer_id, "type": "sent", "time": time_stamp, "body": body, "userid": Attribute_from_response(session['response'], 'sub')}
	payload = json.dumps(payload)
	result = lambda_client.invoke(FunctionName='addMessage',InvocationType="RequestResponse", Payload=payload)
	#print(json.loads(result['Payload'].read()))
	return result

def getMessagesBycustomerAndUserIDs(customer_id):
	payload = {"userid": Attribute_from_response(session['response'], 'sub'),"customerid":customer_id}
	payload = json.dumps(payload)
	result = lambda_client.invoke(
	        FunctionName='getMessagesByUserIdAndCustomerID',InvocationType='RequestResponse',
	        Payload=payload
	)
	range = result['Payload'].read()
	data = json.loads(range)
	#print(data)
	return data

def getMessagesBySenderAndReceiverID(sender,receiver):
	payload = {"senderID": sender,"receiverID":receiver}
	payload = json.dumps(payload)
	result = lambda_client.invoke(
	        FunctionName='getMessagesBySenderAndReceiverID',InvocationType='RequestResponse',
	        Payload=payload
	)
	range = result['Payload'].read()
	data = json.loads(range)
	return data

def getRepliesUsingUserID(userID):
        payload = {"userid": userID}
        payload = json.dumps(payload)
        result = lambda_client.invoke(
                FunctionName='getRecentReplies',InvocationType='RequestResponse',
                Payload=payload
        )
        range = result['Payload'].read()
        data = json.loads(range)
        return data



def storeMessage(sender_id,receiver_id,body):
	time_stamp=time.strftime('%Y-%m-%d %H:%M:%S')
	payload = {"receiverID": receiver_id, "time": time_stamp, "body": body, "senderID": sender_id}
	payload = json.dumps(payload)
	result = lambda_client.invoke(FunctionName='addMessage',InvocationType="RequestResponse", Payload=payload)
	range = result['Payload'].read()
	message_id = json.loads(range)
	return message_id
	# return result

@app.route("/customer_reply_handler", methods=['POST'])
def customer_reply_handler():
	message_id = request.form['messageID']
	print("----->"+request.form['action'])
	try:
		db_client = boto3.client('dynamodb')
		message_response = db_client.get_item(TableName='Messages', Key={'MessageID': {'S':message_id}})
		if(message_response['Item']['Replied']['S']=="1"):
			return "<h1>Already Replied</h1>"
		print(0)
		time_stamp=time.strftime('%Y-%m-%d %H:%M:%S')
		if request.form['action'] == 'Confirm':
			print(message_id+ " confirmed!")
			payload = {"reply_body": "Confirmed!", "time": time_stamp, "message_id": message_id}
		elif request.form['action'] == 'Deny':
			print(message_id+ " denyed!")
			payload = {"reply_body": "Denyed!", "time": time_stamp, "message_id": message_id}
		else:
			print(request.form['action'])
			payload = {"reply_body": request.form['action'], "time": time_stamp, "message_id": message_id}
		
		payload = json.dumps(payload)
		result = lambda_client.invoke(FunctionName='replyHandler',InvocationType="RequestResponse", Payload=payload)
		range = result['Payload'].read()
		data = json.loads(range)
		return data
		print(result)
		# return result
		# return '<!DOCTYPE html> <html lang="en"> <head> <meta charset="UTF-8"> <meta http-equiv="X-UA-Compatible" content="IE=edge"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>Confirm</title> <style> body { font-family: Arial, Helvetica, sans-serif; display: flex; align-items: center; justify-content: center; background-color: grey; } p{ font-size: 3vw; } #main{ margin-top: 25vh; background-color: white; border-radius: 10px; width: 35vw; height: 50vh; display: flex; flex-direction: column; align-items: center; justify-content: center; } </style> </head> <body> <div id="main"> <p>Thank you!</p> </div> </body> </html>'
	except:
		return "<h1>Already Replied</h1>"
@app.route("/customer_reply", methods=['GET'])
def customer_reply():
	message_id = request.args.get('messageID')
	mtype=request.args.get('type')
	try:
		db_client = boto3.client('dynamodb')
		message_response = db_client.get_item(TableName='Messages', Key={'MessageID': {'S':message_id}})
		if(message_response['Item']['Replied']['S']=="1"):
			return "<h1>Already Replied</h1>"
		return render_template("customerReply.html", messageID=message_id,type=mtype)
	except:
		return "<h1>Already Replied</h1>"

def Attribute_from_response(response,att):
    return next(x for x in response['UserAttributes'] if x["Name"] == att)['Value']

def addExistingUser(userID, customerID):
	table = db_resource.Table('Users')
	try:
		response = db_client.transact_write_items(
			TransactItems=[
				{
					'ConditionCheck': {
						'Key': {
							'UserID': {
								'S': userID
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
	except:
		table.put_item(
			Item={
				'UserID': userID,
			}
		)
		print("not found")

	db_client.update_item(TableName="Users",
		Key={'UserID':{'S':userID}},
		UpdateExpression="ADD CustomersID :element",
		ExpressionAttributeValues={":element":{"SS":[customerID]}}
	)
	return True

if __name__ == "__main__":
	serve(app, host='0.0.0.0', port=80)