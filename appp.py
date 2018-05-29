#IMPORTS________________________________________________________________________________________________________________________________________________________
from flask import Flask,jsonify,abort,make_response,request, render_template,redirect, url_for, send_from_directory
from json import loads
from bson.json_util import dumps
from pymongo import MongoClient
from gridfs import GridFS 
import json
from math import sin, cos, sqrt, atan2, radians
import requests
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from pyfcm import FCMNotification
import os
#_______________________________________________________________________________________________________________________________________________________________
#DECLARATIONS___________________________________________________________________________________________________________________________________________________
app = Flask(__name__)
client = MongoClient()
db = client.primer
#______________________IMAGES__________________________________________________________________________________________________________________________________
UPLOAD_FOLDER_PROFILES='D:/DND/test1/profilephoto'
UPLOAD_FOLDER_VEHICLEREGISTRATION='D:/DND/test1/numberplate'
UPLOAD_FOLDER_LISCENCE='D:/DND/test1/licsense'
UPLOAD_FOLDER_PACKAGES='D:/DND/test1/Images_Packages'
#UPLOAD_FOLDER_CNIC='Y:/test1/images_CNIC'
ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER_PROFILES'] = UPLOAD_FOLDER_PROFILES
app.config['UPLOAD_FOLDER_VEHICLEREGISTRATION'] = UPLOAD_FOLDER_VEHICLEREGISTRATION
app.config['UPLOAD_FOLDER_LISCENCE'] = UPLOAD_FOLDER_LISCENCE
app.config['UPLOAD_FOLDER_PACKAGES'] = UPLOAD_FOLDER_PACKAGES
#app.config['UPLOAD_FOLDER_CNIC'] = UPLOAD_FOLDER_CNIC
#_______________________FCM______________________________________________________________________________________________________________________
push_service = FCMNotification(api_key="AAAASWndTx4:APA91bGDgW-pVVo8w6IaK7M6hhjADmuROjV-8HDbopdY6TeG2fLv3Qs_kD0HRA8akKpEGBPUufXlUQGVVc1ZkLP0czdBYMqi6AIzYBPm6TlyLCo7Y4VIcGr-81MOT__3Ai9dElqifmU0")
#_____________________________________________________________________________________________________________________________________________
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/imageupload', methods=['POST'])
def imageupload():
    type = request.args.get("type")
    if 'file' not in request.files:
            # flash('No file part')
            # return jsonify({'upload' : "Koi file part nahi"})
        return jsonify({'upload' : "No file was found in the request parameters"})
    file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
    if file.filename == '':
            # flash('No selected file')
            # return redirect(request.url)
        return jsonify({'upload' : "file selection error"})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if(type=="Package"):
            file.save(os.path.join(app.config['UPLOAD_FOLDER_PACKAGES'], filename))
        elif(type=="Profile"):
            file.save(os.path.join(app.config['UPLOAD_FOLDER_PROFILES'], filename))
        elif(type=="VehicleRegistration"):
            file.save(os.path.join(app.config['UPLOAD_FOLDER_VEHICLEREGISTRATION'], filename))            
        else:#profile lowest as least accessed
            file.save(os.path.join(app.config['UPLOAD_FOLDER_LISCENCE'], filename))
        
            # return redirect(url_for('uploaded_file',
            #                         filename=filename))
        return jsonify({'upload' : "Success"})
    return jsonify({'upload' : "The File type uploaded is not allowed"})

@app.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_PACKAGES'],
                               filename)
@app.route('/getProfilePhoto/<filename>')
def profilephoto(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_PROFILES'],
                               filename)
#_______________________________________________________________________________________________________________________________________________________________

#FORM SIGNUP AND LOGIN TRANSPORTER______________________________________________________________________________________________________________________________

# @app.route('/upload', methods=['PUT','POST'])
# def upload():
#     with grid_fs.new_file(filename=request.data.fileName) as fp:
#         fp.write(request.data)
#         file_id = fp._id
#         return fp._id

