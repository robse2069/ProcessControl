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
#include "stm32f0xx.h"

Constants_t Constants;
RuntimeData_t RuntimeData;

void InitDataHandler(void) {

	/* read Flash section which holds the
	 * Constants while node is shut down
	 *
	 * Warning: The write cycle is not protected in any way.
	 * Corruption of Flash memory is possible due to power down while
	 * writing, etc etc.
	 *
	 * todo: add some protective measures to improve reliability
	 * */

	// address of flash page 31
	uint16_t *FlashMem = (uint16_t *) 0x08007C00;

	Constants.valueDefault = FlashMem[0];
	Constants.valueMax = FlashMem[1];
	Constants.valueMin = FlashMem[2];
	Constants.valueOffset = FlashMem[3];
	Constants.valueMultiplier_m = FlashMem[4];
	Constants.CanID = FlashMem[5];

	for (uint8_t count = 0; count < 4; count++) {
		Constants.unit[count * 2] = (uint8_t) (FlashMem[6 + count] & 0xFF);
		Constants.unit[count * 2 + 1] = (uint8_t) ((FlashMem[6 + count] >> 8) & 0xFF);
	}
	for (uint8_t count = 0; count < 4; count++) {
		Constants.name[count * 2] = (uint8_t) (FlashMem[10 + count] & 0xFF);
		Constants.name[count * 2 + 1] = (uint8_t) ((FlashMem[10 + count] >> 8) & 0xFF);
	}
	Constants.updaterate_ms = FlashMem[8];
	Constants.nodeType = FlashMem[9];
	Constants.lastErrorcode = FlashMem[10];

	// initialize runtime data
	RuntimeData.value = 0;
	RuntimeData.valueSet = Constants.valueDefault;
	RuntimeData.valuePrev = 0;
	RuntimeData.time_ms = 0;
	RuntimeData.timeLastupdate_ms = 0;

}

void StoreConstants(void) {

	uint16_t dataFromConstants[17];

	dataFromConstants[0] = Constants.valueDefault;
	dataFromConstants[1] = Constants.valueMax;
	dataFromConstants[2] = Constants.valueMin;
	dataFromConstants[3] = Constants.valueOffset;
	dataFromConstants[4] = Constants.valueMultiplier_m;
	dataFromConstants[5] = Constants.CanID;
	dataFromConstants[6] = (Constants.unit[1] << 8) | Constants.unit[0];
	dataFromConstants[7] = (Constants.unit[3] << 8) | Constants.unit[2];
	dataFromConstants[8] = (Constants.unit[5] << 8) | Constants.unit[4];
	dataFromConstants[9] = (Constants.unit[7] << 8) | Constants.unit[6];
	dataFromConstants[10] = (Constants.name[0] << 8) | Constants.name[1];
	dataFromConstants[11] = (Constants.name[2] << 8) | Constants.name[3];
	dataFromConstants[12] = (Constants.name[4] << 8) | Constants.name[5];
	dataFromConstants[13] = (Constants.name[6] << 8) | Constants.name[7];
	dataFromConstants[14] = Constants.updaterate_ms;
	dataFromConstants[15] = Constants.nodeType;
	dataFromConstants[16] = Constants.lastErrorcode;

	unlockFlash();
	eraseFlash(0x08007C00); // Page 31
	writeFlash(0x08007C00, dataFromConstants, 17);
	lockFlash();

}

void unlockFlash(void) {
	//keys as described in the data-sheets
#define FLASH_FKEY1 0x45670123
#define FLASH_FKEY2 0xCDEF89AB
	// Wait for the flash memory not to be busy
	while ((FLASH->SR & FLASH_SR_BSY) != 0)
		;
	// Check if the controller is unlocked already
	if ((FLASH->CR & FLASH_CR_LOCK) != 0) {
		// Write the first key
		FLASH->KEYR = FLASH_FKEY1;
		// Write the second key
		FLASH->KEYR = FLASH_FKEY2;
	}
}

void eraseFlash(uint32_t page_addr) {
	// Wait until the flash is no longer busy
	while ((FLASH->SR & FLASH_SR_BSY) != 0)
		;

	FLASH->CR |= FLASH_CR_PER; // Page erase operation
	FLASH->AR = page_addr;     // Set the address to the page to be written
	FLASH->CR |= FLASH_CR_STRT;     // Start the page erase

	// Wait until page erase is done
	while ((FLASH->SR & FLASH_SR_BSY) != 0)
		;
	// If the end of operation bit is set...
	if ((FLASH->SR & FLASH_SR_EOP) != 0) {
		// Clear it, the operation was successful
		FLASH->SR |= FLASH_SR_EOP;
	}
	//Otherwise there was an error
	else {
		// Manage the error cases
	}
	// Get out of page erase mode
	FLASH->CR &= ~FLASH_CR_PER;
}

void writeFlash(uint32_t flash_addr, uint16_t *data, uint16_t size) {
	FLASH->CR |= FLASH_CR_PG;                   // Programing mode

	for (uint16_t offset = 0; offset < size; offset++) {
		*(__IO uint16_t*) (flash_addr + offset * 2) = data[offset]; // Write data
	}
	// Wait until the end of the operation
	while ((FLASH->SR & FLASH_SR_BSY) != 0)
		;
	// If the end of operation bit is set...
	if ((FLASH->SR & FLASH_SR_EOP) != 0) {
		// Clear it, the operation was successful
		FLASH->SR |= FLASH_SR_EOP;
	}
	//Otherwise there was an error
	else {
		// Manage the error cases
	}
	FLASH->CR &= ~FLASH_CR_PG;
}

void lockFlash(void) {
	FLASH->CR |= FLASH_CR_LOCK;
}

/*
 * Notes:
 * flash page addresses: Page 55 Table 4
 *
 * Memory map
 * 	0x4002 2000 - 0x4002 23FF 1 KB FLASH interface
 * 	0x0800 0000 - 0x0801 7FFF 32 KB Main Flash memory
 *
 * Page 31: 0x0800 7C00 .. 0x0800 7FFF
 *
 * to research: what kind of address does FLASH_AR take?
 * -> Base Address + Offset
 * start address of every page (offset + 1024)
 * -> 0x0800 7C00?
 *
 *
 * RDP: Read protection register
 *
 *
 * */
