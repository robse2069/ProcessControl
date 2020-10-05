from csv import writer

class myLogging:
    def __init__(self,config):
        self.file=[]
        self.state="off"
        self.cycleTime=config['cycletime']
        self.doLogging=False
        self.objList = config['objList']
        self.filename="tempfile"



    def loggingTask(self):
        if self.state=="active":
            # log stuff
            values=[]
            for obj in self.objList:
                values.append(obj.value)
            self.writer.writerow(values)
        elif self.state == "off":
            self.state="inactive"
        else:
            pass


    def toggleLogging(self,filename):
        self.filename=filename
        if self.state =="inactive":
            self.startLogging()
        elif self.state == "active":
            self.stopLogging()
        else:
            print("invalid state transition")

    def startLogging(self):
        self.state="starting"
        self.file = open(self.filename,'a+', newline='')
        self.writer=writer(self.file)
        #add header with information
        headline="timestamp"
        for obj in self.objList:
            headline = headline + ", " + obj.name
        self.file.write(headline + "\r\n")


        # at end of function
        self.state="active"

    def stopLogging(self):
        self.state="stopping"
        try:
            self.file.close()
        except:
            pass
        # at end of function
        self.state="inactive"