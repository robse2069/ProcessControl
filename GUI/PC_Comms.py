import os
import can

#rename to CAN_Comms
class PC_Message:
    def __init__(self,ID,setV,value,name=""):
        self.name=name
        self.MSGID = ID
        self.setValue = setV
        self.value = value


class PC_Comms:
#    def __init__(self,Controls,Measurements,type="CAN"):
    def __init__(self,Controls,Measurements,type="loopback"):
        self.commstype=type

#        self.name=name
#        self.setValue=setValue
#        self.value=value
#        self.min=minValue
#        self.max = maxValue
#        self.unit=unit
#        self.ID=MsgID
#        self.type=type  #can be: button, slider, number, string



        self.Messages=[]
        for control in Controls:
            self.Messages.append(PC_Message(control.name,control.ID,control.setValue,control.value))
        for meas in Measurements:
            self.Messages.append(PC_Message(meas.name,meas.ID,0,meas.value))


        if self.commstype=="CAN":
            # init CAN interface
            os.system('sudo ip link set can0 type can bitrate 1000000')
            os.system('sudo ifconfig can0 up')
            self.can0 = can.interface.Bus(channel='can0', bustype='socketcan_ctypes')
        elif self.commstype == "loopback":
            self.loopbackBuffer = PC_Message(0, 0, 0)
            self.loopbackMSG = False


    def send(self,MsgID,value):

        if self.commstype=="CAN":
            valueBytes=[]
            msg = can.Message(arbitration_id=MsgID, data=valueBytes, extended_id=False)
            self.can0.send(msg)
        elif self.commstype == "loopback":
            self.loopbackBuffer=PC_Message(MsgID,value,0)
            self.loopbackMSG = True


    def read(self):

        if self.commstype=="CAN":
            msg = self.can0.recv(30.0)
            print(msg)
            if msg is None:
                print('No message was received')
        elif self.commstype == "loopback":
            if self.loopbackMSG==True:
                return [self.loopbackBuffer.MSGID,self.loopbackBuffer.setValue]
                self.loopbackMSG=False
            else:
                return None


    def __del__(self):
        if self.commstype=="CAN":
            os.system('sudo ifconfig can0 down')
