/*
 * Scheduler.c
 *
 *  Created on: Oct 27, 2020
 *      Author: robert
 */

#include "Scheduler.h"
#include "DataHandler.h"
#include "CanHandler.h"
#include "Debug.h"

extern Constants_t Constants;
extern RuntimeData_t RuntimeData;

void myscheduler(void){
RuntimeData.time_ms++;

	if (RuntimeData.time_ms >= RuntimeData.timeLastupdate_ms + Constants.updaterate_ms){
		RuntimeData.timeLastupdate_ms = RuntimeData.time_ms;
		RuntimeData.flags.sendCAN=1;

#if DebugActive == 1
//		RuntimeData.value++;
//		print("schedule\n",9 );
#endif
	}


}
