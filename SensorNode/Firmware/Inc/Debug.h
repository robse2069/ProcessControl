/*
 * Debug.h
 *
 *  Created on: Oct 15, 2020
 *      Author: robert
 */

#ifndef DEBUG_H_
#define DEBUG_H_

#include "stdint.h"

#define DebugActive 1


//void print(uint8_t* string, uint8_t len);
void DecodeDebugMessage(uint8_t *debugmessage);

#endif /* DEBUG_H_ */
