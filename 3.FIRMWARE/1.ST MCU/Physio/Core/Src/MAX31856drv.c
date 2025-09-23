
//// *  ------------------------------------------------------------------------- */
///*
// * Copyright (C) 2012 Maxim Integrated Products, Inc., All Rights Reserved.
// *
// * Permission is hereby granted, free of charge, to any person obtaining a
// * copy of this software and associated documentation files (the "Software"),
// * to deal in the Software without restriction, including without limitation
// * the rights to use, copy, modify, merge, publish, distribute, sublicense,
// * and/or sell copies of the Software, and to permit persons to whom the
// * Software is furnished to do so, subject to the following conditions:
// *
// * The above copyright notice and this permission notice shall be included
// * in all copies or substantial portions of the Software.
// *
// * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
// * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
// * MERCHANTABILITY,  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
// * IN NO EVENT SHALL MAXIM INTEGRATED PRODUCTS BE LIABLE FOR ANY CLAIM, DAMAGES
// * OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
// * ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
// * OTHER DEALINGS IN THE SOFTWARE.
// *
// * Except as contained in this notice, the name of Maxim Integrated Products
// * shall not be used except as stated in the Maxim Integrated Products
// * Branding Policy.
// *
// * The mere transfer of this software does not imply any licenses
// * of trade secrets, proprietary technology, copyrights, patents,
// * trademarks, maskwork rights, or any other form of intellectual
// * property whatsoever. Maxim Integrated Products retains all ownership rights.
// *
// ***************************************************************************/
// 
///** \file max31856drv.c ******************************************************
// *
// *             Project: max31856
// *            Filename: max31856drv.c
// *         Description: This module contains the Main application for the max31856 example program.
// *
// *    Revision History:
// *\n                    23-12-15    Rev 1.0.0    TTS    Initial release.
// *\n                                             TTS    Re-release.
// *\n                    		
// *
// *  --------------------------------------------------------------------
// *
// *  This code follows the following naming conventions:
// *
// *\n    char                    	ch_pmod_value
// *\n    char (array)            s_pmod_string[16]
// *\n    float                  	 f_pmod_value
// *\n    int                    	 n_pmod_value
// *\n    int (array)             	an_pmod_value[16]
// *\n    u16                     	u_pmod_value
// *\n    u16 (array)             au_pmod_value[16]
// *\n    u8                     	 uch_pmod_value
// *\n    u8 (array)              	auch_pmod_buffer[16]
// *\n    unsigned int     	un_pmod_value
// *\n    int *                   	pun_pmod_value
// *




///*---------------------------------------------------------------*/

#include "MAX31856drv.h"
#include "spi.h"


//define
#define SSEL_LOW HAL_GPIO_WritePin(GPIOB, TC_SSEL_Pin, GPIO_PIN_RESET)
#define SSEL_HIGH HAL_GPIO_WritePin(GPIOB, TC_SSEL_Pin, GPIO_PIN_SET)



uint8_t uch_cr0,uch_cr1,uch_mask;

uint8_t uch_reg[8],tc_val;
uint8_t uch_cjth,uch_cjtl,uch_ltcbh,uch_ltcbm,uch_ltcbl,uch_sr;
uint32_t temperature_value;

char s[64];
float  f_cold_junction_temperature, f_linearized_tc_temperature;

void maxim_31856_write_register(uint8_t uch_register_address, uint8_t uch_register_value)
{
////  SPI_CS_LOW;
////  SPI_WriteByte(uch_register_address);
////  SPI_WriteByte(uch_register_value);
////  SPI_CS_HIGH; 
//	
//			SPI_FLASH_CS_LOW()
////	  DelayMs(1);
//    ssp_xfer_byte(uch_register_address);	

//		ssp_xfer_byte(uch_register_value);
////		DelayMs(1);
//	  SPI_FLASH_CS_HIGH();
	
	
		SSEL_LOW;
//		SPI_Send_Dat(uch_register_address);
		HAL_SPI_Transmit (&hspi2, &uch_register_address, 1, 10);
//		SPI_Send_Dat(uch_register_value);
		HAL_SPI_Transmit (&hspi2, &uch_register_value, 1, 10);
		SSEL_HIGH;
}

