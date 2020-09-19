import PC_Comms

class control:
    def __init__(self, name, setValue=0, value=0, minValue=0, maxValue=1, unit="", MsgID=10000, type="button"):
        self.name=name
        self.setValue=setValue
        self.value=value
        self.min=minValue
        self.max = maxValue
        self.unit=unit
        self.ID=MsgID
        self.type=type  #can be: button, slider, number, string


    def toggle(self):
        if self.setValue == 0:
            self.setValue=1
        else:
            self.setValue=0
