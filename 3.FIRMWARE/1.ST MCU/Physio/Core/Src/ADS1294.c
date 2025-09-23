#include <ADS1294.h>
#include "spi.h"

//define
#define SPI_FLASH_CS_LOW() HAL_GPIO_WritePin(GPIOG, ECG_SSEL_Pin, GPIO_PIN_RESET)
#define SPI_FLASH_CS_HIGH() HAL_GPIO_WritePin(GPIOG, ECG_SSEL_Pin, GPIO_PIN_SET)
//Var
unsigned char ADS1294_REG[26];		//ADS1294閿熶茎杈炬嫹閿熸枻鎷烽敓鏂ゆ嫹閿熸枻鎷�
unsigned char buff[27]={};
unsigned char ADS1294_Cache[26];	//閿熸枻鎷烽敓鎹蜂紮鎷烽敓鏂ゆ嫹閿熸枻鎷�


extern unsigned char readdata[27];


ADS1294_CONFIG1	ADS1294_Config1;																					//CONFIG1
ADS1294_CONFIG2 ADS1294_Config2;
ADS1294_CONFIG3 ADS1294_Config3;
ADS1294_LOFCTLREG ADS1294_LofCtlReg;
ADS1294_CHSETREG  ADS1294_CH0CtlReg;
ADS1294_CHSETREG  ADS1294_CH1CtlReg;
ADS1294_CHSETREG  ADS1294_CH2CtlReg;
ADS1294_CHSETREG  ADS1294_CH3CtlReg;
//ADS1294_CONFIG2 	ADS1294_Config2		={PDB_LOFF_COMP,PDB_REFBUF,VREF,CLK_EN,INT_TEST};		//CONFIG2
//ADS1294_CHSET 		ADS1294_Ch1set		={CNNNLE1_POWER,CNNNLE1_GAIN,CNNNLE1_MUX};					//CH1SET
//ADS1294_CHSET 		ADS1294_Ch2set		={CNNNLE2_POWER,CNNNLE2_GAIN,CNNNLE2_MUX};					//CH2SET
//ADS1294_RLD_SENS	ADS1294_Rld_Sens	={PDB_RLD,RLD_LOFF_SENSE,RLD2N,RLD2P,RLD1N,RLD1P};	//RLD_SENS
//ADS1294_LOFF_SENS	ADS1294_Loff_Sens	={FLIP2,FLIP1,LOFF2N,LOFF2P,LOFF1N,LOFF1P};					//LOFF_SENS
//ADS1294_RESP1			ADS1294_Resp1			={RESP_DEMOD_EN1,RESP_MOD_EN,RESP_PH,RESP_CTRL};		//RSP1
//ADS1294_RESP2			ADS1294_Resp2			={CALIB,FREQ,RLDREF_INT};														//RSP2

#define CPU_FREQUENCY_MHZ 131 // STM32鏃堕挓涓婚
void delay_us(__IO uint32_t delay)
{

    int last, curr, val;
    int temp;

    while (delay != 0)
    {

        temp = delay > 900 ? 900 : delay;
        last = SysTick->VAL;
        curr = last - CPU_FREQUENCY_MHZ * temp;
        if (curr >= 0)
        {

            do
            {

                val = SysTick->VAL;
            }
            while ((val < last) && (val >= curr));
        }
        else
        {

            curr += CPU_FREQUENCY_MHZ * 1000;
            do
            {

                val = SysTick->VAL;
            }
            while ((val <= last) || (val > curr));
        }
        delay -= temp;
    }
}



//ADS1294
void ADS1294_Init(void) 
{			
		ADS1294_PowerOnInit();//

		HAL_Delay(1000);
		ADS1294_Send_CMD(SDATAC);//
		HAL_Delay(1000);
		ADS1294_WR_REGS(RREG|ID,26,buff);
		ADS1294_SET_REGBUFF();
		ADS1294_WR_REGS(WREG|CONFIG1,25,&ADS1294_Cache[CONFIG1]);
		ADS1294_WR_REGS(RREG|ID,26,buff);
		ADS1294_Single_Read();
//		SPI_FLASH_CS_LOW();
}

