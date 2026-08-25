#ifndef __ADS1298R_H
#define __ADS1298R_H	 


/////////////////////////////////////////////////////////////////////////////////////////////
//Variable declarations

// unsigned char ADS1298R_recive_flag=0;	// receive-complete flag


//ADS1298R command definitions
//System commands
	#define WAKEUP	0X02	//Wake up from standby mode
	#define STANDBY	0X04	//Enter standby mode
//	#define RESET	0X06	//Reset ADS1298R
	#define START	0X08	//Start conversions
	#define STOP	0X0A	//Stop conversions
	//#define OFFSETCAL	0X1A	//Channel offset calibration

//Data read commands
	#define RDATAC	0X10	//Enable continuous data read mode; this mode is used by default
	#define SDATAC	0X11	//Stop continuous data read mode
	#define RDATA		0X12	//Read data by command; supports multiple readbacks
//Register access commands
	//r rrrr=first register address to read/write	 //	n nnnn=number of registers to read/write
	#define RREG	0X20	//Read  001r rrrr (first byte) 000n nnnn (second byte)
	#define WREG	0X40	//Write  010r rrrr (first byte) 000n nnnn (second byte)

//ADS1298R internal register address definitions
	#define ID					0	//ID control register
	#define CONFIG1			1	//Configuration register 1
	#define CONFIG2			2	//Configuration register 2
	#define CONFIG3			3	//Configuration register 3
	#define LOFF				4	//Lead-off control register
	#define CH1SET			5	//Channel 1 setup register
	#define CH2SET			6	//Channel 2 setup register
	#define CH3SET			7	//Channel 3 setup register
	#define CH4SET			8	//Channel 4 setup register
	#define CH5SET			9	//Channel 5 setup register
	#define CH6SET			10	//Channel 6 setup register
	#define CH7SET			11	//Channel 7 setup register
	#define CH8SET			12	//Channel 8 setup register
	#define RLD_SENSP		13	//Right-leg drive selection register
	#define RLD_SENSN		14	//Right-leg drive selection register
	#define LOFF_SENSP	15	//Positive lead-off detection register
	#define LOFF_SENSN	16	//Negative lead-off detection register
	#define LOFF_FLIP		17	//Lead-off flip register
	#define LOFF_STATP	18	//Positive lead-off status register
	#define LOFF_STATN	19	//Negative lead-off status register
	#define	GPIO				20  //GPIO control register
	#define	PACE				21  //Pace detection register
	#define	RESP				22	//Respiration control register
	#define CONFIG4			23	//Configuration register 4
	#define WCT1			  24	//Wilson central terminal control register
  #define WCT2			  25	//Wilson central terminal control register

  //DeviceId
  #define	DEVICE_ID_ADS1298R	0Xd0
	//CONFIG1
	#define HR_LP_Mode  0
	#define HR_HR_Mode  1
	#define DAISY_ENABLE  0// Daisy_chain mode
	#define DAISY_DISENABLE  1// Multiple readback mode
	#define CLK_DISEN_OUTPUT 0// OSCILLATOR clock output disabled
	#define CLK_EN_OUTPUT 1// OSCILLATOR clock output enabled
	#define	DATA_RATE_HR_32kSPS	0	//Sample rate
	#define	DATA_RATE_LP_16kSPS	0	//Sample rate
	#define	DATA_RATE_HR_16kSPS	1	//Sample rate
	#define	DATA_RATE_LP_8kSPS	1	//Sample rate
	#define	DATA_RATE_HR_8kSPS	2	//Sample rate
	#define	DATA_RATE_LP_4kSPS	2	//Sample rate
	#define	DATA_RATE_HR_4kSPS	3	//Sample rate
	#define	DATA_RATE_LP_2kSPS	3	//Sample rate
	#define	DATA_RATE_HR_2kSPS	4	//Sample rate
	#define	DATA_RATE_LP_1kSPS	4	//Sample rate
	#define	DATA_RATE_HR_1kSPS	5	//Sample rate
	#define	DATA_RATE_LP_500SPS	5	//Sample rate
	#define	DATA_RATE_HR_500SPS	6	//Sample rate
	#define	DATA_RATE_LP_250SPS	6	//Sample rate
	#define	DATA_RATE_Reserved	7	//Sample rate
	//CONFIG2
	#define	WCT_CHOP_Varies     0	//Chopping frequency varies
	#define	WCT_CHOP_Fixed      1	//Chopping frequency constant at fMOD / 16
	#define	INT_TEST_External   0	//Test signals are driven externally
	#define	INT_TEST_Internal   1	//Test signals are driven internally
	#define	TEST_AMP_CalibrationAP0   0	// determine the calibration signal amplitude 0 = 1*-(VREFP � VREFN) / 2400 V
  #define	TEST_AMP_CalibrationAP1   1	// determine the calibration signal amplitude 0 = 2*-(VREFP � VREFN) / 2400 V
  #define	TEST_FREQUENCY0   0	//determine the calibration signal frequency 00 = Pulsed at fCLK / 2^21
	#define	TEST_FREQUENCY1   1	//determine the calibration signal frequency 01 = Pulsed at fCLK / 2^20
	#define	TEST_FREQUENCY2   2	// Not used
	#define	TEST_FREQUENCY3   3	//At dc
	//CONFIG3
	#define	PD_REFBUF_SATAUS0     0	//determines the power-down reference buffer state. Power-down internal reference buffer
  #define	PD_REFBUF_SATAUS1     1	//determines the power-down reference buffer state. Enable internal reference buffer
	#define	VREF_SET2V4           0	//determines the reference voltage, VREFP.VREFP is set to 2.4 V
	#define	VREF_SET4V	          1	//determines the reference voltage, VREFP.VREFP is set to 4.0 V(use only with a 5-V analog supply)
  #define	RLD_MEAS0             0 //enables RLD measurement. The RLD signal may be measured with any channel Open
  #define	RLD_MEAS1             1 //enables RLD measurement. The RLD signal may be measured with any channel Open = RLD_IN signal is routed to the channel that has the MUX_Setting 010 (VREF)
  #define RLDREF_INT_External   0 //determines the RLDREF signal source RLDREF signal fed externally
	#define RLDREF_INT_Internal   1 //determines the RLDREF signal source RLDREF signal (AVDD-AVSS)/2 generated internally
  #define PD_RLD_BUFPOWERDOWN   0 //determines the RLD buffer power state.RLD buffer is powered down
	#define PD_RLD_BUFPOWERENBALE 1 //determines the RLD buffer power state. RLD buffer is enabled     
  #define RLD_LOFF_SENS_DisEnable   0 //RLD sense is disabled
	#define RLD_LOFF_SENS_Enable      1 //RLD sense is enabled
  #define RLD_STAT_Connected        0// Read only RLD lead-off status  determines the RLD status.  RLD is connected
	#define RLD_STAT_InConnected      1// Read only RLD lead-off status  determines the RLD status.  RLD is connected
  //LOFFCTLREG
  #define COMP_TH_P_Percent95     0
	#define COMP_TH_P_Percent92P5   1
	#define COMP_TH_P_Percent90     2
	#define COMP_TH_P_Percent87P5   3
  #define COMP_TH_P_Percent85     4
	#define COMP_TH_P_Percent80     5
	#define COMP_TH_P_Percent75     6
	#define COMP_TH_P_Percent70     7	
  #define COMP_TH_N_Percent5      0
	#define COMP_TH_N_Percent7P5    1
	#define COMP_TH_N_Percent10     2
	#define COMP_TH_N_Percent12P5   3
  #define COMP_TH_N_Percent15     4
	#define COMP_TH_N_Percent20     5
	#define COMP_TH_N_Percent25     6
	#define COMP_TH_N_Percent30     7		
	#define VLEAD_OFF_EN_Mode0       0			//Lead-off detection mode Lead-off detection mode Current source mode lead-off
	#define VLEAD_OFF_EN_Mode1       1			//Lead-off detection mode Lead-off detection mode pullup or pulldown resistor mode lead-off
  #define ILEAD_OFF_6nA           0 //determine the magnitude of current for the current lead-off mode  6nA
  #define ILEAD_OFF_12nA          1 //determine the magnitude of current for the current lead-off mode 12nA
	#define ILEAD_OFF_18nA          2 //determine the magnitude of current for the current lead-off mode 18nA
  #define ILEAD_OFF_24nA          3 //determine the magnitude of current for the current lead-off mode 24nA
	#define FLEAD_OFF_0             0//determine the frequency of lead-off detect for each channel.When any bits of the LOFF_SENSP or LOFF_SENSN registers are turned on, make sure that FLEAD[1:0] are either set to 01 or 11
	#define FLEAD_OFF_1             1//determine the frequency of lead-off detect for each channel.AC lead-off detection at fDR / 4
	#define FLEAD_OFF_2             2//not used
	#define FLEAD_OFF_3             3//determine the frequency of lead-off detect for each channel.DC lead-off detection turned o
  //CH0SETREG
	#define PD_CH0_Normal           0//determines the channel power mode for the corresponding channel. Normal operation
	#define PD_CH0_PowerDown        1//determines the channel power mode for the corresponding channel. Channel power-down
	#define GAIN_CH0_6db            0//determine the PGA gain setting.6db
	#define GAIN_CH0_1db            1//determine the PGA gain setting.1db
	#define GAIN_CH0_2db            2//determine the PGA gain setting.2db
	#define GAIN_CH0_3db            3//determine the PGA gain setting.3db
	#define GAIN_CH0_4db            4//determine the PGA gain setting.4db
	#define GAIN_CH0_8db            5//determine the PGA gain setting.8db
	#define GAIN_CH0_12db           6//determine the PGA gain setting.12db
	#define GAIN_CH0_Unused         7//determine the PGA gain setting.unused
	#define MUX_CH0_NormalInput     0//Normal electrode input
	#define MUX_CH0_InputShorted    1//Input shorted (for offset or noise measurements)
	#define MUX_CH0_Conjunction     2//Used in conjunction with RLD_MEAS bit for RLD measurements. See the Right Leg Drive (RLD) DC Bias Circuit subsection of the ECG-Specific Functions section for more details.
	#define MUX_CH0_MVDD            3//MVDD for supply measurement
	#define MUX_CH0_TemperatureSensor    4//Temperature sensor
	#define MUX_CH0_TestSignal      5 //Test signal
	#define MUX_CH0_RLD_DRP         6 //RLD_DRP (positive electrode is the driver)
	#define MUX_CH0_RLD_DRN         7 //RLD_DRn (negative electrode is the driver)
  //CH1SETREG	
	#define PD_CH1_Normal           0//determines the channel power mode for the corresponding channel. Normal operation
	#define PD_CH1_PowerDown        1//determines the channel power mode for the corresponding channel. Channel power-down
	#define GAIN_CH1_6db            0//determine the PGA gain setting.6db
	#define GAIN_CH1_1db            1//determine the PGA gain setting.1db
	#define GAIN_CH1_2db            2//determine the PGA gain setting.2db
	#define GAIN_CH1_3db            3//determine the PGA gain setting.3db
	#define GAIN_CH1_4db            4//determine the PGA gain setting.4db
	#define GAIN_CH1_8db            5//determine the PGA gain setting.8db
	#define GAIN_CH1_12db           6//determine the PGA gain setting.12db
	#define GAIN_CH1_Unused         7//determine the PGA gain setting.unused
	#define MUX_CH1_NormalInput     0//Normal electrode input
	#define MUX_CH1_InputShorted    1//Input shorted (for offset or noise measurements)
	#define MUX_CH1_Conjunction     2//Used in conjunction with RLD_MEAS bit for RLD measurements. See the Right Leg Drive (RLD) DC Bias Circuit subsection of the ECG-Specific Functions section for more details.
	#define MUX_CH1_MVDD            3//MVDD for supply measurement
	#define MUX_CH1_TemperatureSensor    4//Temperature sensor
	#define MUX_CH1_TestSignal      5 //Test signal
	#define MUX_CH1_RLD_DRP         6 //RLD_DRP (positive electrode is the driver)
	#define MUX_CH1_RLD_DRN         7 //RLD_DRn (negative electrode is the driver)
	//CH2SETREG
	#define PD_CH2_Normal           0//determines the channel power mode for the corresponding channel. Normal operation
	#define PD_CH2_PowerDown        1//determines the channel power mode for the corresponding channel. Channel power-down
	#define GAIN_CH2_6db            0//determine the PGA gain setting.6db
	#define GAIN_CH2_1db            1//determine the PGA gain setting.1db
	#define GAIN_CH2_2db            2//determine the PGA gain setting.2db
	#define GAIN_CH2_3db            3//determine the PGA gain setting.3db
	#define GAIN_CH2_4db            4//determine the PGA gain setting.4db
	#define GAIN_CH2_8db            5//determine the PGA gain setting.8db
	#define GAIN_CH2_12db           6//determine the PGA gain setting.12db
	#define GAIN_CH2_Unused         7//determine the PGA gain setting.unused
	#define MUX_CH2_NormalInput     0//Normal electrode input
	#define MUX_CH2_InputShorted    1//Input shorted (for offset or noise measurements)
	#define MUX_CH2_Conjunction     2//Used in conjunction with RLD_MEAS bit for RLD measurements. See the Right Leg Drive (RLD) DC Bias Circuit subsection of the ECG-Specific Functions section for more details.
	#define MUX_CH2_MVDD            3//MVDD for supply measurement
	#define MUX_CH2_TemperatureSensor    4//Temperature sensor
	#define MUX_CH2_TestSignal      5 //Test signal
	#define MUX_CH2_RLD_DRP         6 //RLD_DRP (positive electrode is the driver)
	#define MUX_CH2_RLD_DRN         7 //RLD_DRn (negative electrode is the driver)	
	//CH3SETREG
	#define PD_CH3_Normal           0//determines the channel power mode for the corresponding channel. Normal operation
	#define PD_CH3_PowerDown        1//determines the channel power mode for the corresponding channel. Channel power-down
	#define GAIN_CH3_6db            0//determine the PGA gain setting.6db
	#define GAIN_CH3_1db            1//determine the PGA gain setting.1db
	#define GAIN_CH3_2db            2//determine the PGA gain setting.2db
	#define GAIN_CH3_3db            3//determine the PGA gain setting.3db
	#define GAIN_CH3_4db            4//determine the PGA gain setting.4db
	#define GAIN_CH3_8db            5//determine the PGA gain setting.8db
	#define GAIN_CH3_12db           6//determine the PGA gain setting.12db
	#define GAIN_CH3_Unused         7//determine the PGA gain setting.unused
	#define MUX_CH3_NormalInput     0//Normal electrode input
	#define MUX_CH3_InputShorted    1//Input shorted (for offset or noise measurements)
	#define MUX_CH3_Conjunction     2//Used in conjunction with RLD_MEAS bit for RLD measurements. See the Right Leg Drive (RLD) DC Bias Circuit subsection of the ECG-Specific Functions section for more details.
	#define MUX_CH3_MVDD            3//MVDD for supply measurement
	#define MUX_CH3_TemperatureSensor    4//Temperature sensor
	#define MUX_CH3_TestSignal      5 //Test signal
	#define MUX_CH3_RLD_DRP         6 //RLD_DRP (positive electrode is the driver)
	#define MUX_CH3_RLD_DRN         7 //RLD_DRn (negative electrode is the driver)
	//RLD_SENSPREG
	#define	RLD8P_DISABLE           0	
	#define	RLD8P_ENABLE            1
	#define	RLD7P_DISABLE           0	
	#define	RLD7P_ENABLE            1	
	#define	RLD6P_DISABLE           0	
	#define	RLD6P_ENABLE            1
	#define	RLD5P_DISABLE           0	
	#define	RLD5P_ENABLE            1	
	#define	RLD4P_DISABLE           0	
	#define	RLD4P_ENABLE            1
	#define	RLD3P_DISABLE           0	
	#define	RLD3P_ENABLE            1	
	#define	RLD2P_DISABLE           0	
	#define	RLD2P_ENABLE            1
	#define	RLD1P_DISABLE           0	
	#define	RLD1P_ENABLE            1	
	//RLD_SENSNREG
	#define	RLD8N_DISABLE           0	
	#define	RLD8N_ENABLE            1
	#define	RLD7N_DISABLE           0	
	#define	RLD7N_ENABLE            1	
	#define	RLD6N_DISABLE           0	
	#define	RLD6N_ENABLE            1
	#define	RLD5N_DISABLE           0	
	#define	RLD5N_ENABLE            1	
	#define	RLD4N_DISABLE           0	
	#define	RLD4N_ENABLE            1
	#define	RLD3N_DISABLE           0	
	#define	RLD3N_ENABLE            1	
	#define	RLD2N_DISABLE           0	
	#define	RLD2N_ENABLE            1
	#define	RLD1N_DISABLE           0	
	#define	RLD1N_ENABLE            1	
	//LOFF_SENSPREG
	#define	LOFF8P_DISABLE           0	
	#define	LOFF8P_ENABLE            1
	#define	LOFF7P_DISABLE           0	
	#define	LOFF7P_ENABLE            1	
	#define	LOFF6P_DISABLE           0	
	#define	LOFF6P_ENABLE            1
	#define	LOFF5P_DISABLE           0	
	#define	LOFF5P_ENABLE            1	
	#define	LOFF4P_DISABLE           0	
	#define	LOFF4P_ENABLE            1
	#define	LOFF3P_DISABLE           0	
	#define	LOFF3P_ENABLE            1	
	#define	LOFF2P_DISABLE           0	
	#define	LOFF2P_ENABLE            1
	#define	LOFF1P_DISABLE           0	
	#define	LOFF1P_ENABLE            1	
	//LOFF_SENSNREG
	#define	LOFF8N_DISABLE           0	
	#define	LOFF8N_ENABLE            1
	#define	LOFF7N_DISABLE           0	
	#define	LOFF7N_ENABLE            1	
	#define	LOFF6N_DISABLE           0	
	#define	LOFF6N_ENABLE            1
	#define	LOFF5N_DISABLE           0	
	#define	LOFF5N_ENABLE            1	
	#define	LOFF4N_DISABLE           0	
	#define	LOFF4N_ENABLE            1
	#define	LOFF3N_DISABLE           0	
	#define	LOFF3N_ENABLE            1	
	#define	LOFF2N_DISABLE           0	
	#define	LOFF2N_ENABLE            1
	#define	LOFF1N_DISABLE           0	
	#define	LOFF1N_ENABLE            1		
