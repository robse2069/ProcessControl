import tkinter as tk
import logging
import time
import sys
import can


class ConfiguratorGUI():
    def __init__(self,master,Data):
        self.window=master

        #configure windowgrid
        self.window.rowconfigure(list(range(0,12)), minsize=20, weight=1)
        self.window.columnconfigure(list(range(0,6)), minsize=100, weight=1)

        #todo: remove text "not connected" from ent fields
        self.window.lbl_nodeIDDescr = tk.Label(master=None, text="Node ID")
        self.window.lbl_nodeIDDescr.grid(row=0, column=0)
        self.window.ent_nodeID=tk.Entry(master=None,width = 10)
        self.window.ent_nodeID.grid(row=0, column=1)
        self.window.ent_nodeID.insert(0, '0x7ff')
        self.window.btn_selectNode = tk.Button(master=None, text="Connect to Node", command=self.selectNode)
        self.window.btn_selectNode.grid(row=0, column=2)
        self.window.lbl_nameDescr = tk.Label(master=None, text="Node Name")
        self.window.lbl_nameDescr.grid(row=1, column=0)
        self.window.ent_name=tk.Entry(master=None,width = 10)
        self.window.ent_name.grid(row=1, column=1)
        self.window.ent_name.insert(0, 'Not Connected')
        self.window.lbl_nodeTypeDescr = tk.Label(master=None, text="Node Type")
        self.window.lbl_nodeTypeDescr.grid(row=2, column=0)
        self.window.ent_nodeType=tk.Entry(master=None,width = 10)
        self.window.ent_nodeType.grid(row=2, column=1)
        self.window.ent_nodeType.insert(0, 'Not Connected')

        self.window.lbl_valueSetDescr = tk.Label(master=None, text="Set Value")
        self.window.lbl_valueSetDescr.grid(row=4, column=0)
        self.window.lbl_valueDescr = tk.Label(master=None, text="Actual Value")
        self.window.lbl_valueDescr.grid(row=4, column=1)
        self.window.lbl_unitDescr = tk.Label(master=None, text="Unit (8 Characters)")
        self.window.lbl_unitDescr.grid(row=4, column=2)
        self.window.ent_valueSet=tk.Entry(master=None,width = 10)
        self.window.ent_valueSet.grid(row=5, column=0)
        self.window.ent_valueSet.insert(0, 'Not Connected')
        self.window.lbl_value = tk.Label(master=None, text="not implemented")
        self.window.lbl_value.grid(row=5, column=1)
        self.window.ent_unit=tk.Entry(master=None,width = 10)
        self.window.ent_unit.grid(row=5, column=2)
        self.window.ent_unit.insert(0, 'Not Connected')
        self.window.btn_writeControl = tk.Button(master=None, text="Write Set Value", command=self.writeControl)
        self.window.btn_writeControl.grid(row=6, column=0)

        self.window.lbl_valueOffsetDescr = tk.Label(master=None, text="Offset")
        self.window.lbl_valueOffsetDescr.grid(row=8, column=0)
        self.window.ent_valueOffset=tk.Entry(master=None,width = 10)
        self.window.ent_valueOffset.grid(row=8, column=1)
        self.window.ent_valueOffset.insert(0, 'Not Connected')
        self.window.lbl_valueMultiplierDescr = tk.Label(master=None, text="Multiplier (1/1000)")
        self.window.lbl_valueMultiplierDescr.grid(row=9, column=0)
        self.window.ent_valueMultiplier=tk.Entry(master=None,width = 10)
        self.window.ent_valueMultiplier.grid(row=9, column=1)
        self.window.ent_valueMultiplier.insert(0, 'Not Connected')


        self.window.lbl_lastErrorcodeDescr = tk.Label(master=None, text="Last Error")
        self.window.lbl_lastErrorcodeDescr.grid(row=1, column=4)
        self.window.lbl_lastErrorcode = tk.Label(master=None, text="Error: not implemented")
        self.window.lbl_lastErrorcode.grid(row=1, column=5)
        self.window.btn_resetLastErrorcode = tk.Button(master=None, text="Reset last Error", command=self.resetLastErrorcode)
        self.window.btn_resetLastErrorcode.grid(row=2, column=5)


        self.window.lbl_valueDefaultDescr = tk.Label(master=None, text="Default Value")
        self.window.lbl_valueDefaultDescr.grid(row=5, column=4)
        self.window.ent_valueDefault=tk.Entry(master=None,width = 10)
        self.window.ent_valueDefault.grid(row=5, column=5)
        self.window.ent_valueDefault.insert(0, 'Not Connected')
        self.window.lbl_valueMaxDescr = tk.Label(master=None, text="Maximum Value")
        self.window.lbl_valueMaxDescr.grid(row=6, column=4)
        self.window.ent_valueMax=tk.Entry(master=None,width = 10)
        self.window.ent_valueMax.grid(row=6, column=5)
        self.window.ent_valueMax.insert(0, 'Not Connected')
        self.window.lbl_valueMinDescr = tk.Label(master=None, text="Minimum Value")
        self.window.lbl_valueMinDescr.grid(row=7, column=4)
        self.window.ent_valueMin=tk.Entry(master=None,width = 10)
        self.window.ent_valueMin.grid(row=7, column=5)
        self.window.ent_valueMin.insert(0, 'Not Connected')
        self.window.lbl_canIDDescr = tk.Label(master=None, text="CAN ID")
        self.window.lbl_canIDDescr.grid(row=8, column=4)
        self.window.ent_canID=tk.Entry(master=None,width = 10)
        self.window.ent_canID.grid(row=8, column=5)
        self.window.ent_canID.insert(0, 'Not Connected')
        self.window.lbl_updaterateDescr = tk.Label(master=None, text="Updaterate in ms")
        self.window.lbl_updaterateDescr.grid(row=9, column=4)
        self.window.ent_updaterate_ms=tk.Entry(master=None,width = 10)
        self.window.ent_updaterate_ms.grid(row=9, column=5)
        self.window.ent_updaterate_ms.insert(0, 'Not Connected')

        self.window.btn_writeParameters = tk.Button(master=None, text="Write all Parameters to Node", command=self.writeParameters)
        self.window.btn_writeParameters.grid(row=11, column=1)

        # logging
        # self.btn_logging = tk.Button(master=None, text="Start / Stop Logging", command=self.toggleLogging)
        # self.btn_logging.grid(row=3, column=0)
        # self.lbl_Logging = tk.Label(master=None, text="no Value")
        # self.lbl_Logging.grid(row=3, column=1)
        # self.ent_filename=tk.Entry(master=None,width = 10)
        # self.ent_filename.insert(0, 'Logfile')
        # self.ent_filename.grid(row=3, column=2)


        self.window.title("PC Node Configurator")
        #start updater for all displayed values

        logging.info("GUI done")
        self.update()


    def update(self):
        logging.info("updating...")


        #todo: add all label and not(!) entry fields

        self.window.ent_canID.delete(0,20)
        self.window.ent_canID.insert(0,hex(Data.CanID_8U))

        self.window.after(500, self.update)



    def selectNode(self):
        try:
            Data.CanID_8U = int(self.window.ent_nodeID.get())
        except:
            Data.CanID_8U = int(self.window.ent_nodeID.get(),16)

        Data.readNodeData()


    def writeControl(self):
        #todo: write information into Data-class
        #todo: send Message with setvalue
        pass

    def resetLastErrorcode(self):
        #todo: set last errorcode = all fine
        Data.writeNodeData()


    def writeParameters(self):
        # todo: write all information into Data-class
        Data.writeNodeData()


class NodeData():
    def __init__(self):
        self.value_16U=0
        self.valueSet_16U=0
        self.valueDefault_16U=0
        self.valueMax_16U=0
        self.valueMin_16U=0
        self.valueOffset_16U=0
        self.valueMultiplier_m_16U=0
        self.CanID_8U=0x7ff
        self.unit_8x8U=" no unit"
        self.name_8x8U=" no Name"
        self.updaterate_ms_16U=0
        self.nodeType=0
        self.lastErrorcode=0

    def readNodeData(self):

        raise Exception("not yet implemented")

    def writeNodeData(self):
        #todo: write messages
        # refresh all information
        self.readNodeData()


format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,datefmt="%H:%M:%S")

Data=NodeData()
root=tk.Tk()


GUI=ConfiguratorGUI(root,Data)

root.mainloop()