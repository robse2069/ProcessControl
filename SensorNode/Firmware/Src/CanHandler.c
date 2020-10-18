/*
 * CanHandler.c
 *
 *  Created on: Oct 6, 2020
 *      Author: robert
 */

#include "CanHandler.h"
#include "DataHandler.h"

extern Constants_t Constants;
extern RuntimeData_t RuntimeData;

void CAN_HandleRecvMsg(CANMessage_t message) {

	switch (message.ID) {
	case CAN_MSG_EMERGENCY:
		// Relevant only for Actor-Nodes. All Actors shall go to Default value.
		RuntimeData.valueSet
		break;
	case CAN_MSG_CONTROL_NODE:
		break;
	case CAN_MSG_SETUP_MSG_1:
		break;
	case CAN_MSG_SETUP_MSG_2:
		break;
	case CAN_MSG_SETUP_MSG_3:
		break;
	case CAN_MSG_SETUP_MSG_4:
		break;
	case Constants.CanID:
		// This is the ID that the Node was configured to.
	default:
		break;
	break}

}

