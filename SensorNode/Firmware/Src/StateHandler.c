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
			if (DebugActive)
				print("Statechange: Init -> Running\n",29);
		}
		break;
	case SetLock:
		if (SystemState == Running) {
			SystemState = Locked;
			if (DebugActive)
				print("Statechange: Running -> Locked\n",31);
		}
		break;
	case ReleaseLock:
		if (SystemState == Locked) {
			SystemState = Running;
			if (DebugActive)
				print("Statechange: Locked-> Running\n",30);
		}
		break;
	case RequestSetup:
		if (SystemState == Running) {
			SystemState = Setup;
			if (DebugActive)
				print("Statechange: Running -> Setup\n",30);
		} else if (SystemState == Error) {
			SystemState = Setup;
			if (DebugActive)
				print("Statechange: Error -> Setup\n",28);
		}
		// If SystemState is Locked: Ths message is ignored
		break;
	case SetupComplete:
		if (SystemState == Setup) {
			SystemState = Init;
			if (DebugActive)
				print("Statechange: Setup -> Init\n",27);
		}
		break;
	case ErrorOccured:
		SystemState = Error;
		if (DebugActive)
			print("Statechange: Error was reported\n",28);
		break;
	default:
		//default to error if none of the statechanges above are met
		SystemState = Error;
		Constants.lastErrorcode = Illegal_State_Change_request;
		StoreConstants();
		if (DebugActive)
			print("Statechange: Illegal Statechange -> Error\n",38);

	}

}
