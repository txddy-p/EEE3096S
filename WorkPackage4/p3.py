import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import threading
import datetime
import time

start = datetime.datetime.now()
btn_24 = 24
interval = 1
Tempt = None
Light = None
btn = None
cs = None

def setup():
   global Tempt
   global Light
   global cs
   global btn
   # create the spi bus
   spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
   # create the cs (chip select)
   cs = digitalio.DigitalInOut(board.D5)
   # create the mcp object
   mcp = MCP.MCP3008(spi, cs)
   #setup button
   btn = digitalio.DigitalInOut(board.D24)
   btn.switch_to_input(pull=digitalio.Pull.UP)
   btn.pull=digitalio.Pull.UP
   # create an analog input channel on pin 0
   Tempt = AnalogIn(mcp, MCP.P1)
   Light = AnalogIn(mcp, MCP.P2)


def temperature(TV):
   #returns the temperature in degrees
   t = TV-0.5
   t=t/0.01
   return t

def change():
   #used to change sampling interval
   global interval
   if interval==5:
      time.sleep(0.2)
      interval=10
      #time.sleep(0.02)
   elif interval==10:
      time.sleep(0.2)
      interval=1
      #time.sleep(0.02)
   elif interval==1:
      time.sleep(0.2)
      interval=5
      #time.sleep(0.02)

def data():
   """
   Function for printing out the data
   """
   global interval
   global cs
   global start
   thread = threading.Timer(interval, data)
   thread.daemon = True  # Daemon threads exit when the program does
   thread.start()
   tim= round((datetime.datetime.now()-start).total_seconds())
   print(str(tim)+"s \t\t"+str(Tempt.value)+"\t\t"+str(round(temperature(Tempt.voltage),2))+" C\t    "+str(Light.value))

def main():
    global btn
    print("Runtime\t\tTemp Reading \tTemp \t    Light Reading")
    setup()
    data()
    while True:
        if btn.value==False:
           #print("Button pressed")
           T = threading.Thread(target=change)
           T.start()
           T.join()
        pass

if __name__=='__main__':
    main()
