# -*- coding: utf-8 -*-

#from __future__ import with_statement
import serial
import binascii


def hexToAscii(hexStr):
        asciiStr = ''
        for i in range(len(hexStr)/2):
                asciiStr +=  binascii.a2b_hex(hexStr[2*i] + hexStr[2*i+1])
        return asciiStr

def asciiToHex(asciiStr):
        hexStr = ''
        for i in range(len(asciiStr)):
                hexStr +=  hex(ord(asciiStr[i]))
        return hexStr


#Read Memory
com_read_memory = '2E483041360D'
com_read_manifold_temperature = '2E4937370D'
#com_set_stabilized_temp = '2E4D+223'
com_serial_watchdog = '2E5538330D'

asci_com_read_memory = hexToAscii(com_read_memory) # read set temperature
asci_com_read_manifold_temperature = hexToAscii(com_read_manifold_temperature) #read actual temperature
asci_com_serial_watchdog = hexToAscii(com_serial_watchdog)

TEMP_MIN = 160
TEMP_MAX = 300

#print 'TEMP_MAX =', TEMP_MAX
#print 'TEMP_MIN=', TEMP_MIN

# Opens the serial connection to the chiller with the correct settings
def open_chiller_port(comport):
        s = serial.Serial(comport,9600,bytesize=8,parity=serial.PARITY_NONE,stopbits=1,timeout = 0.6, xonxoff=1)
##        try:
##                s.close()
##                print 'serial port was still open, so I close it aforehand'
##        except:
##                pass
        return s

# Closes the serial connection
def close_chiller_port(serialPort):
        serialPort.close()
        

# Changes the set temperature of the chiller,
# numbers are given in tenths of degrees (200 = 20.0 deg C)
def setTemperature(serialPort, temp = 200):
        temp = int(temp)

        print temp, TEMP_MIN, TEMP_MAX
        
        if (temp>TEMP_MIN and temp < TEMP_MAX):
                
                temp10 = str(temp/100%10)
                temp1 = str(temp/10%10)
                temp01 =  str(temp%10)
                
                checksum_int =  (46 + 77 +  43 + ord(temp10) +  ord(temp1) +  ord(temp01))%256   # 46 is for 
                asci_com_set_temperature = '.M+' + str(temp)  + hex(checksum_int)[2:] + '\r'
                serialPort.write(asci_com_set_temperature)
                
        else:
                print 'Havent changed the temperature, because it is out of range, max: ',TEMP_MAX,' degree, min: ', TEMP_MIN,' degree'
                

# Returns actual (coolant) temperature in degree celcius,
# for instance:  22.40 (type = float)
def readCoolantTemperature(serialPort):
        serialPort.write(asci_com_read_manifold_temperature)
        #time.sleep(0.3)
        answer = serialPort.readline()
#        print answer[3:8]
        
        try:
                temp = float(answer[3:8])/100.
                if not (temp>TEMP_MIN/10. and temp < TEMP_MAX/10.):
                        print 'WARNuNG: Got chiller coolant temperature of: ',temp, 'min is  ',TEMP_MIN, 'and max is ',TEMP_MAX
                return temp
        except:
                print 'could not read actual temperature'
                return -1

        

# Returns set temperature in 10th of degree celcius,
# for instace:  224 (type = int)
def readSetTemperature(serialPort):
        serialPort.write(asci_com_read_memory)
        answer = serialPort.readline()
        #print answer
        #print answer[4:8]
        try:
                temp = int(answer[4:8])
                if not (temp>TEMP_MIN and temp < TEMP_MAX):
                        print 'WARNUNG: in readSetTemperature: Got chiller set temperature of: ',temp, 'min is  ',TEMP_MIN, 'and max is ',TEMP_MAX
                return temp
        except:
                print 'could not read set temperature'
                return -1


# Checks if the chiller is on, running and not errors - if not it
# prints a warning and returns -1
def readChillerStatus(serialPort, print_statues = True, print_chiller_working_Fine = False):
        success = 0
        while not success:
                serialPort.write(asci_com_serial_watchdog)
                answer = serialPort.readline()
                if answer == '':
                        print 'failed'
                        success = 1
                else:
                        #print answer
                        success = 1
                
                   
        try:
                chiller_status = int(answer[3]) # 0 = auto_start, 1 = standby, 2= chiller run, 3 = safety default
                alarm_status = int(answer[4]) # 0 = no alamrs, 1 = Alarm on
                chiller_status2 = int(answer[5]) # 0 = off, 1 = on
                dryer_status = int(answer[6]) # 0 = dryer off, 1 = dryer on
                
                if print_statues:
                        print 'chiller_status=',chiller_status, ' alarm_status=', alarm_status, ' chiller_status2=',chiller_status2 
                
                if chiller_status == 2 and alarm_status == 0 and chiller_status2 == 1:
                        if print_chiller_working_Fine:
                                print 'chiller working fine'
                else:
                        print "WARNING: check chiller!"
                return 0
        except:
                print "WARNING, could not determine chiller status"
                return -1
        




if __name__ == "__main__":

    import time
    s = open_chiller_port(4)

        #s = serial.Serial(3,9600,bytesize=8,parity=serial.PARITY_NONE,stopbits=1,timeout = 0.6, xonxoff=1)
#        s.write('.G0A5\r') # Sets chiller to standby
#        s.write('.G1A6\r') # Sets chiller on run
    print "Old junk:" , s.readlines()
        
    #setTemperature(serialPort = s, temp = 200)
    status = readChillerStatus(serialPort = s)
    realtemp = readCoolantTemperature(serialPort = s)
    settemp = readSetTemperature(serialPort = s)
    print 'status',status
    print 'actual temp',realtemp
    print 'set temp.',settemp
    print "Trying to set temperature to 18 degrees"
    setTemperature(s,180)
    print 'set temp.', settemp

    close_chiller_port(s)



