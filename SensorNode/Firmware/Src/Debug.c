/*
 * Debug.c
 *
 *  Created on: Oct 15, 2020
 *      Author: robert
 */


#include "usart.h"


void print(char* string, uint8_t len){

	HAL_UART_Transmit(&huart2,string,len,100);

}
