from flask import Flask
from flask import request


import gopigo3
import time
import easygopigo3 as easy
import atexit

import cv2
import base64

# Robot Hackathon Edge Controller

app = Flask(__name__)

GPG = gopigo3.GoPiGo3()
easygpg = easy.EasyGoPiGo3()

distance_sensor = easygpg.init_distance_sensor()

servo = easygpg.init_servo()
servo.reset_servo()

easygpg.set_speed(300)

easygpg.close_eyes()
# Signal running edge controller with left led
# easygpg.open_left_eye()

print("Edge controller has started")

def exit_handler():
    print ("Edge Controller is exiting")
    easygpg.close_eyes()

def start_executing(command):
    #easygpg.open_right_eye()
    print ("Start executing -> " + command)

def stop_executing(command):
    print ("Stop executing -> " + command)
    easygpg.close_right_eye()

@app.route('/', methods=['GET'])
def index():
    start_executing("Robot ping")
    stop_executing("Robot ping")
    return "Hackathon Robot ready" 
	
@app.route('/forward/<int:length_in_cm>', methods=['POST'])
def forward(length_in_cm):
	
    start_executing ("forward : " + str(length_in_cm))	
    easygpg.drive_cm(length_in_cm)
    stop_executing("forward : " + str(length_in_cm))
    return "OK"

@app.route('/backward/<int:length_in_cm>', methods=['POST'])
def backward(length_in_cm):	
    start_executing ("backward : " + str(length_in_cm))	
    
    # Change sign
    if length_in_cm > 0:
        length_in_cm *= -1
    
    easygpg.drive_cm(length_in_cm)
    stop_executing("backward : " + str(length_in_cm))
    return "OK"

@app.route('/left/<int:degrees>', methods=['POST'])
def left(degrees):
    start_executing ("left : " + str(degrees))

    # Change sign
    if degrees > 0:
        degrees *= -1

    easygpg.turn_degrees(degrees)
    stop_executing("left : " + str(degrees))
    return "OK"

@app.route('/right/<int:degrees>', methods=['POST'])
def right(degrees):
    start_executing ("right : " + str(degrees))
    easygpg.turn_degrees(degrees)
    stop_executing("right : " + str(degrees))
    return "OK"

@app.route('/servo/<int:degrees>', methods=['POST'])
def servo(degrees):
    start_executing ("servo : " + str(degrees))
    servo = easygpg.init_servo()
    servo.rotate_servo(degrees)
    stop_executing("servoZ : " + str(degrees))
    return "OK"

@app.route('/reset', methods=['POST'])
def reset():
    start_executing ("reset")
    #GPG.reset_all()
    stop_executing("reset")

@app.route('/distance', methods=['GET'])
def distance():
    start_executing ("distance")
    stop_executing("distance : " + str(distance_sensor.read_mm()))
    return(str(distance_sensor.read_mm()))

@app.route('/power', methods=['GET'])
def power():
    start_executing ("power")
    current_voltage = str(easygpg.volt())
    stop_executing("power : " + current_voltage)
    return(current_voltage)

@app.route('/camera', methods=['GET'])
def camera():
    cap = cv2.VideoCapture('/dev/video0', cv2.CAP_V4L)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    ret, frame = cap.read()
    ret, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer)
    cap.release()
    return(jpg_as_text)   

if __name__=='__main__':
	app.run(host='0.0.0.0',debug=True)