//volatile unsigned char ADS1294_recive_flag=0;	//閿熸枻鎷烽敓鎹疯鎷峰彇閿熸枻鎷锋潃閿熻锟�
//volatile unsigned char ADS1294_Cache[26];	//閿熸枻鎷烽敓鎹蜂紮鎷烽敓鏂ゆ嫹閿熸枻鎷�


//void EXTI9_5_IRQHandler(void)
//{
//	
////		if(EXTI->IMR&EXTI_Line8 && ADS_DRDY==0)//閿熸枻鎷烽敓鎹锋枻鎷烽敓鏂ゆ嫹閿熷彨璁规嫹
////		{		
////				EXTI_ClearITPendingBit(EXTI_Line8); 	
////				ADS1294_Read_Data((INT8U*)ADS1294_Cache);//閿熸枻鎷烽敓鎹峰瓨鍒�9閿熻鑺備紮鎷烽敓鏂ゆ嫹閿熸枻鎷�
////				ADS1294_recive_flag=1;
////		}	
//}



//閿熸枻鎷峰彇72浣嶉敓鏂ゆ嫹閿熸枻鎷烽敓鏂ゆ嫹1100+LOFF_STAT[4:0]+GPIO[1:0]+13閿熸枻鎷�0+2CHx24浣嶉敓鏂ゆ嫹閿熸枻鎷�9閿熻鏂ゆ嫹
//	1100	LOFF_STAT[4			3			2			1			0	]	//閿熸枻鎷烽敓鏂ゆ嫹閿熸枻鎷烽敓鏂ゆ嫹閿熸枻鎷锋皭閿熸枻鎷烽敓杈冿拷閿熸枻鎷稬OFF_STAT閿熶茎杈炬嫹閿熸枻鎷烽敓鏂ゆ嫹
//									RLD		1N2N	1N2P	1N1N	1N1P	
//	閿熸枻鎷�	C0 00 00 FF E1 1A FF E1 52

void ADS1294_Read_Data(unsigned char *data)//72M鏃堕敓鏂ゆ嫹閿熼摪鐚存嫹閿熸枻鎷烽敓鏂ゆ嫹鏃堕敓鏂ゆ嫹绾�10us  8M鏃堕敓鏂ゆ嫹閿熸枻鎷� 閿熸枻鎷烽敓鏂ゆ嫹閿熸枻鎷锋椂閿熸枻鎷风害 100us
{		
//		unsigned char i;
//		uint8_t txdata=0x00;
		uint8_t txdata[27]={0};

	    SPI_FLASH_CS_LOW();
//		for(i=0;i<27;i++)
//		{
////		delay_us(1);
//		HAL_SPI_TransmitReceive (&hspi6, &txdata,data, 1, 1);
//		data++;
//		}

//		HAL_SPI_TransmitReceive (&hspi6, &txdata,data, 27, 1);//85us

		HAL_SPI_TransmitReceive_DMA (&hspi6, txdata,data, 27);
		while(__HAL_DMA_GET_COUNTER(&hdma_spi6_rx)!=0);//DMA <30us

		SPI_FLASH_CS_HIGH();
////		return *data;
}


