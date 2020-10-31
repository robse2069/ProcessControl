/*
 * DataHandler.c
 *
 *  Created on: Oct 6, 2020
 *      Author: robert
 */

#include "DataHandler.h"
#include "Debug.h"
#include "string.h"
#include "StateHandler.h"

Constants_t Constants;
RuntimeData_t RuntimeData;

void InitDataHandler(void){
	//todo: read values from memory
#if DebugActive == 1
	Constants.valueDefault=0;
	Constants.valueMax=1000;
	Constants.valueMin=0;
	Constants.valueOffset=0;
	Constants.valueMultiplier_m=1000;
	Constants.CanID=0xa2;
	strcpy(Constants.unit,"Dummy");
	strcpy(Constants.name,"MySensor");
	Constants.updaterate_ms=500;
	Constants.nodeType=	SensorVoltage;
	Constants.lastErrorcode=All_Fine;

	RuntimeData.value=0;
	RuntimeData.valueSet=0;
	RuntimeData.valuePrev=0;
	RuntimeData.time_ms=0;
	RuntimeData.timeLastupdate_ms=0;

#else
	Constants.lastErrorcode=Not_Implemented;
	Statehandler(ErrorOccured);
#endif
}

void StoreConstants(void) {
#if DebugActive ==1
		print("Storing Constants to Flash\n", 27);
		print("Storing Constants to Flash is not yet implemented\n", 50);
#endif

}
