import tkinter as tk
import time
import threading
import logging
import xml.etree.ElementTree as ET
import PC_Comms
import control as controlhandler
import measurement as meashandler
import myLogging
import sys
import can
import struct

import queue


class myGUIClass:
    def __init__(self, master):
        self.window = master
        self.GUIControls=[]
        self.GUIControlsReadback=[]
        self.GUIMeasurementsLabels=[]
        self.GUIMeasurements=[]

        #extract information from config
        numberOfControls=len(config.Controls)
        numberOfMeasurements = len(config.Measurements)

        #configure windowgrid
        self.window.rowconfigure(list(range(max(numberOfControls,numberOfMeasurements)+1)), minsize=50, weight=1)
        self.window.columnconfigure([0, 1, 2, 3], minsize=200, weight=1)
        gridrow=0

        #create control buttons etc.
        for control in config.Controls:
            #create actual controls
            if control.type == "button":
                logging.info("button created")
                self.GUIControls.append(tk.Button(master=self.window, text=control.name, command=control.toggle))
                self.GUIControls[-1].grid(row=gridrow, column=0, sticky="nsew")
            # add "else if" for other control types: slider, parameter, etc.
            else:
                self.GUIControls.append(tk.Label(master=self.window,text="empty"))


            #readback displays
            self.GUIControlsReadback.append(tk.Label(master=self.window, text="no Value"))
            self.GUIControlsReadback[-1].grid(row=gridrow, column=1)
            gridrow += 1

        # logging
        self.btn_logging = tk.Button(master=self.window, text="Start / Stop Logging", command=self.toggleLogging)
        self.btn_logging.grid(row=gridrow, column=0)
        self.lbl_Logging = tk.Label(master=self.window, text="no Value")
        self.lbl_Logging.grid(row=gridrow, column=1)
        self.ent_filename=tk.Entry(master=self.window,width = 50)
        self.ent_filename.insert(0, 'Logfile')
        self.ent_filename.grid(row=gridrow, column=2)

        #create measurements table
        gridrow = 0
        for measurement in config.Measurements:
            # wirte Labels
            self.GUIMeasurementsLabels.append(tk.Label(master=self.window, text=measurement.name))
            self.GUIMeasurementsLabels[-1].grid(row=gridrow, column=2, sticky="nsew")

            # value displays
            self.GUIMeasurements.append(tk.Label(master=self.window, text="no Value"))
            self.GUIMeasurements[-1].grid(row=gridrow, column=3, sticky="nsew")
            gridrow += 1



        self.window.title("Process Control")
        #start updater for all displayed values
        self.update()
        self.callLogging()
        #self.CANScheduler

    def toggleLogging(self):
        filename=self.ent_filename.get()
        logginghandler.toggleLogging(filename)

    def update(self):
        logging.info("updating...")
        iterator = 0
        # update control readbacks
        for setValue in self.GUIControlsReadback:
            if config.Controls[iterator].unit != "none":
                setValue["text"] = config.Controls[iterator].value + " " + config.Controls[iterator].unit
            else:
                setValue["text"] = config.Controls[iterator].value
            iterator += 1

        #update measurements
        iterator = 0
        for value in self.GUIMeasurements:
            if config.Measurements[iterator].unit != "none":
                value["text"] = str(config.Measurements[iterator].value) + " " + config.Measurements[iterator].unit
            else:
                value["text"] = config.Measurements[iterator].value
            iterator += 1

        #update logging
        self.lbl_Logging['text']=logginghandler.state
        #
        self.window.after(config.GUIUpdate, self.update)

    def callLogging(self):
        self.window.after(logginghandler.cycleTime,self.callLogging)
        logginghandler.loggingTask()



class configManager:
    def __init__(self):

        #extract info from xml
        tree = ET.parse('config.xml')
        root = tree.getroot()

        #create control structure
        self.Controls=[]
        ListOfControls = root.findall('control')
        for iterator in ListOfControls:
            try:
                self.Controls.append(controlhandler.control(iterator.attrib['name'],int(iterator.attrib['setValue']),int(iterator.attrib['value']),int(iterator.attrib['minValue']),int(iterator.attrib['maxValue']),iterator.attrib['unit'],int(iterator.attrib['MsgID']),iterator.attrib['type']))
            except:
                sys.exit("Config import crashed. Check config.xml")

        # create measurements structure
        self.Measurements = []
        ListOfMeasurements = root.findall('measurement')
        for iterator in ListOfMeasurements:
            try:
                self.Measurements.append(meashandler.measurement(iterator.attrib['name'],int(iterator.attrib['value']),int(iterator.attrib['minValue']),int(iterator.attrib['maxValue']),iterator.attrib['unit'],int(iterator.attrib['MsgID'])))
            except:
                sys.exit("Config import crashed. Check config.xml")

        # misc options
        self.commsMethod=root.findall('communication')[0].attrib['method']
        if self.commsMethod=="loopback":
            logging.info("Communication disabled, Loopback only")
        self.GUIUpdate=root.findall('GUIUpdate')[0].text

        #logging options
        root = root.findall('logging')
        tempLogging={}
        for iterator in root:
            tempLogging[iterator.attrib['name']]=iterator.attrib['value']

        #tempLogging['cycletime']=int(tempLogging['cycletime'])

        tempLogging['objList']=[]
        for object in self.Controls:
            tempLogging['objList'].append(object)
        for object in self.Measurements:
            tempLogging['objList'].append(object)
        self.logging=tempLogging

class ThreadedClient:
    def __init__(self,master):
        self.master=master

        # Create the queue
        self.queue = queue.Queue()

        # Set up the GUI part
        self.gui = myGUIClass(master)

        # Set up the thread to do asynchronous I/O
        # More can be made if necessary
        self.can0 = can.interface.Bus(channel='can0', bustype='socketcan_ctypes')
        self.threadCAN = threading.Thread(target=self.workerThreadCAN)
        self.threadCAN.start()

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.CANScheduler()




#        self.window.mainloop()



    def CANScheduler(self):
        # function is polling the can recv queue, decodes information and updates measurements
        # control updates are also send out regularly

        for control in config.Controls:
            pcComms.send(control.ID,control.setValue)


        self.master.after(config.GUIUpdate, self.CANScheduler)

    def workerThreadCAN(self):
        """
        This is where the asynchronous CAN Messages are received.
        One important thing to remember is that the thread has to yield
        control.
        """

        while True:
            pcComms.read()

root=tk.Tk()
format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,datefmt="%H:%M:%S")


config = configManager()
pcComms = PC_Comms.PC_Comms(config.Controls,config.Measurements,type="CAN")


logginghandler=myLogging.myLogging(config.logging)

client=ThreadedClient(root)
root.mainloop()

logginghandler.stopLogging()
