/*
 * StateHandler.h
 *
 *  Created on: Oct 6, 2020
 *      Author: robert
 */

#ifndef STATEHANDLER_H_
#define STATEHANDLER_H_




typedef enum {
	Init, Setup, Running, Locked, Error,
} SystemState_t;

typedef enum{
	InitComplete,
	RequestSetup,
	SetupComplete,
	SetLock,
	ReleaseLock,
	ErrorOccured,

}Events_t;



void Statehandler(Events_t event);


#endif /* STATEHANDLER_H_ */
