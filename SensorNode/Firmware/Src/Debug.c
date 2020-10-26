/*
 * Debug.c
 *
 *  Created on: Oct 15, 2020
 *      Author: robert
 */


#include "usart.h"
#include "CanHandler.h"

void print(char* string, uint8_t len){
	HAL_UART_Transmit(&huart2,string,len,100);
}

void DecodeDebugMessage(uint8_t *debugmessage){
	CANMessage_t canMsg;
	canMsg.ID=(debugmessage[0]<<8)|debugmessage[1];
	for (uint8_t i;i<8;i++){
		canMsg.data[i]=debugmessage[i+2];
	}
	CAN_HandleRecvMsg(canMsg);

}

