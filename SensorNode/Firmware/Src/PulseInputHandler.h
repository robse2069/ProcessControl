/*
 * PulseInputHandler.h
 *
 *  Created on: Dec 3, 2020
 *      Author: robert
 */

#ifndef PULSEINPUTHANDLER_H_
#define PULSEINPUTHANDLER_H_

#include "stdint.h"
#include "tim.h"


void InitPulseInputHandler(TIM_HandleTypeDef *htim);
void PulseInputHandler_updateMeasurement(uint16_t count);


#endif /* PULSEINPUTHANDLER_H_ */
