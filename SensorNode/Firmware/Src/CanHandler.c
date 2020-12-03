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

void InitCANHandler(CAN_HandleTypeDef *hcan) {
	/*if (HAL_CAN_Receive_IT(&hcan, CAN_FIFO0) != HAL_OK) {
	 Constants.lastErrorcode = CAN_Error;
	 Statehandler(ErrorOccured);
	 }*/
	HAL_CAN_Start(hcan);


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
void CAN_PublishData(CAN_HandleTypeDef *hcan) {

	print("CAN\n", 4);

	CAN_TxHeaderTypeDef myHeader;
	uint8_t myData[8];

	myHeader.DLC = 8;
	myHeader.ExtId = 0;
	myHeader.IDE = CAN_ID_STD;
	myHeader.RTR = CAN_RTR_DATA;
	myHeader.StdId = Constants.CanID;
	myHeader.TransmitGlobalTime = DISABLE;

	myData[CAN_VALUE_MSB] = RuntimeData.value >> 8;
	myData[CAN_VALUE_LSB] = RuntimeData.value & 0xff;

	myData[CAN_VALUESET_MSB] = RuntimeData.valueSet >> 8;
	myData[CAN_VALUESET_LSB] = RuntimeData.valueSet & 0xff;
	myData[CAN_VALUEDEFAULT_MSB] = Constants.valueDefault >> 8;
	myData[CAN_VALUEDEFAULT_LSB] = Constants.valueDefault & 0xff;
	myData[CAN_STATE] = SystemState;
	myData[CAN_ERRORCODE] = Constants.lastErrorcode;

	uint32_t myMailbox;
	myMailbox =CAN_TX_MAILBOX0;

	if ((hcan->Instance->TSR & CAN_TSR_TME0) != 0U){
		HAL_CAN_AddTxMessage(hcan, &myHeader, myData, &myMailbox);
	}

}