uint8_t maxim_31856_read_register(uint8_t uch_register_address)
{
  uint8_t uch_register_data;
  
////  SPI_CS_LOW;
////  SPI_WriteByte(uch_register_address);
////  uch_register_data=SPI_ReadByte();
////  SPI_CS_HIGH;
//	
////		u32 data =0;
////		u8 d1,d2,d3;
//		SPI_FLASH_CS_LOW()
////	  DelayMs(1);
//    ssp_xfer_byte(uch_register_address);	
////	  DelayMs(5);
////			d1=ssp_xfer_byte(0x00);	
////			d2=ssp_xfer_byte(0x00);
////			d3=ssp_xfer_byte(0x00);
////	  data=(d1<<16)|(d2<<8)|(d3);
//			uch_register_data=ssp_xfer_byte(0x00);
//		  SPI_FLASH_CS_HIGH();
////		return data;
	
		SSEL_LOW;
//		SPI_Send_Dat(uch_register_address);
		HAL_SPI_Transmit (&hspi2, &uch_register_address, 1, 10);
//		uch_register_data=SPI_Receiver_Dat();
		HAL_SPI_Receive ( &hspi2, &uch_register_data, 1, 10);
		
		SSEL_HIGH;
	
	
	
	
	
  return (uch_register_data);
  
}
void maxim_31856_read_nregisters(uint8_t uch_register_address, uint8_t *uch_buff,uint8_t uch_nBytes)
{
// SPI_CS_LOW;
// SPI_WriteByte(uch_register_address);
// SPI_Read(uch_buff,uch_nBytes);
// SPI_CS_HIGH;
		uint8_t i;
//		SPI_FLASH_CS_LOW()
////	  DelayMs(1);
//    ssp_xfer_byte(uch_register_address);	
//		for(i=0;i<uch_nBytes;i++)
//		{
//			*uch_buff=ssp_xfer_byte(0x00);
//			uch_buff++;
//		}
//		  SPI_FLASH_CS_HIGH();
		
		SSEL_LOW;
//		SPI_Send_Dat(uch_register_address);
		HAL_SPI_Transmit (&hspi2, &uch_register_address, 1, 10);
				for(i=0;i<uch_nBytes;i++)
		{
//			*uch_buff=SPI_Receiver_Dat();
			HAL_SPI_Receive ( &hspi2, uch_buff, 1, 10);
			uch_buff++;
		}
		
		SSEL_HIGH;
}

void maxim_31856_init(void)
{

   //使能故障检测，选择50Hz滤波   故障模式采用中断模式
   uch_cr0= OC_Fault_Enable_1|NRF_50Hz| Interrupt_Mode;  //配置CR0
   //由于采用单次测量模式，因此设置每次测量输出结果。热电偶选择T型热电偶
   uch_cr1&= Average_1_Bit ;
   uch_cr1|=TC_TypeT;
   //由于使能故障检测，因此，不屏蔽任何的故障检测，可以根据要求选择屏蔽掉不需要检测的故障
   uch_mask=0xFE ;//FAULT PIN assert when thermocouple open
   
   maxim_31856_write_register(0x80, uch_cr0);  //设置CR0
   maxim_31856_write_register(0x81, uch_cr1);  //设置CR1
   maxim_31856_write_register(0x82,uch_mask);  //设置MASK
   
   //写冷端故障门限寄存器，可根据需要设置
   maxim_31856_write_register(0x83,0x7F);
   maxim_31856_write_register(0x84,0xC0);
   //写热电偶故障门限寄存器，可根据需要设置
   maxim_31856_write_register(0x85,0x7F);
   maxim_31856_write_register(0x86,0xFF);
   maxim_31856_write_register(0x87,0x80);
   maxim_31856_write_register(0x88,0x00);
   //写冷端温度失调寄存器，可根据需要设置
   maxim_31856_write_register(0x89,0x00);
   //如果禁止使用器件内部冷端补偿，写冷端温度寄存器，可根据需要设置
   //如果采用外部冷端温度传感器测量冷端温度，需要在每次测量冷端温度后更新
   //冷端温度寄存器。
   maxim_31856_write_register(0x8A,0x00);
   maxim_31856_write_register(0x8B,0x00);
  
}
/*****************************************************

CR0 Bit operation
******************************************************/
void maxim_stop_conversion(void)
{
  uch_cr0= maxim_31856_read_register(0x00);
  uch_cr0&=Stop_Conversion_Bit;
  maxim_31856_write_register(0x80, uch_cr0);
}
/****************************************************

Start_Conversion: used to start conversion.

Conversion Mode can be One_Shot_ Conversion or Automatic_Conversion

 the define of One_Shot_ Conversion or Automatic_Conversion
 please see MAX31856drv.h
*****************************************************/
void maxim_start_conversion(uint8_t uch_conversion_mode)  
{
 uch_cr0=maxim_31856_read_register(0x00);
 uch_cr0&=Stop_Conversion_Bit;
 uch_cr0|=uch_conversion_mode;
 maxim_31856_write_register(0x80, uch_cr0);
}

