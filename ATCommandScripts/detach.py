import sys
import time
import serial
import datetime
import threading

if len(sys.argv) < 2:
	print "<filename> <timeout>"
	sys.exit()
timeout = int(sys.argv[1])
port = '/dev/ttyACM0'
baud = 9600
serial_port = serial.Serial(port, baud, timeout=0)

def read_from_port(ser):
    while 1:
        res = ''
        if ser.is_open == False:
            break
        if ser.is_open == True:
            try:
                res = res + ser.readline().encode().strip('\r\n')
            except:
                pass    
        if res != '':
            if 'AT+' in res:
                if '?' in res:
                    print res + " => CHECKING DEVICE STATUS\n" 
                elif '0' in res:
                    print res + " => SENDING DETACH REQUEST\n"
            else:
                if ':' in res:
                    print res + " => NETWORK RESPONSE (DEVICE STATE)\n"
                else:
                    print res + " => NETWORK RESPONSE\n"       

rthread = threading.Thread(target=read_from_port, args=(serial_port,))
rthread.start()
# serial_port.write(b'AT+CGEQMIN=?\r\n')
# time.sleep(timeout)
# serial_port.write(b'AT+CGATT=1;\r\n')
start_time = time.time()
while 1:
    try:
        serial_port.write(b'AT+CGATT?;\r\n')
        serial_port.write(b'AT+CGATT=0;\r\n')
        time.sleep(timeout)
    except KeyboardInterrupt:
        serial_port.close()
        break
timetaken = int(time.time() - start_time)
print " "
print "Exiting Main Thread"
print str(datetime.timedelta(seconds=(timetaken)))        
sys.exit()        
