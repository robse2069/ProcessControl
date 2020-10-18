/*
 * StateHandler.h
 *
 *  Created on: Oct 6, 2020
 *      Author: robert
 */

#ifndef STATEHANDLER_H_
#define STATEHANDLER_H_

#define InitComplete	0
#define RequestSetup	1
#define SetupComplete	2
#define SetLock			3
#define ReleaseLock		4
#define ErrorOccured	5





void Statehandler(uint8_t event);


#endif /* STATEHANDLER_H_ */
