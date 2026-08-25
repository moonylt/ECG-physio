#include <ADS1298R.h>
#include "spi.h"

//define
#define SPI_FLASH_CS_LOW() HAL_GPIO_WritePin(GPIOG, ECG_SSEL_Pin, GPIO_PIN_RESET)
#define SPI_FLASH_CS_HIGH() HAL_GPIO_WritePin(GPIOG, ECG_SSEL_Pin, GPIO_PIN_SET)
//Var
unsigned char ADS1298R_REG[26];		//ADS1298R register array
unsigned char buff[27]={};
unsigned char ADS1298R_Cache[26];	//Register cache array


extern unsigned char readdata[27];


ADS1298R_CONFIG1	ADS1298R_Config1;																					//CONFIG1
ADS1298R_CONFIG2 ADS1298R_Config2;
ADS1298R_CONFIG3 ADS1298R_Config3;
ADS1298R_LOFCTLREG ADS1298R_LofCtlReg;
ADS1298R_CHSETREG  ADS1298R_CH0CtlReg;
ADS1298R_CHSETREG  ADS1298R_CH1CtlReg;
ADS1298R_CHSETREG  ADS1298R_CH2CtlReg;
ADS1298R_CHSETREG  ADS1298R_CH3CtlReg;
//ADS1298R_CONFIG2 	ADS1298R_Config2		={PDB_LOFF_COMP,PDB_REFBUF,VREF,CLK_EN,INT_TEST};		//CONFIG2
//ADS1298R_CHSET 		ADS1298R_Ch1set		={CNNNLE1_POWER,CNNNLE1_GAIN,CNNNLE1_MUX};					//CH1SET
//ADS1298R_CHSET 		ADS1298R_Ch2set		={CNNNLE2_POWER,CNNNLE2_GAIN,CNNNLE2_MUX};					//CH2SET
//ADS1298R_RLD_SENS	ADS1298R_Rld_Sens	={PDB_RLD,RLD_LOFF_SENSE,RLD2N,RLD2P,RLD1N,RLD1P};	//RLD_SENS
//ADS1298R_LOFF_SENS	ADS1298R_Loff_Sens	={FLIP2,FLIP1,LOFF2N,LOFF2P,LOFF1N,LOFF1P};					//LOFF_SENS
//ADS1298R_RESP1			ADS1298R_Resp1			={RESP_DEMOD_EN1,RESP_MOD_EN,RESP_PH,RESP_CTRL};		//RSP1
//ADS1298R_RESP2			ADS1298R_Resp2			={CALIB,FREQ,RLDREF_INT};														//RSP2

#define CPU_FREQUENCY_MHZ 131 // STM32 main clock frequency
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



//ADS1298R
void ADS1298R_Init(void) 
{			
		ADS1298R_PowerOnInit();//

		HAL_Delay(1000);
		ADS1298R_Send_CMD(SDATAC);//
		HAL_Delay(1000);
		ADS1298R_WR_REGS(RREG|ID,26,buff);
		ADS1298R_SET_REGBUFF();
		ADS1298R_WR_REGS(WREG|CONFIG1,25,&ADS1298R_Cache[CONFIG1]);
		ADS1298R_WR_REGS(RREG|ID,26,buff);
		ADS1298R_Single_Read();
//		SPI_FLASH_CS_LOW();
}

//volatile unsigned char ADS1298R_recive_flag=0;	//receive-complete flag
//volatile unsigned char ADS1298R_Cache[26];	//Register cache array


//void EXTI9_5_IRQHandler(void)
//{
//	
////		if(EXTI->IMR&EXTI_Line8 && ADS_DRDY==0)//Data ready
////		{		
////				EXTI_ClearITPendingBit(EXTI_Line8); 	
////				ADS1298R_Read_Data((INT8U*)ADS1298R_Cache);//Read 9 bytes of data
////				ADS1298R_recive_flag=1;
////		}	
//}



//Read 72 bits of data: 1100 + LOFF_STAT[4:0] + GPIO[1:0] + 13 zeros + 2CH x 24-bit data, 9 bytes in total
//	1100	LOFF_STAT[4			3			2			1			0	]	//The bits that follow are the LOFF_STAT status bits
//									RLD		1N2N	1N2P	1N1N	1N1P	
//Example: C0 00 00 FF E1 1A FF E1 52

void ADS1298R_Read_Data(unsigned char *data)//At a 72 MHz clock the read takes about 10 us; at 8 MHz, about 100 us
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


//Set up the register buffer
void ADS1298R_SET_REGBUFF(void)
{   

	ADS1298R_Cache[CONFIG1]=0xc6;//0XC6=500HZ 0XC3=4K 0XC4=2K 0XC5=1K
	ADS1298R_Cache[CONFIG2]=0x30;
	ADS1298R_Cache[CONFIG3]=0xcc;//INTER REF
	ADS1298R_Cache[LOFF]=0x13;
	ADS1298R_Cache[CH1SET]=0x40;
	ADS1298R_Cache[CH2SET]=0x10;
    ADS1298R_Cache[CH3SET]=0x10;
	ADS1298R_Cache[CH4SET]=0x10;
	ADS1298R_Cache[CH5SET]=0x00;
	ADS1298R_Cache[CH6SET]=0x00;
	ADS1298R_Cache[CH7SET]=0x00;
	ADS1298R_Cache[CH8SET]=0x00;
	ADS1298R_Cache[RLD_SENSP]=0x04;//LEAD II RLD
	ADS1298R_Cache[RLD_SENSN]=0x04;//LEAD II RLD
	ADS1298R_Cache[LOFF_SENSP]=0x04;//LEAD I RLD
	ADS1298R_Cache[LOFF_SENSN]=0x04;//LEAD I RLD
    ADS1298R_Cache[GPIO]=0x0f;		
    ADS1298R_Cache[RESP]=0xF6;//135 degree=F6   EA=67.5  0X36 SHUT DOWN
    ADS1298R_Cache[CONFIG4]=0x20;//NO WCT
    ADS1298R_Cache[WCT1]=0x00;//0XEB
    ADS1298R_Cache[WCT2]=0x00;//0XD4

}


