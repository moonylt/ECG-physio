
// *  ------------------------------------------------------------------------- */
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
///** \file max31856drv.h ******************************************************
// *
// *             Project: max31856
// *            Filename: max31856drv.h
// *         Description: Header file for the Main application module max31856 example program.
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

///* Define to prevent recursive inclusion -------------------------------------*/

#ifndef __MAX31856drv_H
#define __MAX31856drv_H

#ifdef __cplusplus
 extern "C" {
#endif


#include "stdint.h"
//#include "hardwareInterface.h"
//#include "stm32_spi.h"

#define   Cold_Junction_Resolution    0.015625
#define   TC_Resolution               0.0078125   
   
#define  Stop_Conversion_Bit        (uint8_t) 0x3F
#define  One_Shot_Conversion       (uint8_t) 0x40
#define  Automatic_Conversion       (uint8_t) 0x80 
   
#define  OC_Fault_Disable_Bit       (uint8_t) 0xCF 
#define  OC_Fault_Enable_1          (uint8_t) 0x10
#define  OC_Fault_Enable_2          (uint8_t) 0x20
#define  OC_Fault_Enable_3          (uint8_t) 0x30
   
#define  CJ_Sensor_Enable_Bit       (uint8_t) 0xF7
#define  CJ_Sensor_Disable          (uint8_t) 0x08
   
#define  Comparator_Mode_Bit        (uint8_t) 0xFB
#define  Interrupt_Mode             (uint8_t) 0x04

#define  Fault_Clear                (uint8_t) 0x02

#define  NRF_60Hz_Bit               (uint8_t) 0xFE
#define  NRF_50Hz                   (uint8_t) 0x01
   
   
#define Average_1_Bit               (uint8_t) 0x0F
#define Average_2                   (uint8_t) 0x10
#define Average_4                   (uint8_t) 0x20
#define Average_8                   (uint8_t) 0x30
#define Average_16                  (uint8_t) 0x40  
   
#define TC_TypeB_Bit                (uint8_t) 0xF0
#define TC_TypeE                    (uint8_t) 0x01
#define TC_TypeJ                    (uint8_t) 0x02
#define TC_TypeK                    (uint8_t) 0x03
#define TC_TypeN                    (uint8_t) 0x04
#define TC_TypeR                    (uint8_t) 0x05
#define TC_TypeS                    (uint8_t) 0x06
#define TC_TypeT                    (uint8_t) 0x07
#define VM_Gain8                    (uint8_t) 0x80
#define VM_Gain16                   (uint8_t) 0xC0

   
   
#define CJ_High_Fault_Mask          (uint8_t)0x20
#define CJ_Low_Fault_Mask           (uint8_t)0x10
#define TC_High_Fault_Mask          (uint8_t)0x08
#define TC_Low_Fault_Mask           (uint8_t)0x04
#define OVUV_Fault_Mask             (uint8_t)0x02
#define Open_Fault_Mask             (uint8_t)0x01
#define ALL_Fault_Mask              (uint8_t)0x3F
#define No_Fault_Mask               (uint8_t)0x00
   
#define CJ_Range_Fault              (uint8_t)0x80
#define TC_Range_Fault              (uint8_t)0x40
#define CJHIGH_Fault                (uint8_t)0x20
#define CJLOW_Fault                 (uint8_t)0x10
#define TCHIGH_Fault                (uint8_t)0x08
#define TCLOW_Fault                 (uint8_t)0x04
#define OVUV_Fault                  (uint8_t)0x02
#define OPEN_Fault                  (uint8_t)0x01
#define NO_Fault                    (uint8_t)0x00   




void maxim_31856_init(void);
void maxim_stop_conversion(void);
void maxim_start_conversion(uint8_t uch_conversion_mode);
void maxim_disable_oc_fault_detection(void);
void maxim_set_oc_fault_detection(uint8_t uch_oc_fault_enable);
void maxim_clear_fault_status(void);
void maxim_31856_conversion_result_process(void);

void maxim_31856_write_register(uint8_t uch_register_address, uint8_t uch_register_value);
uint8_t maxim_31856_read_register(uint8_t uch_register_address);
void maxim_31856_read_nregisters(uint8_t uch_register_address, uint8_t *uch_buff,uint8_t uch_nBytes);
  
 #ifdef __cplusplus
}
#endif

#endif
