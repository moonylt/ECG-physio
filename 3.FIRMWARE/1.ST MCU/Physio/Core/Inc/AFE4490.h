/**
 * @file    AFE4490.h
 * @brief   AFE4490 pulse-oximeter driver (SPI4, PE2/PE4/PE5/PE6)
 *
 * Ported and simplified from the verified LPC177x project (F:\application\afe4490).
 * PDN is pulled up in hardware (U153), no software control needed; the 8.197MHz clock comes from TIM8_CH1.
 */
#ifndef __AFE4490_H
#define __AFE4490_H

#include "main.h"

/* AFE4490 register addresses */
#define AFE_CONTROL0      0x00
#define AFE_LED2STC       0x01
#define AFE_LED2ENDC      0x02
#define AFE_LED2LEDSTC    0x03
#define AFE_LED2LEDENDC   0x04
#define AFE_ALED2STC      0x05
#define AFE_ALED2ENDC     0x06
#define AFE_LED1STC       0x07
#define AFE_LED1ENDC      0x08
#define AFE_LED1LEDSTC    0x09
#define AFE_LED1LEDENDC   0x0A
#define AFE_ALED1STC      0x0B
#define AFE_ALED1ENDC     0x0C
#define AFE_LED2CONVST    0x0D
#define AFE_LED2CONVEND   0x0E
#define AFE_ALED2CONVST   0x0F
#define AFE_ALED2CONVEND  0x10
#define AFE_LED1CONVST    0x11
#define AFE_LED1CONVEND   0x12
#define AFE_ALED1CONVST   0x13
#define AFE_ALED1CONVEND  0x14
#define AFE_ADCRSTCNT0    0x15
#define AFE_ADCRSTENDCT0  0x16
#define AFE_ADCRSTCNT1    0x17
#define AFE_ADCRSTENDCT1  0x18
#define AFE_ADCRSTCNT2    0x19
#define AFE_ADCRSTENDCT2  0x1A
#define AFE_ADCRSTCNT3    0x1B
#define AFE_ADCRSTENDCT3  0x1C
#define AFE_PRPCOUNT      0x1D
#define AFE_CONTROL1      0x1E
#define AFE_TIAGAIN       0x20
#define AFE_TIA_AMB_GAIN  0x21
#define AFE_LEDCNTRL      0x22
#define AFE_CONTROL2      0x23
#define AFE_ALARM         0x29
#define AFE_LED2VAL       0x2A   /* LED2 (RED) latest sample */
#define AFE_ALED2VAL      0x2B
#define AFE_LED1VAL       0x2C   /* LED1 (IR)  latest sample */
#define AFE_ALED1VAL      0x2D
#define AFE_LED2ABSVAL    0x2E
#define AFE_LED1ABSVAL    0x2F
#define AFE_DIAG          0x30

void     AFE4490_Init(void);
void     AFE4490_WriteReg(uint8_t addr, uint32_t data);
uint32_t AFE4490_ReadReg(uint8_t addr);
void     AFE4490_ReadSample(int32_t *p_ir, int32_t *p_red);

#endif /* __AFE4490_H */
