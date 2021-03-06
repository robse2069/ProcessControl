/*
 * DataHandler.h
 *
 *  Created on: Oct 15, 2020
 *      Author: robert
 */

#ifndef DATAHANDLER_H_
#define DATAHANDLER_H_

#include "stdint.h"

typedef enum{
	SensorResistive,
	SensorResistiveDifferential,
	SensorVoltage,
	SensorVoltageDifferential,
	SensorFreqency,
	SensorPulsewidth,
	ActorOnOff=10,
	ActorPWM,
	ActorMotor,

}nodeType_t;

typedef enum{
	Alles_Fine,
	Not_Implemented,
	Value_too_high,
	Value_too_low,
	Parameter_error_high_low,
	Default_too_high,
	Default_too_low,
	Value_multiplier_equals_0,
	Updaterate_out_of_bounds,
	Illegal_State_Change_request,
	CAN_Error,
}Errorcodes_t;

typedef struct{
	uint32_t sendCAN:1;
	uint32_t sendConfig:1;
	uint32_t getCAN:1;
	uint32_t sendError:1;
	uint32_t myPin:1;		// indicates LED Status while debugging


}Flags_t;

typedef struct{
int16_t valueDefault;
int16_t valueMax;
int16_t valueMin;
int16_t valueOffset;
int16_t valueMultiplier_m;
uint8_t CanID;
uint8_t unit[8];
uint8_t name[8];
uint16_t updaterate_ms;
nodeType_t nodeType;
Errorcodes_t lastErrorcode;
}Constants_t;



typedef struct{
int16_t value;
int16_t valueSet;
int16_t valuePrev;
uint32_t time_ms;
uint32_t timeLastupdate_ms;
Flags_t flags;
}RuntimeData_t;

void InitDataHandler(void);

void StoreConstants(void);
void unlockFlash(void);
void eraseFlash(uint32_t page_addr);
void writeFlash(uint32_t flash_addr, uint16_t *data, uint16_t size);
void lockFlash(void);


#endif /* DATAHANDLER_H_ */