//閿熸枻鎷烽敓鐭瘎杈炬嫹閿熸枻鎷烽敓鏂ゆ嫹閿熸枻鎷�
void ADS1294_SET_REGBUFF(void)
{   

	ADS1294_Cache[CONFIG1]=0xc6;//0XC6=500HZ 0XC3=4K 0XC4=2K 0XC5=1K
	ADS1294_Cache[CONFIG2]=0x30;
	ADS1294_Cache[CONFIG3]=0xcc;//INTER REF
	ADS1294_Cache[LOFF]=0x13;
	ADS1294_Cache[CH1SET]=0x40;
	ADS1294_Cache[CH2SET]=0x10;
    ADS1294_Cache[CH3SET]=0x10;
	ADS1294_Cache[CH4SET]=0x10;
	ADS1294_Cache[CH5SET]=0x00;
	ADS1294_Cache[CH6SET]=0x00;
	ADS1294_Cache[CH7SET]=0x00;
	ADS1294_Cache[CH8SET]=0x00;
	ADS1294_Cache[RLD_SENSP]=0x04;//LEAD II RLD
	ADS1294_Cache[RLD_SENSN]=0x04;//LEAD II RLD
	ADS1294_Cache[LOFF_SENSP]=0x04;//LEAD I RLD
	ADS1294_Cache[LOFF_SENSN]=0x04;//LEAD I RLD
    ADS1294_Cache[GPIO]=0x0f;		
    ADS1294_Cache[RESP]=0xF6;//135 degree=F6   EA=67.5  0X36 SHUT DOWN
    ADS1294_Cache[CONFIG4]=0x20;//NO WCT
    ADS1294_Cache[WCT1]=0x00;//0XEB
    ADS1294_Cache[WCT2]=0x00;//0XD4

}


void ADS1294_Send_CMD(unsigned char data)
{
	  SPI_FLASH_CS_LOW();
//	  delay_us(1);
	  uint8_t rxdata=0x00;
	  HAL_SPI_TransmitReceive (&hspi6, &data,&rxdata, 1, 1);
//	  delay_us(1);
	  SPI_FLASH_CS_HIGH();
}


void ADS1294_WR_REGS(unsigned char reg,unsigned char len,unsigned char *data)
{
		unsigned char i;
		uint8_t rxdata=0x00;
		uint8_t txdata=0x00;
	    SPI_FLASH_CS_LOW();
		delay_us(1);
		HAL_SPI_TransmitReceive (&hspi6, &reg,&rxdata, 1, 1);
//		HAL_SPI_Transmit (&hspi6, &reg, 1, 10);
		delay_us(1);
		uint8_t len_p=len-1;
		HAL_SPI_TransmitReceive (&hspi6, &len_p,&rxdata, 1, 1);
//		HAL_SPI_Transmit (&hspi6, &len_p, 1, 10);
		if(reg&0x40)
		{
				for(i=0;i<len;i++)
				{	
					  delay_us(1);
//					  ssp_xfer_byte(*data);
					  HAL_SPI_TransmitReceive (&hspi6, data,&rxdata, 1, 1);
//					  HAL_SPI_Transmit (&hspi6, data, 1, 10);
					  data++;
				}			
		}
		else 	
		{
				for(i=0;i<len;i++)
				{
					   delay_us(1);
//             *data= ssp_xfer_byte(0x00);
					   HAL_SPI_TransmitReceive (&hspi6, &txdata,data, 1, 1);
//             	 	   HAL_SPI_Receive (&hspi6, data, 1, 10);
					   data++;
				}
		}	
		delay_us(1);
		SPI_FLASH_CS_HIGH();
}


