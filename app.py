import os
from flask import Flask,jsonify,abort,make_response,request, render_template, redirect, url_for, send_from_directory
from json import loads
from bson.json_util import dumps
from pymongo import MongoClient
from gridfs import GridFS
import json
import gridfs
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from pyfcm import FCMNotification

app = Flask(__name__)
client = MongoClient()
db = client.primer
UPLOAD_FOLDER = 'D:/DND/test1/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
push_service = FCMNotification(api_key="AAAASWndTx4:APA91bGDgW-pVVo8w6IaK7M6hhjADmuROjV-8HDbopdY6TeG2fLv3Qs_kD0HRA8akKpEGBPUufXlUQGVVc1ZkLP0czdBYMqi6AIzYBPm6TlyLCo7Y4VIcGr-81MOT__3Ai9dElqifmU0")
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/imageupload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            # flash('No file part')
            # return jsonify({'upload' : "Koi file part nahi"})
            return jsonify({'upload' : "Koi file part nahi hai"})
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            # flash('No selected file')
            # return redirect(request.url)
            return jsonify({'upload' : "Koi file select nahi hui"})
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('uploaded_file',
            #                         filename=filename))
            return jsonify({'upload' : "Upload Done hai"})
    return jsonify({'upload' : "OK hogaya"})

@app.route('/senderprofileimage', methods=['GET', 'POST'])
def upload_profileimage():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            # flash('No file part')
            # return jsonify({'upload' : "Koi file part nahi"})
            return jsonify({'upload' : "Koi file part nahi hai"})
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            # flash('No selected file')
            # return redirect(request.url)
            return jsonify({'upload' : "Koi file select nahi hui"})
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('uploaded_file',
            #                         filename=filename))
            return jsonify({'upload' : "Upload Done hai"})
    return jsonify({'upload' : "OK hogaya"})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/active', methods=['GET','POST'])
def active():
    idSender = int(request.args.get('SenderID'))
    docs = db.package.find({"SenderID":idSender,"Status":"Active"})
    docs=dumps(docs)
    docs=json.loads(docs)
    data=[]
    if (docs==[]):
    	return jsonify({"status": "Not ok", 'content': "failed",'data':data})
    else:		
    	for doc in docs:
    		data.append(doc)
    return jsonify(data)

@app.route('/all', methods=['GET','POST'])
def all():
    idSender = int(request.args.get('SenderID'))
    docs = db.package.find({"SenderID":idSender})
    docs=dumps(docs)
    docs=json.loads(docs)
    data=[]
    if (docs==[]):
    	return jsonify({"status": "Not ok", 'content': "failed",'data':data})
    else:		
    	for doc in docs:
    		data.append(doc)
    return jsonify(data)

@app.route('/allsender', methods=['GET','POST'])
def allsender():
    docs = db.package.find({})
    docs=dumps(docs)
    docs=json.loads(docs)
    data=[]
    if (docs==[]):
    	return jsonify({"status": "Not ok", 'content': "failed",'data':data})
    else:		
    	for doc in docs:
    		data.append(doc)
    return jsonify(data)

@app.route('/intransit', methods=['GET','POST'])
def intransit():
    idSender = int(request.args.get('SenderID'))
    docs = db.package.find({"SenderID":idSender,"Status":"In-Transit"})
    docs=dumps(docs)
    docs=json.loads(docs)
    data=[]
    if (docs==[]):
    	return jsonify({"status": "Not ok", 'content': "failed",'data':data})
    else:		
    	for doc in docs:
    		data.append(doc)
    return jsonify(data)


@app.route('/packagedetails', methods=['GET','POST'])
def packagedetails():
    id = int(request.args.get('PackageID'))
    docs = db.package.find({"ID":id})
    docs=dumps(docs)
    docs=json.loads(docs)
    data=[]
    if (docs==[]):
    	return jsonify({"status": "Not ok", 'content': "failed",'docs':docs})
    else:		
    	for doc in docs:
    		data.append(doc)
    return jsonify(data)

@app.route('/senderprofile', methods=['GET','POST'])
def senderprofile():
    id = int(request.args.get('ID'))
    docs = db.sender.find({"ID":id})
    docs=dumps(docs)
    docs=json.loads(docs)
    return jsonify({'content':docs})
    
@app.route('/notification', methods=['GET','POST'])
def notification():
    senderID = int(request.args.get('SenderID'))
    registration_id = db.sender.find({"ID": senderID},{"FCMToken":1, "_id":0})
    for regID in registration_id:
        token = regID['FCMToken']
    
    message_body = "yeh hai apka message"
    data_message = {
    "Nick" : "Mario",
    "body" : "great match!",
    "Room" : "PortugalVSDenmark"
        }
    result = push_service.notify_single_device(registration_id=token, message_body=message_body, data_message=data_message)
    return jsonify({"Post":"Notification sent!", "result": result})

@app.route('/requestDelivery', methods=['GET','POST'])
def requestDelivery():
    

@app.route('/signup', methods=['POST'])
def signup():
    content = json.loads(request.data)#get the data passed form post
    Records = db.sender.find({"Email":content['Email']})#email to check if it has been used before
    #convert object type to JSON
    Records=dumps(Records)
    Records=json.loads(Records)
    #check if email was used if used returned error else create new record
    if Records==[]:
        Records = db.sender.find({"CNIC":content['CNIC']})
        #convert object type to JSON
        Records=dumps(Records)
        Records=json.loads(Records)
        if Records==[]:
            content['Password'] = generate_password_hash(content['Password'])  # overwrite orignal password with hash as a security measure
            old = db.sender.find({}).sort([('ID', -1)]).limit(1)
            old = dumps(old)
            old = json.loads(old)
            if old != []:
            	content['ID'] = int(old[0]['ID']) + 1
            	data = db.sender.insert_one(content)  # insert new record
            	data = dumps(data.inserted_id)  # convert object type to string
            	return jsonify({"Error": "none", "Operation": "success", "content": content['ID']})
            else:
            	content['ID'] = 1
            	data = db.sender.insert_one(content)  # insert new record
            	data = dumps(data.inserted_id)  # convert object type to string
            	return jsonify({"Error": "none", "Operation": "success", "content": content['ID']})
        else:
        	return jsonify({"Error": "An account with the entered CNIC already exists","Operation": "none"})
    else:
    	return jsonify({"Error": "Email already taken","Operation": "none"})

@app.route('/createpackage', methods=['POST'])
def create():
    data = json.loads(request.data)
    old = db.package.find({}).sort([('ID', -1)]).limit(1)
    old = dumps(old)
    old = json.loads(old)
    if old != []:
        data['ID'] = int(old[0]['ID']) + 1
        print(data)
        id = db.package.insert_one(data)
    else:
        data['ID']= 1
        id = db.package.insert_one(data)

    return jsonify({'post_id' : "OK"})

@app.route('/login', methods=['POST'])
def login():
    content =json.loads(request.data)
    email=content['Email']#get the email user entered
    data = db.sender.find({"Email":email})#search if the record exits
    #convert object type to JSON
    data=dumps(data)
    data=json.loads(data)
    #check if account exirts if not return error else compare passwords
    if data==[]:
        return jsonify({"Error": "No such account exits", "Access":"none"})
    else:
        match=check_password(data[0]['Password'], content['Password'])#check if passwords exits
        if match:
            return jsonify({"Error": "none", "Access": "granted", "content": data})
        else:
            return jsonify({"Error": "Password Mismatch", "Access": "denied"})

def check_password(db, entered):
        return check_password_hash(db, entered)
if __name__== '__main__':
    app.run(debug =True)