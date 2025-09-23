#ifndef __ADS1294_H
#define __ADS1294_H	 


/////////////////////////////////////////////////////////////////////////////////////////////
//声明变量

// unsigned char ADS1294_recive_flag=0;	//锟斤拷锟捷讹拷取锟斤拷杀锟街�


//ADS1294R命令定义
//系统命令
	#define WAKEUP	0X02	//从待机模式唤醒
	#define STANDBY	0X04	//进入待机模式
//	#define RESET	0X06	//复位ADS1294R
	#define START	0X08	//启动或转换
	#define STOP	0X0A	//停止转换
	//#define OFFSETCAL	0X1A	//通道偏移校准

//数据读取命令
	#define RDATAC	0X10	//启用连续的数据读取模式,默认使用此模式
	#define SDATAC	0X11	//停止连续的数据读取模式
	#define RDATA		0X12	//通过命令读取数据;支持多种读回。
//寄存器读取命令
	//r rrrr=要读、写的寄存器首地址	 //	n nnnn=要读写的寄存器数量
	#define RREG	0X20	//读取  001r rrrr(首字节) 000n nnnn(2字节)
	#define WREG	0X40	//写入  010r rrrr(首字节) 000n nnnn(2字节)

//ADS1294R内部寄存器地址定义
	#define ID					0	//ID控制寄存器
	#define CONFIG1			1	//配置寄存器1
	#define CONFIG2			2	//配置寄存器2
	#define CONFIG3			3	//配置寄存器2
	#define LOFF				4	//导联脱落控制寄存器
	#define CH1SET			5	//通道1设置寄存器
	#define CH2SET			6	//通道2设置寄存器
	#define CH3SET			7	//通道3设置寄存器
	#define CH4SET			8	//通道4设置寄存器
	#define CH5SET			9	//通道5设置寄存器
	#define CH6SET			10	//通道6设置寄存器
	#define CH7SET			11	//通道7设置寄存器
	#define CH8SET			12	//通道8设置寄存器
	#define RLD_SENSP		13	//右腿驱动选择寄存器
	#define RLD_SENSN		14	//右腿驱动选择寄存器
	#define LOFF_SENSP	15	//正信号导联脱落检测寄存器
	#define LOFF_SENSN	16	//负信号导联脱落检测寄存器
	#define LOFF_FLIP		17	//导联脱落翻转寄存器
	#define LOFF_STATP	18	//导联脱落正信号状态寄存器
	#define LOFF_STATN	19	//导联脱落负信号状态寄存器
	#define	GPIO				20  //GPIO控制寄存器
	#define	PACE				21  //起搏信号检测寄存器
	#define	RESP				22	//呼吸控制寄存器
	#define CONFIG4			23	//配置寄存器4
	#define WCT1			  24	//威尔逊中心端子控制寄存器
  #define WCT2			  25	//威尔逊中心端子控制寄存器

  //DeviceId
  #define	DEVICE_ID_ADS1294R	0Xd0
	//CONFIG1
	#define HR_LP_Mode  0
	#define HR_HR_Mode  1
	#define DAISY_ENABLE  0// Daisy_chain mode
	#define DAISY_DISENABLE  1// Multiple readback mode
	#define CLK_DISEN_OUTPUT 0// OSCILLATOR clock output disabled
	#define CLK_EN_OUTPUT 1// OSCILLATOR clock output enabled
	#define	DATA_RATE_HR_32kSPS	0	//采样率
	#define	DATA_RATE_LP_16kSPS	0	//采样率
	#define	DATA_RATE_HR_16kSPS	1	//采样率
	#define	DATA_RATE_LP_8kSPS	1	//采样率
	#define	DATA_RATE_HR_8kSPS	2	//采样率
	#define	DATA_RATE_LP_4kSPS	2	//采样率
	#define	DATA_RATE_HR_4kSPS	3	//采样率
	#define	DATA_RATE_LP_2kSPS	3	//采样率
	#define	DATA_RATE_HR_2kSPS	4	//采样率
	#define	DATA_RATE_LP_1kSPS	4	//采样率
	#define	DATA_RATE_HR_1kSPS	5	//采样率
	#define	DATA_RATE_LP_500SPS	5	//采样率
	#define	DATA_RATE_HR_500SPS	6	//采样率
	#define	DATA_RATE_LP_250SPS	6	//采样率
	#define	DATA_RATE_Reserved	7	//采样率
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
 }ADS1294_CONFIG1;
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
 }ADS1294_CONFIG2;

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
 }ADS1294_CONFIG3;

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
 }ADS1294_LOFCTLREG;


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
 }ADS1294_CHSETREG;

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
 }ADS1294_RLD_SENSPREG;

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
 }ADS1294_RLD_SENSNREG;


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
 }ADS1294_LOFF_SENSPREG;

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
 }ADS1294_LOFF_SENSNREG;


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
 }ADS1294_LOFF_FLIPREG;

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
 }ADS1294_LOFF_STATPREG;


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
 }ADS1294_LOFF_STATNREG;

 typedef union
 {
 struct
 {
// 	unsigned char  GPIOD:4;
// 	unsigned char  GPIOC:4;

 }REG_CONFIG;
   unsigned char  GPIOREG_Data;
 }ADS1294_GPIOREG;

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
 }ADS1294_PACEREG;


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
 }ADS1294_RESPREG;


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
 }ADS1294_CONFIG4;

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
 }ADS1294_WCT1REG;

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
 }ADS1294_WCT2REG;