//閿熶茎杈炬嫹閿熸枻鎷烽敓鏂ゆ嫹閿熸枻鎷峰啓閿熸枻鎷锋媷閿熸枻鎷烽敓锟�
void ADS1294_WRITE_REGBUFF(void)
{
//		unsigned char i,res=0;
//		unsigned char REG_Cache[12];	//閿熻姤鍌ㄩ敓渚ヨ揪鎷烽敓鏂ゆ嫹閿熸枻鎷烽敓鏂ゆ嫹
//		ADS1294_SET_REGBUFF();//閿熸枻鎷烽敓鐭瘎杈炬嫹閿熸枻鎷烽敓鏂ゆ嫹閿熸枻鎷�
//		ADS1294_WR_REGS(WREG|CONFIG1,11,ADS1294_REG+1);//閿熸枻鎷烽敓鏂ゆ嫹閿熸枻鎷烽敓鍙揪鎷烽敓渚ヨ揪鎷烽敓鏂ゆ嫹
//		DelayMs(10);		
//		ADS1294_WR_REGS(RREG|ID,12,REG_Cache);//閿熸枻鎷烽敓渚ヨ揪鎷烽敓鏂ゆ嫹
//		DelayMs(10);	
//		
//	#ifdef DEBUG_ADS1294	
//		printf("WRITE REG:\r\n");
//		for(i=0;i<12;i++	)//瑕佸啓閿熸枻鎷烽敓鏂ゆ嫹閿熸枻鎷�
//				printf("%d %x\r\n",i,ADS1294_REG[i]);	
//		printf("READ REG:\r\n");
//	#endif	
//	
//	
//		for(i=0;i<12;i++	)	//閿熸枻鎷烽敓渚ヨ揪鎷烽敓鏂ゆ嫹
//		{						
//				if(ADS1294_REG[i] != REG_Cache[i])
//				{
//						if(i!= 0 && i!=8 && i != 11)	//0 8 閿熸枻鎷�11閿熸枻鎷稩D 閿熸枻鎷烽敓鏂ゆ嫹閿熸枻鎷烽敓鏂ゆ嫹閿燂拷GPIO閿熸枻鎷烽敓锟�
//								res=1;
//						else
//								continue;
//				}					
//			#ifdef DEBUG_ADS1294
//				printf("%d %x\r\n",i,REG_Cache[i]); //閿熸枻鎷烽敓鏂ゆ嫹閿熸枻鎷烽敓鏂ゆ嫹閿熸枻鎷�
//			#endif
//		}	

//		#ifdef DEBUG_ADS1294	
//			if(res == 0)
//					printf("REG write success\r\n");
//			else		
//					printf("REG write err\r\n");
//		#endif
//		return res;				
//}
}

void ADS1294_PowerOnInit(void)
{	

		SPI_FLASH_CS_LOW();
		HAL_Delay(100);
		SPI_FLASH_CS_HIGH();
		HAL_Delay(100);
		SPI_FLASH_CS_LOW();
		ADS1294_Send_CMD(SDATAC);//STOP DATAC
		HAL_Delay(100);
//		ADS1294_Send_CMD(STOP);//STOP
//		HAL_Delay(1000);
		ADS1294_Send_CMD(0X06);//RESET
		HAL_Delay(100);
		SPI_FLASH_CS_HIGH();

}



//閿熸枻鎷烽敓鏂ゆ嫹閫氶敓鏂ゆ嫹1閿熻妭璇ф嫹1mV閿熸枻鎷烽敓鏂ゆ嫹閿熻剼鐚存嫹
void ADS1294_Single_Test(void) //娉ㄩ敓鏂ゆ嫹1292R閿熸枻鎷烽敓鍓跨尨鎷烽敓鏂ゆ嫹閿熸枻鎷烽敓鏂ゆ嫹閿熸枻鎷烽敓鏂ゆ嫹閫氶敓鏂ゆ嫹涓�閿熸枻鎷烽敓鑺傝鎷烽敓鏂ゆ嫹閿熸枻鎷烽敓鑴氬彿璇ф嫹閿熸枻鎷烽敓鏂ゆ嫹閿熸帴甯嫹娆わ拷閿熸枻鎷烽敓鏂ゆ嫹鍙敓杞垮尅鎷烽�氶敓鏂ゆ嫹2閿熸枻鎷烽敓缂达綇鎷�1292閿熸枻鎷烽敓鏂ゆ嫹褰遍敓鏂ゆ嫹
{
//		unsigned char res=0;
//		ADS1294_Config2.Int_Test = INT_TEST_ON;//閿熸枻鎷烽敓鑺傝鎷烽敓鏂ゆ嫹閿熸枻鎷烽敓鑴氱尨鎷�
//		ADS1294_Ch1set.MUX=MUX_Test_signal;//閿熸枻鎷烽敓鏂ゆ嫹閿熻剼鐚存嫹閿熸枻鎷烽敓鏂ゆ嫹
//		ADS1294_Ch2set.MUX=MUX_Test_signal;//閿熸枻鎷烽敓鏂ゆ嫹閿熻剼鐚存嫹閿熸枻鎷烽敓鏂ゆ嫹
//		
//		if(ADS1294_WRITE_REGBUFF())//鍐欓敓鏂ゆ嫹鎷囬敓鏂ゆ嫹閿燂拷
//				res=1;
//		DelayMs(10);
//		return res;		
}
//閿熸枻鎷烽敓鏂ゆ嫹閿熻妭璇ф嫹閿熸枻鎷烽敓鏂ゆ嫹閿熸枻鎷烽敓鏂ゆ嫹
void ADS1294_Noise_Test(void)
{
//		unsigned char res=0;
//		ADS1294_Config2.Int_Test = INT_TEST_OFF;//閿熸枻鎷烽敓鑺傝鎷烽敓鏂ゆ嫹閿熸枻鎷烽敓鑴氱尨鎷�
//		ADS1294_Ch1set.MUX = MUX_input_shorted;//閿熸枻鎷烽敓鏂ゆ嫹閿熼摪锟�
//		ADS1294_Ch2set.MUX = MUX_input_shorted;//閿熸枻鎷烽敓鏂ゆ嫹閿熼摪锟�

//		if(ADS1294_WRITE_REGBUFF())//鍐欓敓鏂ゆ嫹鎷囬敓鏂ゆ嫹閿燂拷
//				res=1;	
//		DelayMs(10);			
//		return res;			
}

