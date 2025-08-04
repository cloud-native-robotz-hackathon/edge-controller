from flask import Flask, request, send_file, make_response
import gopigo3
import easygopigo3 as easy
import atexit
import cv2
import base64
import threading
import time
import sys
import traceback
import os
import logging

__version__ = "2.1.1"

# --- Thread-Safe Camera Class ---
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
app.logger.setLevel(level=os.environ.get('EDGE_CONTROLLER_LOGLEVEL', 'INFO').upper())

app.logger.info("--- Initializing GoPiGo Hardware ---")
GPG = gopigo3.GoPiGo3()
easygpg = easy.EasyGoPiGo3()
distance_sensor = easygpg.init_distance_sensor()
servo = easygpg.init_servo()
servo.reset_servo()
easygpg.set_speed(300)
easygpg.close_eyes()
app.logger.info("--- GoPiGo Initialized ---")

# --- State Management Setup ---
is_moving = False
motion_lock = threading.Lock()
camera_stream = None

# --- Graceful Exit Handler ---
def exit_handler():
    app.logger.info("Edge Controller is exiting")
    if easygpg:
        easygpg.close_eyes()
    if camera_stream:
        app.logger.info("Releasing camera...")
        camera_stream.release()

atexit.register(exit_handler)


# --- Robot Control Endpoints ---
@app.route('/', methods=['GET'])
def index():
    return "Hackathon Robot ready"

@app.route('/version', methods=['GET'])
def version():
    return "v" + __version__

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
    servo.rotate_servo(degrees)
    return "OK"

@app.route('/distance', methods=['GET'])
def distance():
    return str(distance_sensor.read_mm())

@app.route('/power', methods=['GET'])
def power():
    return str(easygpg.volt())

# --- Helper Function ---
def get_camera_jpg(wait_for_move=False, timeout=15.0):
    """
    Captures a frame from the camera.
    :param wait_for_move: If True, waits for robot movement to finish.
    :param timeout: Max seconds to wait for movement to stop.
    :return: A tuple of (buffer, message, status_code).
    """
    global camera_stream
    global is_moving

    # If instructed, wait for the robot to stop moving.
    if wait_for_move:
        start_time = time.time()
        while True:
            with motion_lock:
                if not is_moving:
                    break # Robot has stopped, exit the waiting loop.
            
            if time.time() - start_time > timeout:
                # If we wait too long, return a timeout error.
                return None, "Timed out waiting for robot to stop moving.", 408 # 408 Request Timeout

            time.sleep(0.1) # Wait briefly before checking again.

    # If not waiting, check the lock and fail fast
    with motion_lock:
        if is_moving:
            return None, "Robot is moving, image would be blurry.", 423 # 423 Locked

    # Lazy initialization of the camera.
    if camera_stream is None:
        app.logger.info("--- Initializing camera for the first time ---")
        camera_stream = ThreadedCamera()
        time.sleep(2.0) # Allow camera to initialize
        if camera_stream.capture is None:
            return None, "Error: Could not open camera.", 500

    # Read and encode the frame.
    frame = camera_stream.read()
    if frame is None:
        return None, "Error: Could not read frame from camera.", 500

    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        return None, "Error: Could not encode frame.", 500

    return buffer, "OK", 200

# --- Camera Endpoints (Both now wait for movement) ---
@app.route('/camera', methods=['GET'])
def camera():
    # This endpoint will now WAIT for the robot to stop moving.
    buffer, msg, status = get_camera_jpg(wait_for_move=True)
    
    if buffer is None:
        return msg, status
            
    jpg_as_text = base64.b64encode(buffer)
    return jpg_as_text, status

@app.route('/camera.jpg', methods=['GET'])
def camera_jpg():
    # This endpoint will also WAIT for the robot to stop moving.
    buffer, msg, status = get_camera_jpg(wait_for_move=True)

    if buffer is None:
        return msg, status

    response = make_response(buffer.tobytes())
    response.headers.set('Content-Type', 'image/jpeg')
    response.status_code = status
    return response

# --- Main Execution Block ---
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        threaded=True, # Important for handling concurrent requests
        debug=(os.environ.get('EDGE_CONTROLLER_DEBUG', 'False') == 'True')
    )

