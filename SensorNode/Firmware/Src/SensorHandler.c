/*
 * SensorHandler.c
 *
 *  Created on: Dec 3, 2020
 *      Author: robert
 */

#include "SensorHandler.h"

#define TICKSPS 10000 // ticks/s

extern RuntimeData_t RuntimeData;
extern Constants_t Constants;
SensorData_t SensorData;

void InitSensorHandler(void) {
	SensorData.analog1_mV = 0;
	SensorData.analog2_mV = 0;
	SensorData.pulseCount = 0;
}
void SensorHandler_CreateMeasurement(void) {
	uint32_t tempValue = 0;
	if (Constants.nodeType == SensorResistive) {
		tempValue = SensorData.analog1_mV;
		//todo: Add calculations according to resistors
	} else if (Constants.nodeType == SensorResistiveDifferential) {
		tempValue = SensorData.analog1_mV - SensorData.analog2_mV;
		//todo: Add calculations according to resistors
	} else if (Constants.nodeType == SensorVoltage) {
		tempValue = SensorData.analog1_mV;
	} else if (Constants.nodeType == SensorVoltageDifferential) {
		tempValue = SensorData.analog1_mV - SensorData.analog2_mV;
	} else if (Constants.nodeType == SensorFreqency) {
		tempValue = TICKSPS / SensorData.pulseCount;
	} else if (Constants.nodeType == SensorPulsewidth) {

	} else if (Constants.nodeType == ActorOnOff) {

	} else if (Constants.nodeType == ActorPWM) {

	} else if (Constants.nodeType == ActorMotor) {

	} else {
	}

	// this might not be necessary; use of valuePrev is unclear.
	RuntimeData.valuePrev = RuntimeData.value;

	// calculate node value from raw sensor values
	RuntimeData.value = Constants.valueOffset
			+ (Constants.valueMultiplier_m * tempValue) / 1000;

}
