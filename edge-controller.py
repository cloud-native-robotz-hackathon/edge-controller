from flask import Flask, request
import gopigo3
import easygopigo3 as easy
import atexit
import cv2
import base64
import threading
import time
import sys
import traceback

# --- Thread-Safe Camera Class (Unchanged) ---
class ThreadedCamera:
    def __init__(self, src='/dev/video0'):
        self.capture = cv2.VideoCapture(src, cv2.CAP_V4L)
        if not self.capture.isOpened():
            self.capture = None
            return
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.status, self.frame = self.capture.read()
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while True:
            if self.capture and self.capture.isOpened():
                self.status, self.frame = self.capture.read()
            else:
                break
            time.sleep(.01)

    def read(self):
        return self.frame

    def release(self):
        if self.capture:
            self.capture.release()

# --- Flask Application and GoPiGo Setup ---
app = Flask(__name__)

print("--- Initializing GoPiGo Hardware ---")
GPG = gopigo3.GoPiGo3()
easygpg = easy.EasyGoPiGo3()
distance_sensor = easygpg.init_distance_sensor()
servo = easygpg.init_servo()
servo.reset_servo()
easygpg.set_speed(300)
easygpg.close_eyes()
print("--- GoPiGo Initialized ---")

# --- State Management Setup ---
is_moving = False
motion_lock = threading.Lock()
camera_stream = None

# --- Graceful Exit Handler ---
def exit_handler():
    print("Edge Controller is exiting")
    if easygpg:
        easygpg.close_eyes()
    if camera_stream:
        print("Releasing camera...")
        camera_stream.release()

atexit.register(exit_handler)


# --- Robot Control Endpoints (Updated with State Lock) ---
@app.route('/', methods=['GET'])
def index():
    return "Hackathon Robot ready"

@app.route('/forward/<int:length_in_cm>', methods=['POST'])
def forward(length_in_cm):
    global is_moving
    with motion_lock:
        is_moving = True
    try:
        easygpg.drive_cm(length_in_cm)
    finally:
        with motion_lock:
            is_moving = False
    return "OK"

@app.route('/backward/<int:length_in_cm>', methods=['POST'])
def backward(length_in_cm):
    global is_moving
    with motion_lock:
        is_moving = True
    try:
        if length_in_cm > 0:
            length_in_cm *= -1
        easygpg.drive_cm(length_in_cm)
    finally:
        with motion_lock:
            is_moving = False
    return "OK"

@app.route('/left/<int:degrees>', methods=['POST'])
def left(degrees):
    global is_moving
    with motion_lock:
        is_moving = True
    try:
        if degrees > 0:
            degrees *= -1
        easygpg.turn_degrees(degrees)
    finally:
        with motion_lock:
            is_moving = False
    return "OK"

@app.route('/right/<int:degrees>', methods=['POST'])
def right(degrees):
    global is_moving
    with motion_lock:
        is_moving = True
    try:
        easygpg.turn_degrees(degrees)
    finally:
        with motion_lock:
            is_moving = False
    return "OK"

@app.route('/servo/<int:degrees>', methods=['POST'])
def servo_rotate(degrees):
    # Note: Servo movement is fast, so we might not need to lock it,
    # but it's good practice for consistency.
    servo.rotate_servo(degrees)
    return "OK"

@app.route('/distance', methods=['GET'])
def distance():
    return str(distance_sensor.read_mm())

@app.route('/power', methods=['GET'])
def power():
    return str(easygpg.volt())

# --- Camera Endpoint (Updated with State Check) ---
@app.route('/camera', methods=['GET'])
def camera():
    global camera_stream
    global is_moving

    # First, check if the robot is moving.
    with motion_lock:
        if is_moving:
            return "Robot is moving, image would be blurry.", 423 # 423 Locked

    # If not moving, proceed with lazy initialization of the camera.
    if camera_stream is None:
        print("--- Initializing camera for the first time ---")
        camera_stream = ThreadedCamera()
        time.sleep(2.0)
        if camera_stream.capture is None:
            return "Error: Could not open camera.", 500

    # Read and return the frame as before.
    frame = camera_stream.read()
    if frame is None:
        return "Error: Could not read frame from camera.", 500

    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        return "Error: Could not encode frame.", 500
        
    jpg_as_text = base64.b64encode(buffer)
    return jpg_as_text

# --- Main Execution Block ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