# @app.route('/lasttransporterid', methods=['GET'])
# def lasttransporterid():
#     data = db.transporter.find({}).sort([('_id',-1)]).limit(1)#get the last record that was inserted
#     data=dumps(data)#convert object to string type
#     data=json.loads(data)	
#     return jsonify({"status": "ok", 'content': data})#return data in JSON string    	
#__________________________________-
@app.route('/signup', methods=['POST'])
def signup():
    content = json.loads(request.data)#get the data passed form post
    Records = db.transporter.find({"Email":content['Email']})#email to check if it has been used before
    #convert object type to JSON
    Records=dumps(Records)
    Records=json.loads(Records)
    #check if email was used if used returned error else create new record
    if Records==[]:
        Records = db.transporter.find({"CNIC":content['CNIC']})
        #convert object type to JSON
        Records=dumps(Records)
        Records=json.loads(Records)
        if Records==[]:
            content['Password'] = generate_password_hash(content['Password'])  # overwrite orignal password with hash as a security measure
            old = db.transporter.find({}).sort([('ID', -1)]).limit(1)
            old = dumps(old)
            old = json.loads(old)
            if old != []:
            	content['ID'] = int(old[0]['ID']) + 1
            	data = db.transporter.insert_one(content)  # insert new record
            	data = dumps(data.inserted_id)  # convert object type to string
            	return jsonify({"Error": "none", "Operation": "success", "content": data})
            else:
            	content['ID'] = 1
            	data = db.transporter.insert_one(content)  # insert new record
            	data = dumps(data.inserted_id)  # convert object type to string
            	return jsonify({"Error": "none", "Operation": "success", "content": data})
        else:
        	return jsonify({"Error": "An account with the entered CNIC already exists","Operation": "none"})
    else:
    	return jsonify({"Error": "Email already taken","Operation": "none"})



    
@app.route('/login', methods=['POST'])
def login():
    content =json.loads(request.data)
    email=content['Email']#get the email user entered
    data = db.transporter.find({"Email":email})#search if the record exits
    #convert object type to JSON
    data=json.loads(dumps(data))
    #check if account exirts if not return error else compare passwords
    if (data==[]):
    	return jsonify({"Error": "No such account exits", "Access":"none"})
    else:
        match=check_password(data[0]['Password'], content['Password'])#check if passwords exits
        if match:
            return jsonify({"Error": "none", "Access": "granted", "content": data})
        else:
            return jsonify({"Error": "Password Mismatch", "Access": "denied"})

def check_password(db, entered):
        return check_password_hash(db, entered)

@app.route('/updateToken', methods=['POST'])
def updateToken():
    content =json.loads(request.data)
    if(content['appType']=="Transporter"):
    	db.transporter.update_one({'ID':int(content['ID'])}, {"$set":{"Token":content['Token']}}, upsert=False)# if exits update it
    else:
    	db.sender.update_one({'ID':int(content['ID'])}, {"$set":{"Token":content['Token']}}, upsert=False)# if exits update it

    return jsonify({"status": "ok", 'content': "ok"})

@app.route('/trackUser', methods=['POST'])
def trackUser():
    content =json.loads(request.data)
    data= db.tracking.find({"TransporterID": content['TransporterID']})
    data=json.loads(dumps(data))
    if (data==[]):
    	db.tracking.insert_one(content)
    else:
    	db.tracking.update_one({'TrackingID':content['TransporterID']}, {"$set":{"Latitude":content['Latitude'],"Longitude":content['Longitude']}}, upsert=False)# if exits update it		
    return jsonify({"status": "ok", 'content': "recieved"})
    

#_______________________________________________________________________________________________________________________________________________________________

#GETTING PACKAGES TRANSPORTER AND PROFILE_______________________________________________________________________________________________________________________
@app.route('/allpackages', methods=['GET'])
def allpackages():
    n = int(request.args.get("skips"))#get the number of packages that have already been served on the application
    print(n)
    docs = db.package.find({"Status":"Awaiting"}, {'_id': False}).skip(n).limit(10)#skip already served packages and return next 10 packages
    data=[]# array to hold return packages
    for doc in docs:
        data.append(doc)
    return jsonify({"status": "ok", 'content': data})# reponse return

#This methods works by checking if the package is near the transporter in 2 km radius
@app.route('/nearbypackages', methods=['GET'])
def nearbypackages():
	R = 6373.0# radius of the earth
	#___Get coords passed to this route______________________
	latitude = float(request.args.get("Lat"))
	longitude = float(request.args.get("Long"))
	radius = float(request.args.get("Radius"));
	#________________________________________________________________________
	#___Convert args to radian measure_______________________________________
	lat1 = radians(latitude)
	lon1 = radians(longitude)
	docs = db.package.find({"Status":"Awaiting"}, {'_id': False})
	data=[]
	for doc in docs:
		temp=json.loads(dumps(doc))
		#___Get coords from package and convert to radian________________________
		lat2 = radians(float(temp['SourceLatitude']))
		lon2 = radians(float(temp['SourceLongitude']))
		#________________________________________________________________________
    	#___formula to check distance____________________________________________
		dlon = lon2 - lon1
		dlat = lat2 - lat1
		a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
		c = 2 * atan2(sqrt(a), sqrt(1 - a))
		distance = R * c
		#________________________________________________________________________
		if distance<=radius:#__if within distance add to array
			data.append(doc)
	return jsonify({"status": "ok", 'content': data})#return response

