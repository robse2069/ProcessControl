/*
 * SensorHandler.h
 *
 *  Created on: Dec 3, 2020
 *      Author: robert
 */

#ifndef SENSORHANDLER_H_
#define SENSORHANDLER_H_

#include "stdint.h"
#include "DataHandler.h"

#define TICKSPS 10000 // ticks/s


typedef struct{
	uint16_t analog1_mV;
	uint16_t analog2_mV;
	uint16_t pulseCount;

}SensorData_t;

void InitSensorHandler(void);
void SensorHandler_CreateMeasurement(void);


#endif /* SENSORHANDLER_H_ */
