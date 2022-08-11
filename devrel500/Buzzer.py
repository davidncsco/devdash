import time
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
Buzzer_Pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(Buzzer_Pin,GPIO.OUT)

WEIGHTBASEUNIT = 0.5

class Buzzer:
    def run(self,command):
        if command!="0":
            GPIO.output(Buzzer_Pin,True)
        else:
            GPIO.output(Buzzer_Pin,False)
    def beep(self,sec):
        count=0
        while count<sec:
            GPIO.output(Buzzer_Pin,True)
            time.sleep(WEIGHTBASEUNIT*0.5)
            GPIO.output(Buzzer_Pin,False)
            time.sleep(WEIGHTBASEUNIT*0.5)
            count=count+1 

if __name__=='__main__':
    B=Buzzer()
    print('Beep 1')
    B.beep(1)
    time.sleep(3)
    print('Beep 5')
    B.beep(5)
    time.sleep(3)
    B.run("0")