/**
 * @file    AFE4490.c
 * @brief   AFE4490 pulse-oximeter front-end driver
 *
 * Register init sequence taken from the verified legacy LPC177x project
 * (working part only, commented-out debris removed).
 * SPI timing follows the ProtoCentral AFE44xx library: MODE0, MSB first,
 * write = [addr][24-bit data], read = [addr][3 dummy bytes].
 */

#include "AFE4490.h"
#include "spi.h"

/* STE (PE4) chip select: reconfigure from SPI4 hardware NSS to a manual GPIO output */
#define AFE_CS_LOW()   HAL_GPIO_WritePin(SPO2_STE_TO_MCU_GPIO_Port, SPO2_STE_TO_MCU_Pin, GPIO_PIN_RESET)
#define AFE_CS_HIGH()  HAL_GPIO_WritePin(SPO2_STE_TO_MCU_GPIO_Port, SPO2_STE_TO_MCU_Pin, GPIO_PIN_SET)

static void AFE_CS_Init(void)
{
    GPIO_InitTypeDef gpio = {0};
    gpio.Pin = SPO2_STE_TO_MCU_Pin;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    HAL_GPIO_WritePin(SPO2_STE_TO_MCU_GPIO_Port, SPO2_STE_TO_MCU_Pin, GPIO_PIN_SET);
    HAL_GPIO_Init(SPO2_STE_TO_MCU_GPIO_Port, &gpio);
}

static uint8_t AFE_SPI_Byte(uint8_t tx)
{
    uint8_t rx = 0;
    HAL_SPI_TransmitReceive(&hspi4, &tx, &rx, 1, 1);
    return rx;
}

void AFE4490_WriteReg(uint8_t addr, uint32_t data)
{
    AFE_CS_LOW();
    AFE_SPI_Byte(addr);
    AFE_SPI_Byte((data >> 16) & 0xFF);
    AFE_SPI_Byte((data >> 8) & 0xFF);
    AFE_SPI_Byte(data & 0xFF);
    AFE_CS_HIGH();
}

uint32_t AFE4490_ReadReg(uint8_t addr)
{
    uint32_t data;
    AFE_CS_LOW();
    AFE_SPI_Byte(addr);
    data  = (uint32_t)AFE_SPI_Byte(0x00) << 16;
    data |= (uint32_t)AFE_SPI_Byte(0x00) << 8;
    data |= AFE_SPI_Byte(0x00);
    AFE_CS_HIGH();
    return data;
}

/**
 * @brief Read one PPG sample (22-bit two's complement -> sign-extended int32)
 * @note  ProtoCentral reference timing: write CONTROL0=0x1 before reading
 */
static int32_t AFE_ReadVal22(uint8_t addr)
{
    uint32_t v;
    AFE4490_WriteReg(AFE_CONTROL0, 0x000001);
    v = AFE4490_ReadReg(addr);
    v = (v << 10);              /* sign-extend 22-bit two's complement */
    return (int32_t)v >> 10;
}

void AFE4490_ReadSample(int32_t *p_ir, int32_t *p_red)
{
    *p_ir  = AFE_ReadVal22(AFE_LED1VAL);
    *p_red = AFE_ReadVal22(AFE_LED2VAL);
}

void AFE4490_Init(void)
{
    AFE_CS_Init();

    /* Soft reset */
    AFE4490_WriteReg(AFE_CONTROL0, 0x000000);
    HAL_Delay(10);
    AFE4490_WriteReg(AFE_CONTROL0, 0x000008);
    HAL_Delay(10);
    AFE4490_WriteReg(AFE_CONTROL0, 0x000000);
    HAL_Delay(10);

    /* Analog front end: TIA CF=5pF RF=500k, LED current ~50mA */
    AFE4490_WriteReg(AFE_TIAGAIN,      0x000000);
    AFE4490_WriteReg(AFE_TIA_AMB_GAIN, 0x000000);
    AFE4490_WriteReg(AFE_LEDCNTRL,     0x001405);
    AFE4490_WriteReg(AFE_CONTROL2,     0x000000);
    /* Timers on, 3-sample averaging */
    AFE4490_WriteReg(AFE_CONTROL1,     0x010707);
    AFE4490_WriteReg(AFE_PRPCOUNT,     0x001F3F);

    /* Sampling windows (verified values; 8.197MHz clock -> PRF ~1kHz, four phases per period) */
    AFE4490_WriteReg(AFE_LED2STC,      0x001770);
    AFE4490_WriteReg(AFE_LED2ENDC,     0x001F3E);
    AFE4490_WriteReg(AFE_LED2LEDSTC,   0x001770);
    AFE4490_WriteReg(AFE_LED2LEDENDC,  0x001F3F);
    AFE4490_WriteReg(AFE_ALED2STC,     0x000000);
    AFE4490_WriteReg(AFE_ALED2ENDC,    0x0007CE);
    AFE4490_WriteReg(AFE_LED2CONVST,   0x000002);
    AFE4490_WriteReg(AFE_LED2CONVEND,  0x0007CF);
    AFE4490_WriteReg(AFE_ALED2CONVST,  0x0007D2);
    AFE4490_WriteReg(AFE_ALED2CONVEND, 0x000F9F);

    AFE4490_WriteReg(AFE_LED1STC,      0x0007D0);
    AFE4490_WriteReg(AFE_LED1ENDC,     0x000F9E);
    AFE4490_WriteReg(AFE_LED1LEDSTC,   0x0007D0);
    AFE4490_WriteReg(AFE_LED1LEDENDC,  0x000F9F);
    AFE4490_WriteReg(AFE_ALED1STC,     0x000FA0);
    AFE4490_WriteReg(AFE_ALED1ENDC,    0x00176E);
    AFE4490_WriteReg(AFE_LED1CONVST,   0x000FA2);
    AFE4490_WriteReg(AFE_LED1CONVEND,  0x00176F);
    AFE4490_WriteReg(AFE_ALED1CONVST,  0x001772);
    AFE4490_WriteReg(AFE_ALED1CONVEND, 0x001F3F);

    AFE4490_WriteReg(AFE_ADCRSTCNT0,   0x000000);
    AFE4490_WriteReg(AFE_ADCRSTENDCT0, 0x000000);
    AFE4490_WriteReg(AFE_ADCRSTCNT1,   0x0007D0);
    AFE4490_WriteReg(AFE_ADCRSTENDCT1, 0x0007D0);
    AFE4490_WriteReg(AFE_ADCRSTCNT2,   0x000FA0);
    AFE4490_WriteReg(AFE_ADCRSTENDCT2, 0x000FA0);
    AFE4490_WriteReg(AFE_ADCRSTCNT3,   0x001770);
    AFE4490_WriteReg(AFE_ADCRSTENDCT3, 0x001770);

    HAL_Delay(10);
    AFE4490_WriteReg(AFE_CONTROL0, 0x000001);   /* start count timers */
    HAL_Delay(100);
}
