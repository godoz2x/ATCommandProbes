import sys
import time
import serial
import threading

if len(sys.argv) < 3:
	print "<filename> <cell-number> <timeout>"
	sys.exit()
cell = sys.argv[1]
timeout = int(sys.argv[2])
port = '/dev/ttyACM0'
baud = 9600
serial_port = serial.Serial(port, baud, timeout=0)

def read_from_port(ser):
    while 1:
        if ser.is_open == False:
            break
        if ser.is_open == True:
            try:
                res = ser.readline().encode()
            except:
                pass    
        if res != '':
            print res

rthread = threading.Thread(target=read_from_port, args=(serial_port,))
rthread.start()

serial_port.write(b'ATD+'+cell+';\r\n')
start_time = time.time()
timetaken = 0
while timetaken < timeout:
    timetaken = int(time.time() - start_time)		
    if timetaken == timeout:
        serial_port.close()
print "Exiting Main Thread"
sys.exit()        
