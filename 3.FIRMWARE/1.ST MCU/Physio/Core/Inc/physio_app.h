/**
 * @file    physio_app.h
 * @brief   PHYSIO application layer: acquisition/simulated sources -> protocol frames -> UART5 -> ESP32 -> PC console
 *
 * Data path:
 *   [ECG  ADS1298R/SIM ] --+
 *   [SpO2 AFE4490/SIM  ] --+-> physio_app -> PROTOCOL v2 frame -> UART5 -> ESP32 -> TCP -> PC
 *   [Temp TMP117/MAX31856]┘
 *
 * Bring-up order: run PHYSIO_SIM_MODE=1 first to validate the console link, then switch to 0 for real acquisition.
 */
#ifndef __PHYSIO_APP_H
#define __PHYSIO_APP_H

#include "main.h"

/* 1 = transmit hardcoded simulated data after power-up (no sensors needed, used to validate the console link)
 * 0 = real acquisition (ADS1298R EXTI0 / AFE4490 EXTI1 / TMP117 / MAX31856)
 * Can be overridden on the build command line: python build.py SIM=0 */
#ifndef PHYSIO_SIM_MODE
#define PHYSIO_SIM_MODE   1
#endif

void physio_app_init(void);
void physio_app_poll(void);

/* Real-mode ISR entry points (no-ops in simulation mode) */
void physio_app_ecg_from_isr(const uint8_t ads_raw[27]);
void physio_app_spo2_from_isr(void);

#endif /* __PHYSIO_APP_H */
