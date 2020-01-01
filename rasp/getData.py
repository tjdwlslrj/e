import smbus
import math, struct, array, time, io, fcntl
import Adafruit_DHT as dht
import serial, struct, csv, os, time
from time import sleep

COM_PORT = '/dev/ttyUSB0'

PMS7003_FRAME_LENGTH = 0
PMS7003_PM1P0 = 1
PMS7003_PM2P5 = 2
PMS7003_PM10P0 = 3
PMS7003_PM1P0_ATM = 4
PMS7003_PM2P5_ATM = 5
PMS7003_PM10P0_ATM = 6
PMS7003_PCNT_0P3 = 7
PMS7003_PCNT_0P5 = 8
PMS7003_PCNT_1P0 = 9
PMS7003_PCNT_2P5 = 10
PMS7003_PCNT_5P0 = 11
PMS7003_PCNT_10P0 = 12
PMS7003_VER = 13
PMS7003_ERR_CODE = 14
PMS7003_CHECK_CODE = 15

bus = 1
addressT6713 = 0x15
I2C_SLAVE=0x0703

class i2c(object):
    def __init__(self, device, bus):

        self.fr = io.open("/dev/i2c-"+str(bus), "rb", buffering=0)
        self.fw = io.open("/dev/i2c-"+str(bus), "wb", buffering=0)

        # set device address
        fcntl.ioctl(self.fr, I2C_SLAVE, device)
        fcntl.ioctl(self.fw, I2C_SLAVE, device)

    def write(self, bytes):
        try:
            self.fw.write(bytes)
        except OSError:
            print("")
        except IOError:
            print("")

    def read(self, bytes):
        try:
            return self.fr.read(bytes)
        except OSError:
            print("")
        except IOError:
            print("")

    def close(self):
        self.fw.close()
        self.fr.close()

class T6713(object):
    def __init__(self):
        self.dev = i2c(addressT6713, bus)

    def gasPPM(self):
        buffer = array.array('B', [0x04, 0x13, 0x8b, 0x00, 0x01])
        self.dev.write(buffer)
        time.sleep(0.1)
        data = self.dev.read(4)
        try:
            buffer = array.array('B', data)
        except TypeError:
            print("")
        return buffer[2]*256+buffer[3]


while True:
    h,t = dht.read_retry(dht.DHT22, 4)
    now = time.localtime()
    ser = serial.Serial(COM_PORT, 9600, timeout=0.1)
    while True:
        c = ser.read(1)
        if len(c) >= 1:
            if ord(c[0]) == 0x42:
                c = ser.read(1)
                if len(c) >= 1:
                    if ord(c[0]) == 0x4d:
                        break;

    buff = ser.read(30)
    check = 0x42 + 0x4d
    check += ord(buff[0:1])
    pms7003_data = struct.unpack('!HHHHHHHHHHHHHBBH', buff)

    i = 0
    average = 0
    while i < 60:
        obj = T6713()
        a=obj.gasPPM()
        print(a)
        print(i)
        if(a>10000):
            print("")
        elif(a==0):
            print("")
        else:
            if(average == 0):
                average = a
            else:
                #print("average = ", average)
                #print("small!! ", a)
                average = int((average+a)/2)
                #print("average = ", average)
                #print("")
        i = i + 1
        time.sleep(5)

    print ('\n [%02d.%02d.%02d %02d:%02d:%02d]' 
            %(now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
    print (' ---------------------------')
    print ('  Temperature [*C]   = %.1f' %t) 
    print ('  Humidity    ['+'%'+']    = %.1f' %h)
    print ('  CO2         [PPM]    = %d' %average)
    print (' ---------------------------')
    print ('  PM 1.0 [up/m^3]    =', str(pms7003_data[PMS7003_PM1P0]))
    print ('  PM 2.5 [ug/m^3]    =', str(pms7003_data[PMS7003_PM2P5]))
    print ('  PM 10  [ug/m^3]    =', str(pms7003_data[PMS7003_PM10P0]))
    print (' ---------------------------\n')
    
    data=['g','%.1f'%t,'%.1f'%h, str(pms7003_data[PMS7003_PM1P0]),
                         str(pms7003_data[PMS7003_PM2P5]), str(pms7003_data[PMS7003_PM10P0]),
                         '%02d.%02d.%02d'%(now.tm_year, now.tm_mon, now.tm_mday),
                         '%02d:%02d:%02d' %(now.tm_hour, now.tm_min, now.tm_sec),'%d'%average]
    
    if not os.path.isfile('data/%02d_%02d_%02d.csv'%(now.tm_year, now.tm_mon, now.tm_mday)):
        f = open('data/%02d_%02d_%02d.csv'%(now.tm_year, now.tm_mon, now.tm_mday), 'w')
        csv_writer = csv.writer(f)
        csv_writer.writerow(['name','temperature', 'humidity', 'PM1.0', 'PM2.5', 'PM10', 'date', 'time', 'CO2'])
        f.close()
        
    f = open('data/%02d_%02d_%02d.csv'%(now.tm_year, now.tm_mon, now.tm_mday), 'a')
    csv_writer = csv.writer(f)
    csv_writer.writerow(data)
    
    print(data)
    sleep(300)

