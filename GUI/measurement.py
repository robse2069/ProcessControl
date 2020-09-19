

class measurement:
    def __init__(self, name,value=0, minValue=0, maxValue=1000,unit="",MsgID=10000):
        self.name=name
        self.value=value
        self.min=minValue
        self.max=maxValue
        self.unit = unit
        self.ID=MsgID

    def update(self,value):
        self.value=value