void ADS1298R_Send_CMD(unsigned char data)
{
	  SPI_FLASH_CS_LOW();
//	  delay_us(1);
	  uint8_t rxdata=0x00;
	  HAL_SPI_TransmitReceive (&hspi6, &data,&rxdata, 1, 1);
//	  delay_us(1);
	  SPI_FLASH_CS_HIGH();
}


void ADS1298R_WR_REGS(unsigned char reg,unsigned char len,unsigned char *data)
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


//Write the register buffer into the registers
void ADS1298R_WRITE_REGBUFF(void)
{
//		unsigned char i,res=0;
//		unsigned char REG_Cache[12];	//Register cache data
//		ADS1298R_SET_REGBUFF();//Set up the register buffer
//		ADS1298R_WR_REGS(WREG|CONFIG1,11,ADS1298R_REG+1);//Write the data into the registers
//		DelayMs(10);		
//		ADS1298R_WR_REGS(RREG|ID,12,REG_Cache);//Read back the register data
//		DelayMs(10);	
//		
//	#ifdef DEBUG_ADS1298R	
//		printf("WRITE REG:\r\n");
//		for(i=0;i<12;i++	)//Data to write
//				printf("%d %x\r\n",i,ADS1298R_REG[i]);	
//		printf("READ REG:\r\n");
//	#endif	
//	
//	
//		for(i=0;i<12;i++	)	//Read back the register data
//		{						
//				if(ADS1298R_REG[i] != REG_Cache[i])
//				{
//						if(i!= 0 && i!=8 && i != 11)	//0, 8 and 11 are the ID and GPIO registers
//								res=1;
//						else
//								continue;
//				}					
//			#ifdef DEBUG_ADS1298R
//				printf("%d %x\r\n",i,REG_Cache[i]); //Read back the register data
//			#endif
//		}	

//		#ifdef DEBUG_ADS1298R	
//			if(res == 0)
//					printf("REG write success\r\n");
//			else		
//					printf("REG write err\r\n");
//		#endif
//		return res;				
//}
}

void ADS1298R_PowerOnInit(void)
{	

		SPI_FLASH_CS_LOW();
		HAL_Delay(100);
		SPI_FLASH_CS_HIGH();
		HAL_Delay(100);
		SPI_FLASH_CS_LOW();
		ADS1298R_Send_CMD(SDATAC);//STOP DATAC
		HAL_Delay(100);
//		ADS1298R_Send_CMD(STOP);//STOP
//		HAL_Delay(1000);
		ADS1298R_Send_CMD(0X06);//RESET
		HAL_Delay(100);
		SPI_FLASH_CS_HIGH();

}



//Set channel 1 to the internal 1 mV test signal
void ADS1298R_Single_Test(void) //Note: the ADS1292R test signal is generated internally; only the latched mirror data of the ADS1292 can be read out
{
//		unsigned char res=0;
//		ADS1298R_Config2.Int_Test = INT_TEST_ON;//Enable the internal test signal
//		ADS1298R_Ch1set.MUX=MUX_Test_signal;//Route the test signal to the channel input
//		ADS1298R_Ch2set.MUX=MUX_Test_signal;//Route the test signal to the channel input
//		
//		if(ADS1298R_WRITE_REGBUFF())//Error writing data
//				res=1;
//		DelayMs(10);
//		return res;		
}
//Noise test
void ADS1298R_Noise_Test(void)
{
//		unsigned char res=0;
//		ADS1298R_Config2.Int_Test = INT_TEST_OFF;//Disable the internal test signal
//		ADS1298R_Ch1set.MUX = MUX_input_shorted;//Input shorted
//		ADS1298R_Ch2set.MUX = MUX_input_shorted;//Input shorted

//		if(ADS1298R_WRITE_REGBUFF())//Error writing data
//				res=1;	
//		DelayMs(10);			
//		return res;			
}

//Set normal signal acquisition mode
void ADS1298R_Single_Read(void)
{

//		SPI_FLASH_CS_LOW();
//		delay_us(1000);
		HAL_Delay(20);
		ADS1298R_Send_CMD(RDATAC); 	//Continuous data read mode
		HAL_Delay(20);
//		ADS1298R_Send_CMD(START);	//Send START to begin conversions
//		delay_us(10);
//		SPI_FLASH_CS_HIGH();
}

//Set the data acquisition mode
void Set_ADS1298R_Collect(unsigned char mode)
{
//		unsigned char res;
//
//		delay_us(10);
//		switch(mode)//Select the acquisition mode
//		{
//				case 0:
//					res =ADS1298R_Single_Read();
//				break;
//				case 1:
//					res =ADS1298R_Single_Test();
//				break;
//				case 2:
//					res =ADS1298R_Noise_Test();
//				break;
//		}
//		if(res)return 1;			//Acquisition mode configuration failed
//		ADS1298R_Send_CMD(RDATAC); 	//Continuous data read mode
//		delay_us(10);
//		ADS1298R_Send_CMD(START);	//Send START to begin conversions
//		delay_us(10);
//		return 0;
}