void maxim_disable_oc_fault_detection(void)
{
 uch_cr0= maxim_31856_read_register(0x00);
 uch_cr0&=OC_Fault_Disable_Bit;
 maxim_31856_write_register(0x80, uch_cr0);
}
/****************************************************

OC_Fault_Enable: OC_Fault_Enable1
                 OC_Fault_Enable2
                 OC_Fault_Enable3
*****************************************************/
void maxim_set_oc_fault_detection(uint8_t uch_oc_fault_enable)
{
 uch_cr0= maxim_31856_read_register(0x00);
 uch_cr0&=OC_Fault_Disable_Bit;
 uch_cr0|=uch_oc_fault_enable;
 maxim_31856_write_register(0x80, uch_cr0);
}

void maxim_clear_fault_status(void)
{
 uch_cr0= maxim_31856_read_register(0x00);
 uch_cr0|= Fault_Clear ;
 maxim_31856_write_register(0x80, uch_cr0);
}
//-------------------------------------------------------------------------/
void maxim_31856_conversion_result_process(void)
{
	uint8_t tc_ov;
    maxim_31856_read_nregisters(0x0A, uch_reg,6);  //从0x0A地址开始，读取6个字节数据

    uch_cjth=uch_reg[0];uch_cjtl=uch_reg[1];                //将读取到的结果赋值给对应的寄存器变量
    uch_ltcbh=uch_reg[2];uch_ltcbm=uch_reg[3];uch_ltcbl=uch_reg[4];
    uch_sr=uch_reg[5];
    tc_val=uch_sr&0x01;
//    if(tc_val==1)
//    {
//    	tc_ov++;
//    	if(tc_ov==16)
//    	{
//    	maxim_31856_write_register(0x80, OC_Fault_Enable_1|NRF_50Hz|Interrupt_Mode|Fault_Clear);
//    	tc_ov=0;
//    	}
//    }
//    else
//    	maxim_31856_write_register(0x80, OC_Fault_Enable_1|NRF_50Hz|
//    			Interrupt_Mode|Fault_Clear|Automatic_Conversion);

	//计算冷端温度测量结果
    temperature_value=(uch_cjth<<8|uch_cjtl)>>2;      //构造冷端温度数据

    if((uch_cjth&0x80)==0x80)                           //如果CJTH的最高位为1，则为负温度值
    {
    	temperature_value=0x3FFF-temperature_value+1;
        f_cold_junction_temperature=0-temperature_value*Cold_Junction_Resolution;   //计算得到冷端温度值（负值）
    }

    else
    {
        f_cold_junction_temperature=temperature_value*Cold_Junction_Resolution;     //计算得到冷端温度值（正值）
    }


	temperature_value=(uch_ltcbh<<16|uch_ltcbm<<8|uch_ltcbl)>>5;         //构造热电偶温度数据
    if((uch_ltcbh&0x80)==0x80)                                          //如果LTCBH最高位为1，则为负温度值
    {
        temperature_value=0x7FFFF-temperature_value+1;
        f_linearized_tc_temperature=0-temperature_value*TC_Resolution;  //计算得到热电偶转换温度值(负值)
    }
    else
        f_linearized_tc_temperature=temperature_value*TC_Resolution;     //计算得到热电偶转换温度值(正值)


//	text_temp[3]=(temperature_value>>16)&0XFF;
//	text_temp[4]=(temperature_value>>8)&0XFF;
//	text_temp[5]=(temperature_value)&0XFF;

}