//閿熸枻鎷烽敓鏂ゆ嫹閿熻剼鍙烽噰纭锋嫹妯″紡
void ADS1294_Single_Read(void)
{

//		SPI_FLASH_CS_LOW();
//		delay_us(1000);
		HAL_Delay(20);
		ADS1294_Send_CMD(RDATAC); 	//閿熸枻鎷烽敓鏂ゆ嫹閿熸枻鎷烽敓鏂ゆ嫹妯″紡
		HAL_Delay(20);
//		ADS1294_Send_CMD(START);	//閿熸枻鎷烽敓閰靛尅鎷峰閿熸枻鎷烽敓鏂ゆ嫹杞敓鏂ゆ嫹閿熸枻鎷烽敓鏂ゆ嫹鏁堥敓鏂ゆ嫹閿熸枻鎷烽敓鏂ゆ嫹START閿熸枻鎷烽敓鑴氾綇鎷�
//		delay_us(10);
//		SPI_FLASH_CS_HIGH();
}

//閿熸枻鎷烽敓鏂ゆ嫹ADS1294閿熺即纭锋嫹閿熸枻鎷峰紡
void Set_ADS1294_Collect(unsigned char mode)
{
//		unsigned char res;
//
//		delay_us(10);
//		switch(mode)//閿熸枻鎷烽敓鐭噰纭锋嫹閿熸枻鎷峰紡
//		{
//				case 0:
//					res =ADS1294_Single_Read();
//				break;
//				case 1:
//					res =ADS1294_Single_Test();
//				break;
//				case 2:
//					res =ADS1294_Noise_Test();
//				break;
//		}
//		if(res)return 1;			//閿熶茎杈炬嫹閿熸枻鎷烽敓鏂ゆ嫹閿熸枻鎷峰け閿熸枻鎷�
//		ADS1294_Send_CMD(RDATAC); 	//閿熸枻鎷烽敓鏂ゆ嫹閿熸枻鎷烽敓鏂ゆ嫹妯″紡
//		delay_us(10);
//		ADS1294_Send_CMD(START);	//閿熸枻鎷烽敓閰靛尅鎷峰閿熸枻鎷烽敓鏂ゆ嫹杞敓鏂ゆ嫹閿熸枻鎷烽敓鏂ゆ嫹鏁堥敓鏂ゆ嫹閿熸枻鎷烽敓鏂ゆ嫹START閿熸枻鎷烽敓鑴氾綇鎷�
//		delay_us(10);
//		return 0;
}