//LOFF_FLIPREG
	#define	LOFF_FLIP8_NOFLIP        0
	#define	LOFF_FLIP8_FLIPED        1
	#define	LOFF_FLIP7_NOFLIP        0
	#define	LOFF_FLIP7_FLIPED        1	
	#define	LOFF_FLIP6_NOFLIP        0
	#define	LOFF_FLIP6_FLIPED        1
	#define	LOFF_FLIP5_NOFLIP        0
	#define	LOFF_FLIP5_FLIPED        1		
	#define	LOFF_FLIP4_NOFLIP        0
	#define	LOFF_FLIP4_FLIPED        1
	#define	LOFF_FLIP3_NOFLIP        0
	#define	LOFF_FLIP3_FLIPED        1	
	#define	LOFF_FLIP2_NOFLIP        0
	#define	LOFF_FLIP2_FLIPED        1
	#define	LOFF_FLIP1_NOFLIP        0
	#define	LOFF_FLIP1_FLIPED        1		
//LOFF_STATUSPREG	
	#define	LOFF_STATP_IN8PON       0
	#define	LOFF_STATP_IN8POFF        1		
	#define	LOFF_STATP_IN7PON       0
	#define	LOFF_STATP_IN7POFF        1		
	#define	LOFF_STATP_IN6PON       0
	#define	LOFF_STATP_IN6POFF       1		
	#define	LOFF_STATP_IN5PON       0
	#define	LOFF_STATP_IN5POFF        1	
	#define	LOFF_STATP_IN4PON       0
	#define	LOFF_STATP_IN4POFF        1		
	#define	LOFF_STATP_IN3PON       0
	#define	LOFF_STATP_IN3POFF        1		
	#define	LOFF_STATP_IN2PON       0
	#define	LOFF_STATP_IN2POFF        1		
	#define	LOFF_STATP_IN1PON       0
	#define	LOFF_STATP_IN1POFF        1		
