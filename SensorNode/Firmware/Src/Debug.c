/*
 * Debug.c
 *
 *  Created on: Oct 15, 2020
 *      Author: robert
 */

#include "Debug.h"
#include "usart.h"
#include "CanHandler.h"

void print(uint8_t* string, uint8_t len){
	if(HAL_UART_GetState(&huart2)==HAL_UART_STATE_READY)
		HAL_UART_Transmit(&huart2,string,len,100);
}

void DecodeDebugMessage(uint8_t *debugmessage){
	uint8_t data[8];
	uint16_t ID = (debugmessage[0]<<8)|debugmessage[1];
	for (uint8_t i=0;i<8;i++){
		data[i]=debugmessage[i+2];
	}
	CAN_HandleRecvMsg(ID,data);

}

