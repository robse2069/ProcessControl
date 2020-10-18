/*
 * DataHandler.h
 *
 *  Created on: Oct 15, 2020
 *      Author: robert
 */

#ifndef DATAHANDLER_H_
#define DATAHANDLER_H_

typedef enum{
	SensorNode,ActorNode,
}nodeType_t;

typedef enum{
	All_Fine,
	Value_too_high,
	Value_too_low,
	Parameter_error_high_low,
	Default_too_high,
	Default_too_low,
	Value_multiplier_equals_0,
	Updaterate_out_of_bounds,
	Illegal_State_Change_requested,

}Errorcodes_t;

typedef struct{
uint16_t valueDefault;
uint16_t valueMax;
uint16_t valueMin;
uint16_t valueOffset;
uint16_t valueMultiplier_m;
uint8_t CanID;
uint8_t unit[8];
uint8_t name[8];
uint16_t updaterate_ms;
nodeType_t nodeType;
Errorcodes_t lastErrorcode;
}Constants_t;



typedef struct{
uint16_t value;
uint16_t valueSet;
uint16_t valuePrev;
uint32_t time_ms;
uint32_t timeLastupdate_ms;
}RuntimeData_t;

void StoreConstants(void);

#endif /* DATAHANDLER_H_ */