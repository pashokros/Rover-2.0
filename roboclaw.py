# import serial
# import serial_emul
import struct

class Roboclaw:
    def __init__(self, port=0):
        ttyStr = '/dev/ttyACM' + str(port)
        self.usb = serial.Serial(ttyStr)
        # self.usb = serial_emul.Serial(ttyStr)
        self.checksum = 0
        
    def sendcommand(self,address,command):
        self.checksum = address
        self.usb.write(chr(address))
        self.checksum += command
        self.usb.write(chr(command))
        return

    def readbyte(self):
        val = struct.unpack('>B',self.usb.read(1))
        self.checksum += val[0]
        return val[0]
    def readsbyte(self):
        val = struct.unpack('>b',self.usb.read(1))
        self.checksum += val[0]
        return val[0]
    def readword(self):
        val = struct.unpack('>H',self.usb.read(2))
        self.checksum += (val[0]&0xFF)
        self.checksum += (val[0]>>8)&0xFF
        return val[0]
    def readsword(self):
        val = struct.unpack('>h',self.usb.read(2))
        self.checksum += val[0]
        self.checksum += (val[0]>>8)&0xFF
        return val[0]
    def readlong(self):
        val = struct.unpack('>L',self.usb.read(4))
        self.checksum += val[0]
        self.checksum += (val[0]>>8)&0xFF
        self.checksum += (val[0]>>16)&0xFF
        self.checksum += (val[0]>>24)&0xFF
        return val[0]
    def readslong(self):
        val = struct.unpack('>l',self.usb.read(4))
        self.checksum += val[0]
        self.checksum += (val[0]>>8)&0xFF
        self.checksum += (val[0]>>16)&0xFF
        self.checksum += (val[0]>>24)&0xFF
        return val[0]

    def writebyte(self,val):
        self.checksum += val
        return self.usb.write(struct.pack('>B',val))
    def writesbyte(self,val):
        self.checksum += val
        return self.usb.write(struct.pack('>b',val))
    def writeword(self,val):
        self.checksum += val
        self.checksum += (val>>8)&0xFF
        return self.usb.write(struct.pack('>H',val))
    def writesword(self,val):
        self.checksum += val
        self.checksum += (val>>8)&0xFF
        return self.usb.write(struct.pack('>h',val))
    def writelong(self,val):
        self.checksum += val
        self.checksum += (val>>8)&0xFF
        self.checksum += (val>>16)&0xFF
        self.checksum += (val>>24)&0xFF
        return self.usb.write(struct.pack('>L',val))
    def writeslong(self,val):
        self.checksum += val
        self.checksum += (val>>8)&0xFF
        self.checksum += (val>>16)&0xFF
        self.checksum += (val>>24)&0xFF
        return self.usb.write(struct.pack('>l',val))

    def MForward(self,i,val):
        comm = [0, 4]
        self.sendcommand(128, comm[i - 1])
        self.writebyte(val)
        self.writebyte(self.checksum&0x7F)
        return

    def MBackward(self,i,val):
        comm = [1, 5]
        self.sendcommand(128, comm[i - 1])
        self.writebyte(val)
        self.writebyte(self.checksum&0x7F)
        return

    def SetMinMainBattery(self,val):
        self.sendcommand(128,2)
        self.writebyte(val)
        self.writebyte(self.checksum&0x7F)
        return

    def SetMaxMainBattery(self,val):
        self.sendcommand(128,3)
        self.writebyte(val)
        self.writebyte(self.checksum&0x7F)
        return

    def DriveM1(self,i,val):
        comm = [6, 7]
        self.sendcommand(128, comm[i - 1])
        self.writebyte(val)
        self.writebyte(self.checksum&0x7F)
        return

    def ForwardMixed(self,val):
        self.sendcommand(128,8)
        self.writebyte(val)
        self.writebyte(self.checksum&0x7F)
        return

    def BackwardMixed(self,val):
        self.sendcommand(128,9)
        self.writebyte(val)
        self.writebyte(self.checksum&0x7F)
        return

    def RightMixed(self,val):
        self.sendcommand(128,10)
        self.writebyte(val)
        self.writebyte(self.checksum&0x7F)
        return

    def LeftMixed(self,val):
        self.sendcommand(128,11)
        self.writebyte(val)
        self.writebyte(self.checksum&0x7F)
        return

    def DriveMixed(self,val):
        self.sendcommand(128,12)
        self.writebyte(val)
        self.writebyte(self.checksum&0x7F)
        return

    def TurnMixed(self,val):
        self.sendcommand(128,13)
        self.writebyte(val)
        self.writebyte(self.checksum&0x7F)
        return

    def readMencoder(self, i):
        comm = [16, 17]
        self.sendcommand(128, comm[i - 1])
        enc = self.readslong()
        status = self.readbyte()
        crc = self.checksum&0x7F
        if crc==self.readbyte()&0x7F:
            return (enc,status)
        return (-1,-1)

    def readMspeed(self, i):
        comm = [18, 19]
        self.sendcommand(128, comm[i - 1])
        enc = self.readslong()
        status = self.readbyte()
        crc = self.checksum&0x7F
        if crc==self.readbyte()&0x7F:
            return (enc,status)
        return (-1,-1)

    def ResetEncoderCnts(self):
        self.sendcommand(128,20)
        self.writebyte(self.checksum&0x7F)
        return

    def readversion(self):
        self.sendcommand(128,21)
        return self.usb.read(32)

    def readmainbattery(self):
        self.sendcommand(128,24)
        val = self.readword()
        crc = self.checksum&0x7F
        if crc==self.readbyte()&0x7F:
            return val
        return -1

    def readlogicbattery(self):
        self.sendcommand(128,25)
        val = self.readword()
        crc = self.checksum&0x7F
        if crc==self.readbyte()&0x7F:
            return val
        return -1

    def SetMpidq(self,num,p,i,d,qpps):
        comm = [28, 29]
        self.sendcommand(128, comm[num - 1])
        self.writelong(d)
        self.writelong(p)
        self.writelong(i)
        self.writelong(qpps)
        self.writebyte(self.checksum&0x7F)
        return

    def readMinstspeed(self,i):
        comm = [30, 31]
        self.sendcommand(128, comm[i - 1])
        enc = self.readslong()
        status = self.readbyte()
        crc = self.checksum&0x7F
        if crc==self.readbyte()&0x7F:
            return (enc,status)
        return (-1,-1)

    def SetMDuty(self,i,val):
        comm = [32, 33]
        self.sendcommand(128, comm[i - 1])
        self.writesword(val)
        self.writebyte(self.checksum&0x7F)
        return

    def SetMixedDuty(self,m1,m2):
        self.sendcommand(128,34)
        self.writesword(m1)
        self.writesword(m2)
        self.writebyte(self.checksum&0x7F)
        return

    def SetMSpeed(self,i,val):
        comm = [35, 36]
        self.sendcommand(128, comm[i - 1])
        self.writeslong(val)
        self.writebyte(self.checksum&0x7F)
        return

    def SetMixedSpeed(self,m1,m2):
        self.sendcommand(128,37)
        self.writeslong(m1)
        self.writeslong(m2)
        self.writebyte(self.checksum&0x7F)
        return

    def SetMSpeedAccel(self,i,accel,speed):
        comm = [38, 39]
        self.sendcommand(128, comm[i - 1])
        self.writelong(accel)
        self.writeslong(speed)
        self.writebyte(self.checksum&0x7F)
        return

    def SetMixedSpeedAccel(self,accel,speed1,speed2):
        self.sendcommand(128,40)
        self.writelong(accel)
        self.writeslong(speed1)
        self.writeslong(speed2)
        self.writebyte(self.checksum&0x7F)
        return

    def SetMSpeedDistance(self,i,speed,distance,buffer):
        comm = [41, 42]
        self.sendcommand(128, comm[i - 1])
        self.writeslong(speed)
        self.writelong(distance)
        self.writebyte(buffer)
        self.writebyte(self.checksum&0x7F)
        return

    def SetMixedSpeedDistance(self,speed1,distance1,speed2,distance2,buffer):
        self.sendcommand(128,43)
        self.writeslong(speed1)
        self.writelong(distance1)
        self.writeslong(speed2)
        self.writelong(distance2)
        self.writebyte(buffer)
        self.writebyte(self.checksum&0x7F)
        return

    def SetMSpeedAccelDistance(self,i,accel,speed,distance,buffer):
        comm = [44, 45]
        self.sendcommand(128, comm[i - 1])
        self.writelong(accel)
        self.writeslong(speed)
        self.writelong(distance)
        self.writebyte(buffer)
        self.writebyte(self.checksum&0x7F)
        return

    def SetMixedSpeedAccelDistance(self,accel,speed1,distance1,speed2,distance2,buffer):
        self.sendcommand(128,46)
        self.writelong(accel)
        self.writeslong(speed1)
        self.writelong(distance1)
        self.writeslong(speed2)
        self.writelong(distance2)
        self.writebyte(buffer)
        self.writebyte(self.checksum&0x7F)
        return

    def readbuffercnts(self):
        self.sendcommand(128,47)
        buffer1 = self.readbyte()
        buffer2 = self.readbyte()
        crc = self.checksum&0x7F
        if crc==self.readbyte()&0x7F:
            return (buffer1,buffer2)
        return (-1,-1)

    def readcurrents(self):
        self.sendcommand(128,49)
        motor1 = self.readword()
        motor2 = self.readword()
        crc = self.checksum&0x7F
        if crc==self.readbyte()&0x7F:
            return (motor1,motor2)
        return (-1,-1)

    def SetMixedSpeedIAccel(self,accel1,speed1,accel2,speed2):
        self.sendcommand(128,50)
        self.writelong(accel1)
        self.writeslong(speed1)
        self.writelong(accel2)
        self.writeslong(speed2)
        self.writebyte(self.checksum&0x7F)
        return

    def SetMixedSpeedIAccelDistance(self,accel1,speed1,distance1,accel2,speed2,distance2,buffer):
        self.sendcommand(128,51)
        self.writelong(accel1)
        self.writeslong(speed1)
        self.writelong(distance1)
        self.writelong(accel2)
        self.writeslong(speed2)
        self.writelong(distance2)
        self.writebyte(buffer)
        self.writebyte(self.checksum&0x7F)
        return

    def SetMDutyAccel(self,i,accel,duty):
        comm = [52, 53]
        self.sendcommand(128, comm[i - 1])
        self.writesword(duty)
        self.writeword(accel)
        self.writebyte(self.checksum&0x7F)
        return

    def SetMixedDutyAccel(self,accel1,duty1,accel2,duty2):
        self.sendcommand(128,54)
        self.writesword(duty1)
        self.writeword(accel1)
        self.writesword(duty2)
        self.writeword(accel2)
        self.writebyte(self.checksum&0x7F)
        return

    def readMpidq(self, num):
        comm = [55, 56]
        self.sendcommand(128, comm[num - 1])
        p = self.readlong()
        i = self.readlong()
        d = self.readlong()
        qpps = self.readlong()
        crc = self.checksum&0x7F
        if crc==self.readbyte()&0x7F:
            return (p,i,d,qpps)
        return (-1,-1,-1,-1)

    def readmainbatterysettings(self):
        self.sendcommand(128,59)
        min = self.readword()
        max = self.readword()
        crc = self.checksum&0x7F
        if crc==self.readbyte()&0x7F:
            return (min,max)
        return (-1,-1)

    def readlogicbatterysettings(self):
        self.sendcommand(128,60)
        min = self.readword()
        max = self.readword()
        crc = self.checksum&0x7F
        if crc==self.readbyte()&0x7F:
            return (min,max)
        return (-1,-1)

    def SetMPositionConstants(self,i,kp,ki,kd,kimax,deadzone,min,max):
        comm = [61, 62]
        self.sendcommand(128, comm[i - 1])
        self.writelong(kd)
        self.writelong(kp)
        self.writelong(ki)
        self.writelong(kimax)
        self.writelong(deadzone)
        self.writelong(min)
        self.writelong(max)
        self.writebyte(self.checksum&0x7F)
        return

    def readMPositionConstants(self,num):
        comm = [63, 64]
        self.sendcommand(128, comm[num - 1])
        p = self.readlong()
        i = self.readlong()
        d = self.readlong()
        imax = self.readlong()
        deadzone = self.readlong()
        min = self.readlong()
        max = self.readlong()
        crc = self.checksum&0x7F
        if crc==self.readbyte()&0x7F:
            return (p,i,d,imax,deadzone,min,max)
        return (-1,-1,-1,-1,-1,-1,-1)

    def SetMSpeedAccelDeccelPosition(self,i,accel,speed,deccel,position,buffer):
        comm = [65, 66]
        self.sendcommand(128, comm[i - 1])
        self.writelong(accel)
        self.writelong(speed)
        self.writelong(deccel)
        self.writelong(position)
        self.writebyte(buffer)
        self.writebyte(self.checksum&0x7F)
        return

    def SetMixedSpeedAccelDeccelPosition(self,accel1,speed1,deccel1,position1,accel2,speed2,deccel2,position2,buffer):
        self.sendcommand(128,67)
        self.writelong(accel1)
        self.writelong(speed1)
        self.writelong(deccel1)
        self.writelong(position1)
        self.writelong(accel2)
        self.writelong(speed2)
        self.writelong(deccel2)
        self.writelong(position2)
        self.writebyte(buffer)
        self.writebyte(self.checksum&0x7F)
        return

    def readtemperature(self):
        self.sendcommand(128,82)
        val = self.readword()
        crc = self.checksum&0x7F
        if crc==self.readbyte()&0x7F:
            return val
        return -1

    def readerrorstate(self):
        self.sendcommand(128,90)
        val = self.readword()
        crc = self.checksum&0x7F
        if crc==self.readbyte()&0x7F:
            return val
        return -1