void ADS1294_Init(void); //初始化ADS1294引脚
void ADS1294_PowerOnInit(void);//上电初始化
void ADS1294_Send_CMD(unsigned char data);//发送命令
void ADS1294_WR_REGS(unsigned char reg,unsigned char len,unsigned char *data);//读写多个寄存器
void ADS1294_Read_Data(unsigned char *data);//读9字节数据
void ADS1294_SET_REGBUFF(void);//设置寄存器数组
void ADS1294_WRITE_REGBUFF(void);//将寄存器数组写入寄存器

void ADS1294_Noise_Test(void);
void ADS1294_Single_Test(void);//设置通道1内部1mV测试信号
void ADS1294_Single_Read(void);//设置正常信号采集模式
void Set_ADS1294_Collect(unsigned char mode);//设置数据采集方式

#endif


//手册及论坛资料：
//关于CLK您是使用内部时钟还是使用外部时钟？如果使用内部时钟，可以将其接地。如果使用外部时钟，可以接有源晶振或者MCU的时钟输出引脚给ADS1294 提供时钟。
//使用内部晶振的话，寄存器CONFIG2的bit3 如果配置为1的话，那么CLK有输出，频率即为内部时钟产生的频率，如果配置为0的话，那么CLK输出disable
//SCLK 即为SPI的频率，它的大小datasheet已经给出，当2.7 V ≤ DVDD ≤ 3.6 V，周期tSCLK（min）=50ns。 当1.7 V ≤ DVDD ≤ 2 V时，tSCLK（min）=66.6ns

//1. 在连续读模式下，不能读写寄存器。在连续读模式下，首先要发命令停止 SDATAC 。然后才能发送其他命令。
//2. 手册里面这样描述，1292 接收多字节命令时，解析一个字节需要 7.2us。因此你发送多字节命令时，两个字节之间的间隔至少要到8us
//测试流程
//	设置 CLKSEL =1 	使用内部时钟，
//	设置 PWDN/RESET = 1  等待1秒 开机复位和等待起振
//	发送SDATAC命令  设置寄存器
//	发送WREG CONFIG2 A0h	使用内部参考电压，
//	设置START = 1		激活转换
//	发送RDATAC命令	将设备恢复到RDATAC模式
//	捕获数据并检查噪音
//	捕获数据并测试信号

