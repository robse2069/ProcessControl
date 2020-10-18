/*
 * CanHandler.h
 *
 *  Created on: Oct 15, 2020
 *      Author: robert
 */

#ifndef CANHANDLER_H_
#define CANHANDLER_H_
#include "can.h"


// Definitions of CAN Message IDs
#define CAN_MSG_EMERGENCY		0x000

#define CAN_MSG_CONTROL_NODE	0x7F0
#define CAN_MSG_SETUP_MSG_1		0x7F1
#define CAN_MSG_SETUP_MSG_2		0x7F2
#define CAN_MSG_SETUP_MSG_3		0x7F3
#define CAN_MSG_SETUP_MSG_4		0x7F4

// Bytes in CAN_MSG_CONTROL_NODE
#define CAN_NODECOMMAND			0
#define CANID_MSB				1
#define CANID_LSB				2

// Bytes in CAN_MSG_SETUP_MSG_3
#define CAN_VALUEMIN_MSB		0
#define CAN_VALUEMIN_LSB		1
#define CAN_VALUEMAX_MSB		2
#define CAN_VALUEMAX_LSB		3
#define CAN_VALUEDEFAULT_MSB	4
#define CAN_VALUEDEFAULT_LSB	5
#define CAN_UPDATERATE_MSB		6
#define CAN_UPDATERATE_LSB		7

// Bytes in CAN_MSG_SETUP_MSG_3
#define CAN_NODETYPE			0
//CANID_MSB defined in CAN_MSG_SETUP_MSG_3
//CANID_LSB defined in CAN_MSG_SETUP_MSG_3
#define CAN_VALUEOFFSET_MSB		3
#define CAN_VALUEOFFSET_LSB		4
#define CAN_VALUEMULTIPLIER_MSB	5
#define CAN_VALUEMULTIPLIER_LSB	6
#define CAN_ERRORCODE			7

//Bytes in "Working" Message outside Setup
#define CAN_VALUE_MSB			0
#define CAN_VALUE_LSB			1
#define CAN_VALUESET_MSB		2
#define CAN_VALUESET_LSB		3
//	valueDefault(MSB) defined in CAN_MSG_SETUP_MSG_3
//	valueDefault(LSB) defined in CAN_MSG_SETUP_MSG_3
#define CAN_STATE				6
//	Errorcode defined in CAN_MSG_SETUP_MSG_4

typedef struct{
	uint16_t ID;
	uint8_t data[8];
}CANMessage_t;

void CAN_HandleRecvMsg(CANMessage_t message);
#endif /* CANHANDLER_H_ */
