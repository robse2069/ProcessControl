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
#include "StateHandler.h"

extern Constants_t Constants;
extern RuntimeData_t RuntimeData;
extern SystemState_t SystemState;

void myscheduler(void) {
	RuntimeData.time_ms++;

	if (RuntimeData.time_ms
			>= RuntimeData.timeLastupdate_ms + Constants.updaterate_ms) {
		if (SystemState == Running || SystemState == Locked || SystemState == Setup) {
			RuntimeData.timeLastupdate_ms = RuntimeData.time_ms;
			RuntimeData.flags.sendCAN = 1;
		}
#if DebugActive == 1
//		RuntimeData.value++;	// dont use, doesnt work anymore.
//		print("schedule\n",9 );
#endif
	}
	if (RuntimeData.time_ms >= RuntimeData.timeLastupdate_ms + 10) {
		// executed every 10 ms
//		if (SystemState == Setup || SystemState == Running) {
//			RuntimeData.flags.sendConfig;
//		}
	}

}
