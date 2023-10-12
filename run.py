# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from   flask_migrate import Migrate
from   flask_minify  import Minify
from   sys import exit

from apps.config import config_dict
from apps import create_app, db


from dotenv import load_dotenv

from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from datetime import datetime,timedelta
from flask_login import LoginManager,current_user,login_user
from apps.authentication.models import Users
from flask import session,request,Response,render_template,current_app
from flask_mail import Mail,Message
# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:

    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
Migrate(app, db)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)
    
if DEBUG:
    app.logger.info('DEBUG            = ' + str(DEBUG) )
    app.logger.info('Page Compression = ' + 'FALSE' if DEBUG else 'TRUE' )
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)
##
# Load environment variables from .env file
load_dotenv()

# Access the secret key from the environment
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = app_config.SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_TYPE'] = 'filesystem'
current_dir = os.getcwd()+"/session/storage/"
app.config['SESSION_FILE_DIR'] = current_dir 

# Create the session storage directory if it doesn't exist
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
app.config['SESSION_SQLALCHEMY'] = db
app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
##
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465  # or the appropriate port number
app.config['MAIL_USE_SSL'] = True  # or False if not using TLS/SSL

app.config['MAIL_USERNAME'] = 'jcvirani2000@gmail.com'
app.config['MAIL_PASSWORD'] = 'hukx vvaq uxop ibtd'
app.config['MAIL_DEFAULT_SENDER'] = 'jcvirani2000@gmail.com'

Session(app)
mail = Mail(app)
mail.debug = 1  # Set to 1 for debugging
login_manager = LoginManager(app)
###########################
@login_manager.user_loader
def load_user(user_id=2):
    # Load and return the User object for the given user_id
    return Users.query.get(int(user_id))
@app.route('/get')
def Test():
    current_loggin_user = current_user.username
    user = Users.query.filter_by(username=current_loggin_user).first()
    user_id = user.session_id
    print(user_id)
    if 'sid' in session and user_id == session['sid']:
        return current_user.id
    else:
        return 'Session ID mismatch. Please log in again.'
##################################### ppe kit detection ###########
import cv2
from ultralytics import YOLO
#from ppe_kit.YOLO_Video import video_detection
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ppe_kit.sort_master.sort import Sort
import numpy as np
import math
##############
model = YOLO("models/ppe_kit_det/ppe_kit_det.pt")
classNames = ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest', 'Person', 'Safety Cone',
             'Safety Vest', 'machinery', 'vehicle']

# Initialize the SORT tracker
mot_tracker = Sort()





def send_email(recipient, subject, body,image_path=None):
    with app.app_context():
        msg = Message(subject, sender=current_app.config['MAIL_USERNAME'], recipients=[recipient])
        msg.body = body
         # Attach the image file if provided
        if image_path:
            with app.open_resource(image_path) as img_file:
                msg.attach(image_path, 'image/jpeg', img_file.read())

        mail.send(msg)
        print("Email sent successfully.")
tracked_persons = {}
def video_detection(path_x, email):
    video_capture = path_x
    cap = cv2.VideoCapture(video_capture)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
   
   
    while True:
        success, img = cap.read()
        results = model(img, stream=True)

        frame_objects = []

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])
                class_name = classNames[cls]
                label = f'{class_name}{conf}'

                if class_name == 'Person':
                    if conf > 0.5:
                        frame_objects.append([x1, y1, x2, y2])

                # Draw bounding boxes and labels
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        if frame_objects:
            # Pass the frame_objects to the SORT tracker
            trackers = mot_tracker.update(np.array(frame_objects))

            for d in trackers:
                x1, y1, x2, y2, track_id = d
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                if class_name in ['NO-Hardhat', 'NO-Mask', 'NO-Safety Vest', 'Person']:
                    # Person detected without safety gear
                    if conf > 0.5:
                        print("enterd in class name loop")
                        # Check if this person has been tracked before
                        if track_id not in tracked_persons:
                            tracked_persons[track_id] = {'detected_safety_gear': False}
                            print("enterd in track_id ")
                        if not tracked_persons[track_id]['detected_safety_gear']:
                            print("Person detected without safety gear")
                            
                            # Capture the image
                            image_filename = f"/home/torque/github/main/Torque-AI-portal/ppe_kit/img_of_without_safetykit_det/person_{track_id}_no_safety_gear.jpg"
                            cv2.imwrite(image_filename, img)
                            
                            # Send email notification within Flask application context
                            email_subject = "Safety Gear Alert"
                            email_body = f"Person {track_id} detected without safety gear. Image captured."
                            send_email(recipient=email, subject=email_subject, body=email_body,image_path=image_filename)
                            
                            # Mark that an email has been sent for this person
                            tracked_persons[track_id]['detected_safety_gear'] = True

        yield img

def generate_frames_web(path_x,email):
  
    yolo_output = video_detection(path_x,email)
    for detection_ in yolo_output:
        ref,buffer=cv2.imencode('.jpg',detection_)

        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')

@app.route("/ppe_kit_detection", methods=['GET','POST'])
def ppe_kit_detection():
    # session.clear()
    return render_template('pages/ui.html')

# To display the Output Video on Webcam page
@app.route('/video_inference_ppe_kit_detection')
def video_inference_ppe_kit_detection():
    recipient_email = current_user.email

    #return Response(generate_frames(path_x = session.get('video_path', None),conf_=round(float(session.get('conf_', None))/100,2)),mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(generate_frames_web(path_x="rtmp://media5.ambicam.com:1938/live/1efa24f9-0cd0-47c5-b604-c7e3ee118302",email=recipient_email), mimetype='multipart/x-mixed-replace; boundary=frame')
##########################

#################################
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=3000,debug=True)






