/*
 * SensorHandler.c
 *
 *  Created on: Dec 3, 2020
 *      Author: robert
 */

#include "DataHandler.h"
#include "SensorHandler.h"
#include "adc.h"

extern RuntimeData_t RuntimeData;
extern Constants_t Constants;
extern ADC_HandleTypeDef hadc;

SensorData_t SensorData;

void InitSensorHandler(void) {
	SensorData.analog1_mV = 42;
	SensorData.analog2_mV = 23;
	SensorData.pulseCount = 0;
//	InitADCHandler();	// todo: reactivate
}
void SensorHandler_CreateMeasurement(void) {
	int32_t tempValue = 0;
	if (Constants.nodeType == SensorResistive) {
// todo: configure ADC with 2 channels and DMA.
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
	RuntimeData.value = (int16_t) ( tempValue * Constants.valueMultiplier_m  / 1000 + Constants.valueOffset);

}
