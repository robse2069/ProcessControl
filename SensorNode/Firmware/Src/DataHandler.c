/*
 * DataHandler.c
 *
 *  Created on: Oct 6, 2020
 *      Author: robert
 */

#include "DataHandler.h"
#include "Debug.h"

Constants_t Constants;
RuntimeData_t RuntimeData;

void StoreConstants(void) {
#if DebugActive ==1
		print("Storing Constants to Flash\n", 27);
		print("Storing Constants to Flash is not yet implemented\n", 50);
#endif

}