//LOFF_STATUSNREG		
	#define	LOFF_STATN_IN8NON       0
	#define	LOFF_STATN_IN8NOFF        1		
	#define	LOFF_STATN_IN7NON       0
	#define	LOFF_STATN_IN7NOFF        1		
	#define	LOFF_STATN_IN6NON      0
	#define	LOFF_STATN_IN6NOFF        1		
	#define	LOFF_STATN_IN5NON       0
	#define	LOFF_STATN_IN5NOFF        1	
	#define	LOFF_STATN_IN4NPON       0
	#define	LOFF_STATN_IN4NOFF       1		
	#define	LOFF_STATN_IN3NPON       0
	#define	LOFF_STATN_IN3NOFF        1		
	#define	LOFF_STATN_IN2NON       0
	#define	LOFF_STATN_IN2NOFF        1		
	#define	LOFF_STATN_IN1NON       0
	#define	LOFF_STATN_IN1NOFF        1		
	
//GPIO Control	
//PACE Control	
//Respiration Control Register
	#define	RESP_DEMOD_EN1_OFF       0 
	#define	RESP_DEMOD_EN1_ON       1 	
	#define	RESP_MOD_EN1_OFF       0 
	#define	RESP_MOD_EN1_ON       1 	
  #define	RESP_PH_22P5D          0
  #define	RESP_PH_45D          1	
	#define	RESP_PH_67P5D          2	
	#define	RESP_PH_90D          3	
  #define	RESP_PH_112P5D          4
  #define	RESP_PH_135D          5	
  #define	RESP_PH_157P5D          6
  #define	RESP_PH_NA          7

