#!/usr/bin/python
import time
import requests
import schedule
import ctypes
import smbus

#api_url = 'https://server.timsanalytics.com/api/v1/raspberry/test'
api_url = 'http://192.168.0.17:5000/api/v1/raspberry/test'

#i2c address
LPS22HB_I2C_ADDRESS       =  0x5C
#
LPS_ID                =  0xB1
#Register
LPS_INT_CFG           =  0x0B        #Interrupt register
LPS_THS_P_L           =  0x0C        #Pressure threshold registers
LPS_THS_P_H           =  0x0D
LPS_WHO_AM_I          =  0x0F        #Who am I
LPS_CTRL_REG1         =  0x10        #Control registers
LPS_CTRL_REG2         =  0x11
LPS_CTRL_REG3         =  0x12
LPS_FIFO_CTRL         =  0x14        #FIFO configuration register
LPS_REF_P_XL          =  0x15        #Reference pressure registers
LPS_REF_P_L           =  0x16
LPS_REF_P_H           =  0x17
LPS_RPDS_L            =  0x18        #Pressure offset registers
LPS_RPDS_H            =  0x19
LPS_RES_CONF          =  0x1A        #Resolution register
LPS_INT_SOURCE        =  0x25        #Interrupt register
LPS_FIFO_STATUS       =  0x26        #FIFO status register
LPS_STATUS            =  0x27        #Status register
LPS_PRESS_OUT_XL      =  0x28        #Pressure output registers
LPS_PRESS_OUT_L       =  0x29
LPS_PRESS_OUT_H       =  0x2A
LPS_TEMP_OUT_L        =  0x2B        #Temperature output registers
LPS_TEMP_OUT_H        =  0x2C
LPS_RES               =  0x33        #Filter reset register

class LPS22HB(object):
    def __init__(self,address=LPS22HB_I2C_ADDRESS):
        self._address = address
        self._bus = smbus.SMBus(1)
        self.LPS22HB_RESET()                         #Wait for reset to complete
        self._write_byte(LPS_CTRL_REG1 ,0x02)        #Low-pass filter disabled , output registers not updated until MSB and LSB have been read , Enable Block Data Update , Set Output Data Rate to 0
    def LPS22HB_RESET(self):
        Buf=self._read_u16(LPS_CTRL_REG2)
        Buf|=0x04
        self._write_byte(LPS_CTRL_REG2,Buf)               #SWRESET Set 1
        while Buf:
            Buf=self._read_u16(LPS_CTRL_REG2)
            Buf&=0x04
    def LPS22HB_START_ONESHOT(self):
        Buf=self._read_u16(LPS_CTRL_REG2)
        Buf|=0x01                                         #ONE_SHOT Set 1
        self._write_byte(LPS_CTRL_REG2,Buf)
    def _read_byte(self,cmd):
        return self._bus.read_byte_data(self._address,cmd)
    def _read_u16(self,cmd):
        LSB = self._bus.read_byte_data(self._address,cmd)
        MSB = self._bus.read_byte_data(self._address,cmd+1)
        return (MSB     << 8) + LSB
    def _write_byte(self,cmd,val):
        self._bus.write_byte_data(self._address,cmd,val)

class SHTC3:
    def __init__(self):
        self.dll = ctypes.CDLL("./SHTC3.so")
        init = self.dll.init
        init.restype = ctypes.c_int
        init.argtypes = [ctypes.c_void_p]
        init(None)

    def SHTC3_Read_Temperature(self):
        temperature = self.dll.SHTC3_Read_TH
        temperature.restype = ctypes.c_float
        temperature.argtypes = [ctypes.c_void_p]
        return temperature(None)

    def SHTC3_Read_Humidity(self):
        humidity = self.dll.SHTC3_Read_RH
        humidity.restype = ctypes.c_float
        humidity.argtypes = [ctypes.c_void_p]
        return humidity(None)

def get_data():

    # SHTC3 HUMIDITY SENSOR DATA
    temperature = shtc3.SHTC3_Read_Temperature()
    humidity = shtc3.SHTC3_Read_Humidity()

    # LPS22HB NANO PRESSURE SENSOR DATA
    # Note: The temperature detection of the air pressure sensor is only used as compensation.
    # For accurate temperature detection, please use the SHTC3 temperature value.
    lps22hb.LPS22HB_START_ONESHOT()

    if (lps22hb._read_byte(LPS_STATUS)&0x01)==0x01:  # a new pressure data is generated
        u8Buf[0]=lps22hb._read_byte(LPS_PRESS_OUT_XL)
        u8Buf[1]=lps22hb._read_byte(LPS_PRESS_OUT_L)
        u8Buf[2]=lps22hb._read_byte(LPS_PRESS_OUT_H)
        pressure=((u8Buf[2]<<16)+(u8Buf[1]<<8)+u8Buf[0])/4096.0

    if (lps22hb._read_byte(LPS_STATUS)&0x02)==0x02:   # a new pressure data is generated
        u8Buf[0]=lps22hb._read_byte(LPS_TEMP_OUT_L)
        u8Buf[1]=lps22hb._read_byte(LPS_TEMP_OUT_H)
        TEMP_DATA=((u8Buf[1]<<8)+u8Buf[0])/100.0
    
    
    print('Temperature = %6.2f°C, Humidity = %6.2f%%, Pressure: %6.2f hPa' % (temperature, humidity, pressure))
    headers = {'Content-type': 'application/json'}

    millis = int(round(time.time() * 1000))
    post_object = {'device': 'colby', 'key': 'temperature', 'value': temperature, 'timestamp': millis}
    response = requests.post(api_url, headers=headers, json=post_object, verify=True)
    print(response.text)

    millis = int(round(time.time() * 1000))
    post_object = {'device': 'colby', 'key': 'humidity', 'value': humidity, 'timestamp': millis}
    response = requests.post(api_url, headers=headers, json=post_object, verify=True)
    print(response.text)
    
    millis = int(round(time.time() * 1000))
    post_object = {'device': 'colby', 'key': 'pressure', 'value': pressure, 'timestamp': millis}
    response = requests.post(api_url, headers=headers, json=post_object, verify=True)
    print(response.text)

print("Running sensor...")
get_data()  
schedule.every(1).hours.do(get_data)
lps22hb=LPS22HB()
u8Buf=[0,0,0]
shtc3 = SHTC3()
pressure = 0.0
TEMP_DATA = 0.0
while True:
    schedule.run_pending()
