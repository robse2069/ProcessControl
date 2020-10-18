/*
 * StateHandler.c
 *
 *  Created on: Oct 6, 2020
 *      Author: robert
 */
#include "StateHandler.h"
#include "DataHandler.h"
#include "main.h"
#include "Debug.h"

extern Constants_t Constants;

enum {
	Init, Setup, Running, Locked, Error,
} SystemState;

void Statehandler(uint8_t event) {

	switch (event) {
	case InitComplete:
		if (SystemState == Init) {
			SystemState = Running;
			if (DebugActive)
				print("Statechange: Init -> Running\n");
		}
		break;
	case SetLock:
		if (SystemState == Running) {
			SystemState = Locked;
			if (DebugActive)
				print("Statechange: Running -> Locked\n");
		}
		break;
	case ReleaseLock:
		if (SystemState == Locked) {
			SystemState = Running;
			if (DebugActive)
				print("Statechange: Locked-> Running\n");
		}
		break;
	case RequestSetup:
		if (SystemState == Running) {
			SystemState = Setup;
			if (DebugActive)
				print("Statechange: Running -> Setup\n");
		} else if (SystemState == Error) {
			SystemState = Setup;
			if (DebugActive)
				print("Statechange: Error -> Setup\n");
		}
		break;
	case SetupComplete:
		if (SystemState == Setup) {
			SystemState = Init;
			if (DebugActive)
				print("Statechange: Setup -> Init\n");
		}
		break;
	case Error:
		SystemState = Error;
		if (DebugActive)
			print("Statechange: Error was reported\n");
		break;
	default:
		//default to error if none of the statechanges above are met
		SystemState = Error;
		Constants.lastErrorcode = Illegal_State_Change_requested;
		StoreConstants();
		if (DebugActive)
			print("Statechange: Illegal Statechange -> Error\n");

	}

}