//CONFIG4 REG
  #define	RESP_MODULATIONFREQ_64KHZ       0
  #define	RESP_MODULATIONFREQ_32KHZ       1
  #define	RESP_MODULATIONFREQ_16KHZ       2
  #define	RESP_MODULATIONFREQ_8KHZ        3
  #define	RESP_MODULATIONFREQ_4KHZ        4
  #define	RESP_MODULATIONFREQ_2KHZ        5
  #define	RESP_MODULATIONFREQ_1KHZ        6
  #define	RESP_MODULATIONFREQ_500HZ       7	


 typedef union
 {
 struct
 {
 	unsigned char  DR:3;
 	unsigned char  Reserved:2;
 	unsigned char  CLK_EN:1;
 	unsigned char  DAISY_EN:1;
 	unsigned char  HR_LP:1;
 }REG_CONFIG;
   unsigned char  CONFIG1_Data;
 }ADS1298R_CONFIG1;
 typedef union
 {
 struct
 {
 	unsigned char  TEST_FREQ:2;
 	unsigned char  TEST_AMP:1;
 	unsigned char  Reserved1:1;
 	unsigned char  INT_TEST:1;
 	unsigned char  WCT_CHOP:1;
 	unsigned char  Reserved:2;
 }REG_CONFIG;
   unsigned char  CONFIG2_Data;
 }ADS1298R_CONFIG2;

 typedef union
 {
 struct
 {
 	unsigned char  RLD_STAT:1;
 	unsigned char  RLD_LOFF_SENS:1;
 	unsigned char  PD_RLD:1;
 	unsigned char  RLDREF_INT:1;
 	unsigned char  RLD_MEAS:1;
 	unsigned char  VREF_4V:1;
 	unsigned char  Reserved:1;
 	unsigned char  PD_REFBUF:1;
 }REG_CONFIG;
   unsigned char  CONFIG3_Data;
 }ADS1298R_CONFIG3;

 typedef union
 {
 struct
 {
 	unsigned char  FLEAD_OFF:2;
 	unsigned char  ILEAD_OFF:2;
   unsigned char  VLEAD_OFF_EN:1;
 	unsigned char  COMP_TH:3;
 }REG_CONFIG;
   unsigned char  LOFCTLREG_Data;
 }ADS1298R_LOFCTLREG;


 typedef union
 {
 struct
 {
 	unsigned char  MUX:3;
 	unsigned char  Reserved:1;
   unsigned char  GAIN:3;
 	unsigned char  PD:1;
 }REG_CONFIG;
   unsigned char  CHSETREG_Data;
 }ADS1298R_CHSETREG;

 typedef union
 {
 struct
 {
 	unsigned char  RLD1P:1;
 	unsigned char  RLD2P:1;
 	unsigned char  RLD3P:1;
 	unsigned char  RLD4P:1;
 	unsigned char  RLD5P:1;
 	unsigned char  RLD6P:1;
 	unsigned char  RLD7P:1;
 	unsigned char  RLD8P:1;
 }REG_CONFIG;
   unsigned char  RLD_SENSPREG_Data;
 }ADS1298R_RLD_SENSPREG;

 typedef union
 {
 struct
 {
 	unsigned char  RLD1N:1;
 	unsigned char  RLD2N:1;
 	unsigned char  RLD3N:1;
 	unsigned char  RLD4N:1;
 	unsigned char  RLD5N:1;
 	unsigned char  RLD6N:1;
 	unsigned char  RLD7N:1;
 	unsigned char  RLD8N:1;
 }REG_CONFIG;
   unsigned char  RLD_SENSNREG_Data;
 }ADS1298R_RLD_SENSNREG;


 typedef union
 {
 struct
 {
 	unsigned char  LOFF1P:1;
 	unsigned char  LOFF2P:1;
 	unsigned char  LOFF3P:1;
 	unsigned char  LOFF4P:1;
 	unsigned char  LOFF5P:1;
 	unsigned char  LOFF6P:1;
 	unsigned char  LOFF7P:1;
 	unsigned char  LOFF8P:1;
 }REG_CONFIG;
   unsigned char  LOFF_SENSPREG_Data;
 }ADS1298R_LOFF_SENSPREG;

 typedef union
 {
 struct
 {
 	unsigned char  LOFF1N:1;
 	unsigned char  LOFF2N:1;
 	unsigned char  LOFF3N:1;
 	unsigned char  LOFF4N:1;
 	unsigned char  LOFF5N:1;
 	unsigned char  LOFF6N:1;
 	unsigned char  LOFF7N:1;
 	unsigned char  LOFF8N:1;
 }REG_CONFIG;
   unsigned char  LOFF_SENSNREG_Data;
 }ADS1298R_LOFF_SENSNREG;


 typedef union
 {
 struct
 {
 	unsigned char  LOFF_FLIP1:1;
 	unsigned char  LOFF_FLIP2:1;
 	unsigned char  LOFF_FLIP3:1;
 	unsigned char  LOFF_FLIP4:1;
 	unsigned char  LOFF_FLIP5:1;
 	unsigned char  LOFF_FLIP6:1;
 	unsigned char  LOFF_FLIP7:1;
 	unsigned char  LOFF_FLIP8:1;
 }REG_CONFIG;
   unsigned char  LOFF_FLIPREG_Data;
 }ADS1298R_LOFF_FLIPREG;

 typedef union
 {
 struct
 {
 	unsigned char  IN1P_OFF:1;
 	unsigned char  IN2P_OFF:1;
 	unsigned char  IN3P_OFF:1;
 	unsigned char  IN4P_OFF:1;
 	unsigned char  IN5P_OFF:1;
 	unsigned char  IN6P_OFF:1;
 	unsigned char  IN7P_OFF:1;
 	unsigned char  IN8P_OFF:1;
 }REG_CONFIG;
   unsigned char  LOFF_STATPREG_Data;
 }ADS1298R_LOFF_STATPREG;


 typedef union
 {
 struct
 {
 	unsigned char  IN1N_OFF:1;
 	unsigned char  IN2N_OFF:1;
 	unsigned char  IN3N_OFF:1;
 	unsigned char  IN4N_OFF:1;
 	unsigned char  IN5N_OFF:1;
 	unsigned char  IN6N_OFF:1;
 	unsigned char  IN7N_OFF:1;
 	unsigned char  IN8N_OFF:1;
 }REG_CONFIG;
   unsigned char  LOFF_STATNREG_Data;
 }ADS1298R_LOFF_STATNREG;

 typedef union
 {
 struct
 {
// 	unsigned char  GPIOD:4;
// 	unsigned char  GPIOC:4;

 }REG_CONFIG;
   unsigned char  GPIOREG_Data;
 }ADS1298R_GPIOREG;

 typedef union
 {
 struct
 {
 	unsigned char  PD_PACE:1;
 	unsigned char  PACEO:2;
 	unsigned char  PACEE:2;
 	unsigned char  Reserved:3;
 }REG_CONFIG;
   unsigned char  PACEREG_Data;
 }ADS1298R_PACEREG;


 typedef union
 {
 struct
 {
 	unsigned char  RESP_CTRL:2;
 	unsigned char  RESP_PH:3;
 	unsigned char  Reserved:1;
 	unsigned char  RESP_MOD_EN1:1;
 	unsigned char  RESP_DEMOD_EN1:1;
 }REG_CONFIG;
   unsigned char  RESPREG_Data;
 }ADS1298R_RESPREG;


 typedef union
 {
 struct
 {
 	unsigned char  Reserved1:1;
 	unsigned char  PD_LOFF_COMP:1;
 	unsigned char  WCT_TO_RLD:1;
 	unsigned char  SINGLE_SHOT:1;
 	unsigned char  Reserved:1;
 	unsigned char  RESP_FREQ:3;
 }REG_CONFIG;
   unsigned char  CONFIG4_Data;
 }ADS1298R_CONFIG4;

 typedef union
 {
 struct
 {
 	unsigned char  WCTA:3;
 	unsigned char  PD_WCTA:1;
   unsigned char  aVF_CH4:1;
 	unsigned char  aVF_CH7:1;
   unsigned char  aVF_CH5:1;
 	unsigned char  aVF_CH6:1;
 }REG_CONFIG;
   unsigned char  WCT1REG_Data;
 }ADS1298R_WCT1REG;

 typedef union
 {
 struct
 {
 	unsigned char  WCTC:3;
   unsigned char  WCTB:3;
 	unsigned char  PD_WCTB:1;
 	unsigned char  PD_WCTC:1;
 }REG_CONFIG;
   unsigned char  WCT2REG_Data;
 }ADS1298R_WCT2REG;