#This methods works by checking if the package is near the transporter in 2 km radius and its
#delivery is also 2 km from the destination
@app.route('/enroutepackages', methods=['GET','POST'])
def enroutepackages():
    R = 6373.0;# radius of the earth
    #___Get coords passed to this route________________________
    SourceLat=float(request.args.get("SourceLat"))
    SourceLng=float(request.args.get("SourceLng"))
    DestinationLat = float(request.args.get("DestinationLat"))
    DestinationLng = float(request.args.get("DestinationLng"))
    #________________________________________________________________________
	#___Convert args to radian measure________________________
    radius = float(request.args.get("Radius"));
    SourceLat = radians(SourceLat)
    SourceLng = radians(SourceLng)
    DestinationLat = radians(DestinationLat)
    DestinationLng = radians(DestinationLng)
    #________________________________________________________________________
    docs = db.package.find({"Status":"Awaiting"}, {'_id': False})#get all packages that are awaiting
    data=[]# array to store variables that are to be returned
    for doc in docs:
    	temp=json.loads(dumps(doc))
    	#___Get coords from package and convert to radian________________________
    	lat2 = radians(float(temp['SourceLatitude']))
    	lon2 = radians(float(temp['SourceLongitude']))
    	lat3 = radians(float(temp['DestinationLatitude']))
    	lon3 = radians(float(temp['DestinationLongitude']))
    	#________________________________________________________________________
    	#___formula to check distance____________________________________________
    	dlon1 = lon2 - SourceLng
    	dlat1 = lat2 - SourceLat
    	dlon2 = lon3 - DestinationLng
    	dlat2 = lat3 - DestinationLat
    	a = sin(dlat1 / 2)**2 + cos(SourceLat) * cos(lat2) * sin(dlon1 / 2)**2
    	c = 2 * atan2(sqrt(a), sqrt(1 - a))
    	distance1 = R * c
    	a = sin(dlat2 / 2)**2 + cos(DestinationLat) * cos(lat3) * sin(dlon2 / 2)**2
    	c = 2 * atan2(sqrt(a), sqrt(1 - a))
    	distance2 = R * c
    	#________________________________________________________________________
    	if (distance2<=radius and distance1<=radius):#__if within distance add to array
    		data.append(doc)
    return jsonify({"status": "ok", 'content': data})#return response



@app.route('/deliveryCompleted', methods=['GET'])
def deliveryCompleted():
    token = int(request.args.get("token"))# get confirmation token
    idPackage = int(request.args.get("PackageID"))# package id for which delivery process is to be completed
    package = db.package.find({"PackageID":idPackage}, {'_id': False})# get the package from database
    package=json.loads(dumps(package))
    if(package[0]['token']==token):#check if token matches the one that was provided to the sender
    	db.package.update_one({'PackageID':idPackage}, {"$set":{"Status":"Completed"}}, upsert=False)# if exits update it
    	return jsonify({"status": "ok", 'content': "success"})#return response
    else:
    	return jsonify({"status": "ok", 'content': "failed"})#return response


@app.route('/enquedpackages', methods=['GET'])
def enquedpackages():
    idTransporter = int(request.args.get("TransporterID"))# transporter id to match his intransit packages
    docs = db.package.find({"TransporterID":idTransporter,"Status":"Enqueued"}, {'_id': False})#find packages that are in transit by said trasnporter
    docs=json.loads(dumps(docs))
    data=[]# array to store return data
    if (docs==[]):# if no packages intransit return failed
    	return jsonify({"status": "ok", 'content': "failed"})# return response
    else:# if packages in transit are found 		
    	for doc in docs:
    		data.append(doc)
    return jsonify({"status": "ok", 'content': data})# return response





@app.route('/pendingpackages', methods=['GET'])
def pendingpackages():
	idTransporter = int(request.args.get("TransporterID"))#transporter id to check his pending bids for packages
	data = db.pending.find({"ID": idTransporter},{'_id': False,'ID':False})
	data=json.loads(dumps(data))#convert object to string type
	if(data==[]):# if no pending packages return failed
		return jsonify({"status": "ok", 'content': "failed"})#return data in JSON string
	else:
		packages=[];
		for packageid in data[0]:
			ids=data[0][packageid] # get id of the package		
			pack=db.package.find({"PackageID": ids}, {'_id': False})# find the package
			packages.append(pack[0])#add to arrat
	return jsonify({"status": "ok", 'content': packages})#return response

    

