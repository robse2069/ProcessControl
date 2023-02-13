/*
 * StateHandler.c
 *
 *  Created on: Oct 6, 2020
 *      Author: robert
 */

#include "StateHandler.h"
#include "Debug.h"
#include "DataHandler.h"
#include "main.h"

extern Constants_t Constants;


SystemState_t SystemState;

void Statehandler(uint8_t event) {

	switch (event) {
	case InitComplete:
		if (SystemState == Init) {
			SystemState = Running;
		}
		// todo: All if-clauses need an else-statement to detect illegal state change requests.
		break;
	case SetLock:
		if (SystemState == Running) {
			SystemState = Locked;
		}
		break;
	case ReleaseLock:
		if (SystemState == Locked) {
			SystemState = Running;
		}
		break;
	case RequestSetup:
		if ((SystemState == Running) | (SystemState == Setup)) {
			SystemState = Setup;
		} else if (SystemState == Error) {
			SystemState = Setup;
		}
		// If SystemState is Locked: Ths message is ignored
		break;
	case SetupComplete:
		if (SystemState == Setup) {
			SystemState = Running;
		}
		break;
	case ErrorOccured:
		SystemState = Error;
		break;
	default:
		//default to error if none of the statechanges above are met
		SystemState = Error;
		Constants.lastErrorcode = Illegal_State_Change_request;
		StoreConstants();

	}

}
