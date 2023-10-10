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
from flask_login import current_user
from apps.authentication.models import Users
from flask import session,request,Response,render_template

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
Session(app)
###########################
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

from ppe_kit.YOLO_Video import video_detection
##############
def generate_frames_web(path_x):
    yolo_output = video_detection(path_x)
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
    #return Response(generate_frames(path_x = session.get('video_path', None),conf_=round(float(session.get('conf_', None))/100,2)),mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(generate_frames_web(path_x="rtmp://media5.ambicam.com:1938/live/1efa24f9-0cd0-47c5-b604-c7e3ee118302"), mimetype='multipart/x-mixed-replace; boundary=frame')
##########################

#################################
if __name__ == "__main__":
    app.run(debug=True)