@app.route('/getransporterdata', methods=['GET'])
def getransporterdata():
	idTransporter = int(request.args.get("TransporterID"))#get id 
	data = db.transporter.find({"ID": idTransporter})# find his information in database
	data=json.loads(dumps(data))#convert object to string type and then json
	return jsonify({"status": "ok", 'content': data})#return response



@app.route('/requestDelivery', methods=['GET'])
def requestDelivery():
	idPackage = int(request.args.get("PackageID"))
	idTransporter = int(request.args.get("TransporterID"))
	idSender = int(request.args.get("SenderID"))
	fcmtoken = db.sender.find({"ID": idSender},{"FCMToken":1, "_id":0})
	fcmtoken = dumps(fcmtoken)
	print(fcmtoken["FCMToken"])

	message_body = "Your Package has a bidder!"
	data_message = {
    "TransporterID" : idTransporter,
	"PackageID" : idPackage
        }
	idString=str(idPackage)
	package=db.package.find({"ID":idPackage}, {'_id': False})
	package=json.loads(dumps(package))#convert object to string type and then json
	if(package[0]['TransporterID']==0):
		data=db.pending.find({"ID": idTransporter})
		data=json.loads(dumps(data))#convert object to string type and then json
		print(idString)
		if (data==[]):#check if pending for that transporter exits
			content={}
			content['ID'] = idTransporter
			content[idString] = idPackage
			data = db.pending.insert_one(content)#insert new record
			result = push_service.notify_single_device(registration_id=fcmtoken, message_body=message_body, data_message=data_message)
			return jsonify({"status": "ok", 'content': "success", "result" : result})#return data in JSON string
		else:
			if (idString in data[0]):
				return jsonify({"status": "ok", 'content': "rerequested"})
			else:
				db.pending.update_one({'ID':idTransporter}, {"$set":{idString:idPackage}}, upsert=False)# if exits update it
				result = push_service.notify_single_device(registration_id=token, message_body=message_body, data_message=data_message)
				return jsonify({"status": "ok", 'content': "success", "result" : result})#return data in JSON string
	else:
		return jsonify({"status": "ok", 'content': "failed"})

@app.route('/senderresponse',methods=['PUT'])
def senderresponse():
	content =json.loads(request.data)
	fcmtoken = db.transporter.find({"ID": content['TransporterID']},{"FCMToken":1, "_id":0})
	fcmtoken = dumps(fcmtoken)
	if(content['Status']=="accept"):
		message_body = "Your Bid has been accepted!"
		data_message = {
			"PackageID" : content['PackageID'],
			"LiveTrack" : "true"
		}
		
		
		db.pending.delete_one({'ID': content['TransporterID']})
		db.package.update_one({'ID':content['PackageID']}, {"$set":{"Status":"Intransit"}}, upsert=False)
		result = push_service.notify_single_device(registration_id=fcmtoken, message_body=message_body, data_message=data_message)
		return jsonify({"livetrack": "yes", "result": result})
	else:
		message_body = "Your Bid has been REJECTED!"
		data_message = {
			"LiveTrack" : "false",
		}
		fcmtoken = db.transporter.find({"ID": content['TransporterID']},{"FCMToken":1, "_id":0})
		for regID in fcmtoken:
			token = regID['FCMToken']

		db.pending.delete_one({'ID': content['TransporterID']})
		result = push_service.notify_single_device(registration_id=token, message_body=message_body, data_message=data_message)
		return jsonify({"livetrack": "no", "result": result})

	#if reject then remove from pending
	#if accept then remove from pending and add to package and transporter

@app.route('/notify',methods=['GET'])
def notify():
	url = 'https://fcm.googleapis.com/fcm/send'
	body = {  
		"notification":{  
  			"title":"My web app name",
  			"body":"message",
		},
		"to":"dVogDp3SmXE:APA91bFVEiEOAwBvlPYp-AaCBWtg8lYSvu2kYdChlzCdDosPQ7rfATu3ook_hNliJptOoK0Tun-OzG3B2AAIb6e75bAEF523alFB59Oq2BjbXkW2ZI_oJeSMbLMCKepzwnMUrHB62gSD"
 	}


	headers = {"Content-Type":"application/json",
        "Authorization":"key=AAAAnlrDg6Y:APA91bGe1A-8e7f7Af5hJlfakXt6noDoWgTJiOk6iJDAxt6BY4eqjo0aBy14lkicp4mskuQYVvEgdFr3Ao4WVP2OO5qeW6vFEAyYRiAobzVMfWfWRtQAKauhEPesgC5rULB71YCsWgMO"}
	r=requests.post(url, data=json.dumps(body), headers=headers)
	print(r);
	return jsonify({"status": "ok"})#return data in JSON string
#______________________________________________________________________________________________________________________________________________________________

if __name__ == "__main__":
	app.run(debug =True)