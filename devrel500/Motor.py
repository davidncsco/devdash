import time
from PCA9685 import PCA9685
import random

class Motor:

    def __init__(self, tail=None):
        self.pwm = PCA9685(0x40, debug=True)
        self.pwm.setPWMFreq(50)
        
    def duty_range(self, duty1, duty2, duty3, duty4):
        if duty1 > 4095:
            duty1 = 4095
        elif duty1 < -4095:
            duty1 = -4095        
        
        if duty2 > 4095:
            duty2 = 4095
        elif duty2 < -4095:
            duty2 = -4095
            
        if duty3 > 4095:
            duty3 = 4095
        elif duty3 < -4095:
            duty3 = -4095
            
        if duty4 > 4095:
            duty4 = 4095
        elif duty4 < -4095:
            duty4 = -4095
        return duty1, duty2, duty3, duty4
        
    def left_Upper_Wheel(self, duty):
        if duty > 0:
            self.pwm.setMotorPwm(0, 0)
            self.pwm.setMotorPwm(1, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(1, 0)
            self.pwm.setMotorPwm(0, abs(duty))
        else:
            self.pwm.setMotorPwm(0, 4095)
            self.pwm.setMotorPwm(1, 4095)

    def left_Lower_Wheel(self, duty):
        if duty > 0:
            self.pwm.setMotorPwm(3, 0)
            self.pwm.setMotorPwm(2, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(2, 0)
            self.pwm.setMotorPwm(3, abs(duty))
        else:
            self.pwm.setMotorPwm(2, 4095)
            self.pwm.setMotorPwm(3, 4095)

    def right_Upper_Wheel(self, duty):
        if duty > 0:
            self.pwm.setMotorPwm(6, 0)
            self.pwm.setMotorPwm(7, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(7, 0)
            self.pwm.setMotorPwm(6, abs(duty))
        else:
            self.pwm.setMotorPwm(6, 4095)
            self.pwm.setMotorPwm(7, 4095)

    def right_Lower_Wheel(self, duty):
        if duty > 0:
            self.pwm.setMotorPwm(4, 0)
            self.pwm.setMotorPwm(5, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(5, 0)
            self.pwm.setMotorPwm(4, abs(duty))
        else:
            self.pwm.setMotorPwm(4, 4095)
            self.pwm.setMotorPwm(5, 4095)
            
    def stopMotor(self):
        self.setMotorModel(0, 0, 0, 0)
        
    def fastForward(self):
        self.setMotorModel(1500, 1500, 1500, 1500)
    
    def slowForward(self):
        self.setMotorModel(750, 750, 750, 750)

    def forward(self,speed=1000,duration=1):
        self.setMotorModel(speed, speed, speed, speed)
        if(duration > 0):
            time.sleep(duration*0.5)
            self.setMotorModel(0,0,0,0)
    
    def turnLeft(self):
        self.setMotorModel(-2400, -2400, 2400, 2400)

    def turnRight(self):
        self.setMotorModel(2400, 2400, -2400, -2400)
        
    def slightRight(self,duty):
        offset = int(duty * 0.6)
        self.setMotorModel(duty, duty, -offset, -offset)
        time.sleep(0.5)
        self.setMotorModel(0,0,0,0)
        
    def slightLeft(self,duty):
        offset = int(duty*0.6)
        self.setMotorModel(-offset, -offset, duty, duty)
        time.sleep(0.5)
        self.setMotorModel(0,0,0,0)
        
    def spin(self):
        self.setMotorModel(-1200, -1200, 3000, 3000)
    
    def backup(self):
        self.setMotorModel(-1000, -1000, -1000, -1000)
 
    def slowBackup(self):
        self.setMotorModel(-750, -750, -750, -750)

    def setMotorModel(self, duty1, duty2, duty3, duty4):
        duty1, duty2, duty3, duty4 = self.duty_range(duty1, duty2, duty3, duty4)
        print('Calling setMotorModel ',duty1,duty2,duty3,duty4)
        self.left_Upper_Wheel(-duty1)
        self.left_Lower_Wheel(-duty2)
        self.right_Upper_Wheel(-duty3)
        self.right_Lower_Wheel(-duty4)
            
PWM = Motor()          

def destroy():
    PWM.setMotorModel(0, 0, 0, 0)                   

# Should run this on every newly assembled car to make sure all the wheels are functional
if __name__ == '__main__':
    try:
        while True:
            random.seed()
            speed = random.randint(-4000, 4000)
            print("Speed: ",speed)
            print('Checking left_Lower_Wheel...')
            PWM.left_Lower_Wheel(speed)
            time.sleep(1)
            PWM.stopMotor()
            print('Checking right_Lower_Wheel...')
            PWM.right_Lower_Wheel(speed)
            time.sleep(1)
            PWM.stopMotor()
            print('Checking left_Upper_Wheel...')
            PWM.left_Upper_Wheel(speed)
            time.sleep(1)
            PWM.stopMotor()
            print('Checking right_Upper_Wheel...')
            PWM.right_Upper_Wheel(speed)
            time.sleep(1)
            PWM.stopMotor()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
