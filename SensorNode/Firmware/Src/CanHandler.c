/*
 * CanHandler.c
 *
 *  Created on: Oct 6, 2020
 *      Author: robert
 */

#include "CanHandler.h"
#include "can.h"
#include "DataHandler.h"
#include "StateHandler.h"
#include "SetupHandler.h"
#include "Debug.h"

extern Constants_t Constants;
extern RuntimeData_t RuntimeData;
extern SystemState_t SystemState;
extern CAN_HandleTypeDef hcan;

void InitCANHandler(void) {
	/*if (HAL_CAN_Receive_IT(&hcan, CAN_FIFO0) != HAL_OK) {
	 Constants.lastErrorcode = CAN_Error;
	 Statehandler(ErrorOccured);
	 }*/
}

void CAN_HandleRecvMsg(uint32_t ID, uint8_t *data) {

	if (ID == CAN_MSG_EMERGENCY) {
		// Relevant only for Actor-Nodes. All Actors shall go to Default value.
		RuntimeData.valueSet = Constants.valueDefault;
	} else if (ID == CAN_MSG_CONTROL_NODE) {
		if (((data[CANID_MSB] << 8) | data[CANID_LSB]) == Constants.CanID) {
			// listen only if node is addressed by its CAN ID
			if (data[CAN_NODECOMMAND] == CAN_REQUEST_SETUP) {
				Statehandler(RequestSetup);
			}
			if (data[CAN_NODECOMMAND] == CAN_TERMINATE_SETUP) {
				Statehandler(SetupComplete);
			}
		}
	} else if (ID == CAN_MSG_SETUP_MSG_1) {

		if (SystemState == Setup) {
			//only react to setupmessages if node is switched to setup
			// SetupMsg 1 contains the Name
			for (uint8_t i = 0; i < 8; i++) {
				Constants.name[i] = data[i];
			}
		}
	} else if (ID == CAN_MSG_SETUP_MSG_2) {

		if (SystemState == Setup) {
			//only react to setupmessages if node is switched to setup
			// Message contains the Unit of the value
			for (uint8_t i = 0; i < 8; i++) {
				Constants.unit[i] = data[i];
			}
		}
	} else if (ID == CAN_MSG_SETUP_MSG_3) {
		if (SystemState == Setup) {
			//only react to setupmessages if node is switched to setup
			Constants.valueMin = (data[CAN_VALUEMIN_MSB] << 8)
					| data[CAN_VALUEMIN_LSB];
			Constants.valueMax = (data[CAN_VALUEMAX_MSB] << 8)
					| data[CAN_VALUEMAX_LSB];
			Constants.valueDefault = (data[CAN_VALUEDEFAULT_MSB] << 8)
					| data[CAN_VALUEDEFAULT_LSB];
			Constants.updaterate_ms = (data[CAN_UPDATERATE_MSB] << 8)
					| data[CAN_UPDATERATE_LSB];
		}
	} else if (ID == CAN_MSG_SETUP_MSG_4) {
		if (SystemState == Setup) {
			//only react to setupmessages if node is switched to setup
			Constants.nodeType = data[CAN_NODETYPE];
			Constants.CanID = (data[CANID_MSB] << 8) | data[CANID_LSB];
			Constants.valueOffset = (data[CAN_VALUEOFFSET_MSB] << 8)
					| data[CAN_VALUEOFFSET_LSB];
			Constants.valueMultiplier_m = (data[CAN_VALUEMULTIPLIER_MSB] << 8)
					| data[CAN_VALUEMULTIPLIER_LSB];
			Constants.lastErrorcode = data[CAN_ERRORCODE];
		}
		StoreConstants();
		SendSetupMsgs();
	} else if (ID == Constants.CanID) {

		// This is the ID that the Node was configured to.
		RuntimeData.valueSet = (data[CAN_VALUESET_MSB] << 8)
				| data[CAN_VALUESET_LSB];
		// if node is Sensor, this value is ignored

	}

}
void CAN_PublishData(void) {

	volatile CanTxMsgTypeDef* myTxMsg;

	if (hcan.State != HAL_CAN_STATE_RESET && hcan.State != HAL_CAN_STATE_BUSY
			&& hcan.State != HAL_CAN_STATE_BUSY_TX
			&& hcan.State != HAL_CAN_STATE_BUSY_TX_RX0
			&& hcan.State != HAL_CAN_STATE_ERROR) {
		(*myTxMsg).Data[CAN_VALUE_MSB] = RuntimeData.value >> 8;
		myTxMsg->Data[CAN_VALUE_LSB] = RuntimeData.value & 0xff;

		myTxMsg->Data[CAN_VALUESET_MSB] = RuntimeData.valueSet >> 8;
		myTxMsg->Data[CAN_VALUESET_LSB] = RuntimeData.valueSet & 0xff;
		myTxMsg->Data[CAN_VALUEDEFAULT_MSB] = Constants.valueDefault >> 8;
		myTxMsg->Data[CAN_VALUEDEFAULT_LSB] = Constants.valueDefault & 0xff;
		myTxMsg->Data[CAN_STATE] = SystemState;
		myTxMsg->Data[CAN_ERRORCODE] = Constants.lastErrorcode;

		myTxMsg->DLC = 8;
		myTxMsg->ExtId = 0;
		myTxMsg->IDE = 0;
		myTxMsg->RTR = 0;
		myTxMsg->StdId = Constants.CanID;
		hcan.pTxMsg = myTxMsg;
		HAL_CAN_Transmit(&hcan, Constants.updaterate_ms / 10);

	}
}