void ADS1298R_Init(void); //Initialize the ADS1298R pins
void ADS1298R_PowerOnInit(void);//Power-on initialization
void ADS1298R_Send_CMD(unsigned char data);//Send a command
void ADS1298R_WR_REGS(unsigned char reg,unsigned char len,unsigned char *data);//Read/write multiple registers
void ADS1298R_Read_Data(unsigned char *data);//Read 9 bytes of data
void ADS1298R_SET_REGBUFF(void);//Set up the register buffer
void ADS1298R_WRITE_REGBUFF(void);//Write the register buffer into the registers

void ADS1298R_Noise_Test(void);
void ADS1298R_Single_Test(void);//Set channel 1 to the internal 1 mV test signal
void ADS1298R_Single_Read(void);//Set normal signal acquisition mode
void Set_ADS1298R_Collect(unsigned char mode);//Set the data acquisition mode

#endif


//Datasheet and forum notes:
//For CLK: internal or external clock? With the internal clock, tie the pin to ground. With an external clock, drive it from an active crystal or an MCU clock output pin.
//With the internal oscillator, CONFIG2 bit3 = 1 enables the CLK output at the internal clock frequency; bit3 = 0 disables the CLK output
//SCLK is the SPI clock rate; per the datasheet: 2.7 V ≤ DVDD ≤ 3.6 V → tSCLK(min) = 50 ns; 1.7 V ≤ DVDD ≤ 2 V → tSCLK(min) = 66.6 ns

//1. Registers cannot be accessed in continuous read mode; send SDATAC first to leave that mode before issuing other commands.
//2. Per the datasheet, the 1292 takes 7.2 us to parse each byte of a multi-byte command; leave at least 8 us between bytes
//Test procedure
//	Set CLKSEL = 1 	use the internal clock
//	Set PWDN/RESET = 1  wait 1 s for power-on reset and oscillator startup
//	Send the SDATAC command  then configure the registers
//	Send WREG CONFIG2 A0h	use the internal reference voltage
//	Set START = 1		to start conversions
//	Send the RDATAC command	to return the device to RDATAC mode
//	Capture data and check the noise
//	Capture data and test the signal

