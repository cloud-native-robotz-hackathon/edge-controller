from __future__ import print_function, unicode_literals
import optparse
import json
import gopigo3
import time
import easygopigo3 as easy
import atexit   

from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import AtMostOnce, Container

GPG = gopigo3.GoPiGo3()
easygpg = easy.EasyGoPiGo3()

distance_sensor = easygpg.init_distance_sensor()
servo = easygpg.init_servo()
servo.reset_servo()
easygpg.set_speed(300)
easygpg.close_eyes()

class HelloWorld(MessagingHandler):
    
    def __init__(self, url, address):
        super(HelloWorld, self).__init__()
        self.url = url
        self.address = address       

    @staticmethod
    def forward(length_in_cm):	
        HelloWorld.start_executing ("forward : " + str(length_in_cm))	
        easygpg.drive_cm(float(length_in_cm))
        HelloWorld.stop_executing("forward : " + str(length_in_cm))
        return "OK"

    @staticmethod
    def backward(length_in_cm):	
        HelloWorld.start_executing ("backward : " + str(length_in_cm))	
        
        # Change sign
        if length_in_cm > 0:
            length_in_cm *= -1
        
        easygpg.drive_cm(length_in_cm)
        HelloWorld.stop_executing("backward : " + str(length_in_cm))
        return "OK"

    @staticmethod
    def left(degrees):
        HelloWorld.start_executing ("left : " + str(degrees))

        # Change sign
        if degrees > 0:
            degrees *= -1

        easygpg.turn_degrees(degrees)
        HelloWorld.stop_executing("left : " + str(degrees))
        return "OK"

    @staticmethod
    def right(degrees):
        HelloWorld.start_executing ("right : " + str(degrees))
        easygpg.turn_degrees(degrees)
        HelloWorld.stop_executing("right : " + str(degrees))
        return "OK"

    @staticmethod
    def servo(degrees):
        HelloWorld.start_executing ("servo : " + str(degrees))
        servo = easygpg.init_servo()
        servo.rotate_servo(degrees)
        HelloWorld.stop_executing("servoZ : " + str(degrees))
        return "OK"

    @staticmethod
    def reset():
        HelloWorld.start_executing ("reset")
        GPG.reset_all()
        HelloWorld.stop_executing("reset")

    @staticmethod
    def distance():
        HelloWorld.start_executing ("distance")
        stop_executing("distance : " + str(distance_sensor.read_mm()))
        return(str(distance_sensor.read_mm()))
        #return "10"    

    @staticmethod
    def power():
        HelloWorld.start_executing ("power")
        current_voltage = str(easygpg.volt())
        stop_executing("power : " + current_voltage)
        return(current_voltage)    
    
    @staticmethod
    def status():
        HelloWorld.start_executing ("status")
        return("OK")    
    
    
    def on_start(self, event):
        print("on start" + self.url)
        self.container = event.container
        self.conn = event.container.connect(self.url)
        self.receiver = event.container.create_receiver(self.conn, self.address)
        self.server = self.container.create_sender(self.conn, None)
        event.container.create_receiver(self.url)

    def on_link_opened(self, event):
        print("RECEIVE: Created receiver for source address '{0}'".format
              (self.url))  

    def on_message(self, event):
        print("Received message: " + event.message.body)

        #event.receiver.close()
        #event.connection.close()
        json_data = json.loads(event.message.body)

        operation = json_data['operation']
        print("Received operation: " + operation)

        if json_data.get('parameter'):
            parameter = json_data['parameter']
            print("Received parameter: " + parameter)              

        if 'forward' == str(operation):
            ret = HelloWorld.forward(parameter)
            
        elif 'backward' == str(operation):
            ret = HelloWorld.backward(parameter)

        elif 'left' == str(operation):
            ret = HelloWorld.left(parameter)

        elif 'right' == str(operation):
            ret = HelloWorld.right(parameter)

        elif 'servo' == str(operation):
            ret = HelloWorld.servo(parameter)

        elif 'distance' == str(operation):
            ret = HelloWorld.distance()

        elif 'power' == str(operation):
            ret = HelloWorld.power()                             
        
        elif 'status' == str(operation):
            ret = HelloWorld.status()                             
            
        else:
            print("operation {0} not implemented").format(operation)
            ret = ("operation {0} not implemented").format(operation)


        print("Answering: " + str(event.message.correlation_id))
        
        self.server.send(Message(address=event.message.reply_to, body=ret,
                            correlation_id=event.message.correlation_id))

        print("Answer sent" )                    

        #event.receiver.close()
        #event.connection.close()

    @staticmethod
    def start_executing(command):
        #easygpg.open_right_eye()
        print ("Start executing -> " + command)

    @staticmethod
    def stop_executing(command):
        print ("Stop executing -> " + command)
        #easygpg.close_right_eye()
      
parser = optparse.OptionParser(usage="usage: %prog [options]")
parser.add_option("-u", "--url", default="amqps://username:password@localhost:5672",
                  help="url to use for receiving messages")
parser.add_option("-a", "--address", default="myqueue",
                  help="url to use for receiving messages")                                  
opts, args = parser.parse_args()

try:
    Container(HelloWorld(opts.url,opts.address)).run()
except KeyboardInterrupt: pass
