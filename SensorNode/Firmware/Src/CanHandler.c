/*
 * CanHandler.c
 *
 *  Created on: Oct 6, 2020
 *      Author: robert
 */

#include "CanHandler.h"
#include "DataHandler.h"
#include "StateHandler.h"

extern Constants_t Constants;
extern RuntimeData_t RuntimeData;
extern SystemState_t SystemState;

void CAN_HandleRecvMsg(uint32_t ID, uint8_t data) {

	switch (ID) {
	case CAN_MSG_EMERGENCY:
		// Relevant only for Actor-Nodes. All Actors shall go to Default value.
		RuntimeData.valueSet = Constants.valueDefault;
		break;
	case CAN_MSG_CONTROL_NODE:
		if (((data[CANID_MSB] << 8) | data[CANID_LSB]) == Constants.CanID) {
			// listen only if node is addressed by its CAN ID
			if (data[CAN_NODECOMMAND] == CAN_REQUEST_SETUP) {
				StateHandler(RequestSetup);
			}
			if (data[CAN_NODECOMMAND] == CAN_TERMINATE_SETUP) {
				StateHandler(SetupComplete);
			}
		}
		break;
	case CAN_MSG_SETUP_MSG_1:
		if (SystemState == Setup) {
			//only react to setupmessages if node is switched to setup
			// SetupMsg 1 contains the Name
			for (uint8_t i; i < 8; i++) {
				Constants.name[i] = data[i];
			}
		}
		break;
	case CAN_MSG_SETUP_MSG_2:
		if (SystemState == Setup) {
			//only react to setupmessages if node is switched to setup
			// Message contains the Unit of the value
			for (uint8_t i; i < 8; i++) {
				Constants.unit[i] = data[i];
			}
		}
		break;
	case CAN_MSG_SETUP_MSG_3:
		if (SystemState == Setup) {
			//only react to setupmessages if node is switched to setup
			Constants.valueMin = (data[CAN_VALUEMIN_MSB] << 8) | data[CAN_VALUEMIN_LSB];
			Constants.valueMax = (data[CAN_VALUEMAX_MSB] << 8) | data[CAN_VALUEMAX_LSB];
			Constants.valueDefault = (data[CAN_VALUEDEFAULT_MSB] << 8) | data[CAN_VALUEDEFAULT_LSB];
			Constants.updaterate_ms = (data[CAN_UPDATERATE_MSB] << 8) | data[CAN_UPDATERATE_LSB];
		}
		break;
	case CAN_MSG_SETUP_MSG_4:
		if (SystemState == Setup) {
			//only react to setupmessages if node is switched to setup
			Constants.nodeType = data[CAN_NODETYPE];
			Constants.CanID = (data[CANID_MSB] << 8) | data[CANID_LSB];
			Constants.valueOffset = (data[CAN_VALUEOFFSET_MSB] << 8) | data[CAN_VALUEOFFSET_LSB];
			Constants.valueMultiplier_m = (data[CAN_VALUEMULTIPLIER_MSB] << 8)
					| data[CAN_VALUEMULTIPLIER_LSB];
			Constants.lastErrorcode = data[CAN_ERRORCODE];
		}
		StoreConstants();
		SendSetupMsgs();
		break;
	case Constants.CanID:
		// This is the ID that the Node was configured to.
		RuntimeData.valueSet = (data[CAN_VALUESET_MSB] << 8) | data[CAN_VALUESET_LSB];
		// if node is Sensor, this value is ignored
		break;
	default:
		break;
	}

}

