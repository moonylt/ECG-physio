/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
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
#include "stm32f4xx_hal.h"

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
#define SPO2_SCLK_TO_MCU_Pin GPIO_PIN_2
#define SPO2_SCLK_TO_MCU_GPIO_Port GPIOE
#define EN_TO_MCU_Pin GPIO_PIN_3
#define EN_TO_MCU_GPIO_Port GPIOE
#define SPO2_STE_TO_MCU_Pin GPIO_PIN_4
#define SPO2_STE_TO_MCU_GPIO_Port GPIOE
#define SPO2_SOMI_TO_MCU_Pin GPIO_PIN_5
#define SPO2_SOMI_TO_MCU_GPIO_Port GPIOE
#define SPO2_SIMO_TO_MCU_Pin GPIO_PIN_6
#define SPO2_SIMO_TO_MCU_GPIO_Port GPIOE
#define I2C2_SDA_Pin GPIO_PIN_0
#define I2C2_SDA_GPIO_Port GPIOF
#define TX_TRIG_Pin GPIO_PIN_4
#define TX_TRIG_GPIO_Port GPIOF
#define USM_SSEL_Pin GPIO_PIN_6
#define USM_SSEL_GPIO_Port GPIOF
#define USM_SCK_Pin GPIO_PIN_7
#define USM_SCK_GPIO_Port GPIOF
#define USM_MISO_Pin GPIO_PIN_8
#define USM_MISO_GPIO_Port GPIOF
#define USM_MOSI_Pin GPIO_PIN_9
#define USM_MOSI_GPIO_Port GPIOF
#define TC_MISO_Pin GPIO_PIN_2
#define TC_MISO_GPIO_Port GPIOC
#define TC_MOSI_Pin GPIO_PIN_3
#define TC_MOSI_GPIO_Port GPIOC
#define FT_RTS1_Pin GPIO_PIN_0
#define FT_RTS1_GPIO_Port GPIOA
#define RECTAL_TEMP_Pin GPIO_PIN_1
#define RECTAL_TEMP_GPIO_Port GPIOA
#define MONI_12V_Pin GPIO_PIN_2
#define MONI_12V_GPIO_Port GPIOA
#define MONI_3V3_Pin GPIO_PIN_3
#define MONI_3V3_GPIO_Port GPIOA
#define DAC_OUT_Pin GPIO_PIN_4
#define DAC_OUT_GPIO_Port GPIOA
#define DAC_OUT1_Pin GPIO_PIN_5
#define DAC_OUT1_GPIO_Port GPIOA
#define MONI_5V_Pin GPIO_PIN_6
#define MONI_5V_GPIO_Port GPIOA
#define ECG_RDY_Pin GPIO_PIN_0
#define ECG_RDY_GPIO_Port GPIOG
#define ECG_RDY_EXTI_IRQn EXTI0_IRQn
#define ADC_RDY_TO_MCU_Pin GPIO_PIN_1
#define ADC_RDY_TO_MCU_GPIO_Port GPIOG
#define ADC_RDY_TO_MCU_EXTI_IRQn EXTI1_IRQn
#define WIFI_TXD0_Pin GPIO_PIN_7
#define WIFI_TXD0_GPIO_Port GPIOE
#define WIFI_RXD0_Pin GPIO_PIN_8
#define WIFI_RXD0_GPIO_Port GPIOE
#define MCU_ECG_CLK_Pin GPIO_PIN_9
#define MCU_ECG_CLK_GPIO_Port GPIOE
#define C596_SRCK_Pin GPIO_PIN_10
#define C596_SRCK_GPIO_Port GPIOE
#define C596_SERIN_Pin GPIO_PIN_11
#define C596_SERIN_GPIO_Port GPIOE
#define C596_CLR__Pin GPIO_PIN_12
#define C596_CLR__GPIO_Port GPIOE
#define C596_RCK_Pin GPIO_PIN_13
#define C596_RCK_GPIO_Port GPIOE
#define EXT_SW_Pin GPIO_PIN_14
#define EXT_SW_GPIO_Port GPIOE
#define INV_SW_Pin GPIO_PIN_15
#define INV_SW_GPIO_Port GPIOE
#define TC_SCK_Pin GPIO_PIN_10
#define TC_SCK_GPIO_Port GPIOB
#define FT_TXD0_Pin GPIO_PIN_11
#define FT_TXD0_GPIO_Port GPIOB
#define TC_SSEL_Pin GPIO_PIN_12
#define TC_SSEL_GPIO_Port GPIOB
#define FT_RTS0_Pin GPIO_PIN_13
#define FT_RTS0_GPIO_Port GPIOB
#define FT_CTS0_Pin GPIO_PIN_14
#define FT_CTS0_GPIO_Port GPIOB
#define FT_RXD0_Pin GPIO_PIN_8
#define FT_RXD0_GPIO_Port GPIOD
#define SW_BT_Pin GPIO_PIN_2
#define SW_BT_GPIO_Port GPIOG
#define ECG_SSEL_Pin GPIO_PIN_8
#define ECG_SSEL_GPIO_Port GPIOG
#define MCU_8M_BACKUP_Pin GPIO_PIN_6
#define MCU_8M_BACKUP_GPIO_Port GPIOC
#define MCU_8M_Pin GPIO_PIN_8
#define MCU_8M_GPIO_Port GPIOA
#define SPO2_DET_Pin GPIO_PIN_11
#define SPO2_DET_GPIO_Port GPIOA
#define DAC_SCLK_Pin GPIO_PIN_10
#define DAC_SCLK_GPIO_Port GPIOC
#define DAC_SDO_Pin GPIO_PIN_11
#define DAC_SDO_GPIO_Port GPIOC
#define WIFI_RXD2_Pin GPIO_PIN_12
#define WIFI_RXD2_GPIO_Port GPIOC
#define WIFI_RXD2D2_Pin GPIO_PIN_2
#define WIFI_RXD2D2_GPIO_Port GPIOD
#define FT_CTS1_Pin GPIO_PIN_4
#define FT_CTS1_GPIO_Port GPIOD
#define FT_RXD1_Pin GPIO_PIN_5
#define FT_RXD1_GPIO_Port GPIOD
#define FT_TXD1_Pin GPIO_PIN_6
#define FT_TXD1_GPIO_Port GPIOD
#define ECG_MISO_Pin GPIO_PIN_12
#define ECG_MISO_GPIO_Port GPIOG
#define ECG_SCK_Pin GPIO_PIN_13
#define ECG_SCK_GPIO_Port GPIOG
#define ECG_MOSI_Pin GPIO_PIN_14
#define ECG_MOSI_GPIO_Port GPIOG
#define DAC_SDI_Pin GPIO_PIN_5
#define DAC_SDI_GPIO_Port GPIOB
#define DAC_CS_Pin GPIO_PIN_7
#define DAC_CS_GPIO_Port GPIOB
#define IO0_TO_MCU_Pin GPIO_PIN_8
#define IO0_TO_MCU_GPIO_Port GPIOB
#define WIFI_TXD1_Pin GPIO_PIN_0
#define WIFI_TXD1_GPIO_Port GPIOE
#define WIFI_TXD0E1_Pin GPIO_PIN_1
#define WIFI_TXD0E1_GPIO_Port GPIOE

/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
