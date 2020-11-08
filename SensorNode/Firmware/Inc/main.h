/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2020 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under BSD 3-Clause license,
  * the "License"; You may not use this file except in compliance with the
  * License. You may obtain a copy of the License at:
  *                        opensource.org/licenses/BSD-3-Clause
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f1xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define B1_Pin GPIO_PIN_13
#define B1_GPIO_Port GPIOC
#define IN_A_Meas1_Pin GPIO_PIN_0
#define IN_A_Meas1_GPIO_Port GPIOA
#define IN_A_Meas2_Pin GPIO_PIN_1
#define IN_A_Meas2_GPIO_Port GPIOA
#define UART_Tx_Pin GPIO_PIN_2
#define UART_Tx_GPIO_Port GPIOA
#define UART_Rx_Pin GPIO_PIN_3
#define UART_Rx_GPIO_Port GPIOA
#define IN_A_HW_Version_Pin GPIO_PIN_4
#define IN_A_HW_Version_GPIO_Port GPIOA
#define LD2_Pin GPIO_PIN_5
#define LD2_GPIO_Port GPIOA
#define OUT_D_Actor1_Pin GPIO_PIN_6
#define OUT_D_Actor1_GPIO_Port GPIOA
#define OUT_D_Green_N_Pin GPIO_PIN_14
#define OUT_D_Green_N_GPIO_Port GPIOB
#define OUT_D_Red_N_Pin GPIO_PIN_15
#define OUT_D_Red_N_GPIO_Port GPIOB
#define OUT_D_Trigger_Pin GPIO_PIN_8
#define OUT_D_Trigger_GPIO_Port GPIOC
#define CAN_Rx_Pin GPIO_PIN_11
#define CAN_Rx_GPIO_Port GPIOA
#define CAN_Tx_Pin GPIO_PIN_12
#define CAN_Tx_GPIO_Port GPIOA
#define TMS_Pin GPIO_PIN_13
#define TMS_GPIO_Port GPIOA
#define TCK_Pin GPIO_PIN_14
#define TCK_GPIO_Port GPIOA
#define SWO_Pin GPIO_PIN_3
#define SWO_GPIO_Port GPIOB
/* USER CODE BEGIN Private defines */
#define ERROR_ALL_FINE					0
#define ERROR_VALUE_TOO_HIGH			1
#define ERROR_VALUE_TOO_LOW				2
#define ERROR_PARAM_HIGH_LOW			3
#define ERROR_DEFAULT_TOO_HIGH			4
#define ERROR_DEFAULT_TOO_LOW			5
#define ERROR_VALUE_MULTIPLIER_ZERO		6
#define ERROR_UPDATERATE				7
#define ERROR_ILLEGAL_STATE_CHANCE		8

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
