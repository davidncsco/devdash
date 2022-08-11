from fastapi import Request,FastAPI
from uvicorn import run
from Motor import *
from Buzzer import *
import time,socket

WEIGHTBASEUNIT = 0.5 # Tune from command line option "-u"
WEIGHTMIN = 1
WEIGHTMAX = 20
SPEEDSTD  = 1000
SPEEDMIN  = 0
SPEEDMAX  = 4000

class RaceCar:
    def __init__(self):
        self.buzzer = Buzzer()
        self.motor  = Motor()
        self.speed  = 1000
        self.duration = 1.0
	
    def calibrate(self, speed, weight):
        self.speed = speed
        self.duration = weight * WEIGHTBASEUNIT
        if speed < SPEEDMIN or speed > SPEEDMAX :
            self.speed = SPEEDSTD
        if weight < WEIGHTMIN or weight > WEIGHTMAX :
            self.duration = WEIGHTBASEUNIT

    def moveForward(self):
        print('Moving forward: speed ' + str(self.speed) + ' duration ' + str(self.duration))
        self.motor.setMotorModel(self.speed, self.speed, self.speed, self.speed)
        time.sleep(self.duration)
        self.stop()	
	
    def moveBackward(self, weight):
        print('Moving backward: speed ' + str(self.speed) + ' weight ' + str(weight))
        self.motor.setMotorModel(-self.speed, -self.speed, -self.speed, -self.speed)
        self.buzzer.beep(weight)
        self.stop()
    
    def stop(self):
        self.motor.setMotorModel(0,0,0,0)

""" REST API server, taking instruction from API request """
mycar = RaceCar() 
app   = FastAPI()

# Quick test to see if web server is running
@app.get("/")
async def read_root():
    return { 'Happy' : 'Racing' }

# POSt request handler
@app.post("/forward")
async def move_forward(speed: int, weight: int):
    global mycar
    mycar.calibrate(speed,weight)
    mycar.moveForward()
    
@app.post("/backward")
async def move_backward(speed: int, weight: int):
    global mycar
    mycar.calibrate(speed,weight)
    mycar.moveBackward(weight)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255",1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP

if __name__ == '__main__':
    host = get_ip()
    port = 8888
    #Start server
    try:
        run("car:app",host=host,port=port)
    except:
        print ("Something went wrong, cannot setup server, maybe check network, host IP or port number?")
    
