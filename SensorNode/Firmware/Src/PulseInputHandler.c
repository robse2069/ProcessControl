/*
 * PulseInputHandler.c
 *
 *  Created on: Dec 3, 2020
 *      Author: robert
 */

#include "PulseInputHandler.h"
#include "tim.h"
#include "SensorHandler.h"


extern SensorData_t SensorData;

void InitPulseInputHandler(TIM_HandleTypeDef *htim){
	HAL_TIM_IC_Start_IT(htim,TIM_CHANNEL_1);
}

void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim){
	SensorData.pulseCount = htim->Instance->CNT;
	htim->Instance->CNT=0;
}
