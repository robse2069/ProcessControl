import os
import can
import struct



class PC_Comms:

    def __init__(self,Controls,Measurements,type="CAN"):
        self.commstype=type
        self.Controls = Controls
        self.Measurements = Measurements

#        self.name=name
#        self.setValue=setValue
#        self.value=value
#        self.min=minValue
#        self.max = maxValue
#        self.unit=unit
#        self.ID=MsgID
#        self.type=type  #can be: button, slider, number, string


        if self.commstype=="CAN":
            # init CAN interface
            os.system('sudo ip link set can0 type can bitrate 500000')
            os.system('sudo ifconfig can0 up')
            self.can0 = can.interface.Bus(channel='can0')#, bustype='socketcan_ctypes')


    def send(self,MsgID,value):

        if self.commstype=="CAN":
            valueBytes=[]
            msg = can.Message(arbitration_id=MsgID, data=valueBytes, extended_id=False)
            #self.can0.send(msg)


    def read(self):

        if self.commstype=="CAN":
            CANRecvdMsg = self.can0.recv(30.0)
            for chara in self.Controls:
                if chara.ID == CANRecvdMsg.arbitration_id:
                    # received message matches an existing characteristic
                    chara.value = struct.unpack('>H',CANRecvdMsg.data[0:2])[0]
                    pass
            for chara in self.Measurements:
                if chara.ID == CANRecvdMsg.arbitration_id:
                    # received message matches an existing characteristic
                    chara.value = struct.unpack('>H',CANRecvdMsg.data[0:2])[0]
                    pass



    def __del__(self):
        if self.commstype=="CAN":
            os.system('sudo ifconfig can0 down')
