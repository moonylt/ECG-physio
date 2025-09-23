/*
该程序是PID调节的函数库
*/
#include "PID.h"
#include "dac.h"

PIDTypdDef RSencer,LSencer;

float temp_setvalue0=38;//default test
//float temp_value=0.0;
float temp_error=3.5;
float temp_error0=1.5;
float pid_recall=0;
int temp=0X50;
int F_Start=1;
int pid_count=0;

/*初始化RSencer结构体参数*/
void PID_RSencer_Init(void)
{
    RSencer.LastError  = 0;		
    RSencer.PrevError  = 0;			
		RSencer.Proportion = 0;			
    RSencer.Integral   = 0;		
    RSencer.Derivative = 0;			
    RSencer.SetPoint   = 0;    
		RSencer.SumError   = 0;     
}

/*初始化LSencer结构体参数*/
void PID_LSencer_Init(void)
{
    LSencer.LastError  = 0;	
    LSencer.PrevError  = 0;			
		LSencer.Proportion = 0;			
    LSencer.Integral   = 0;			
    LSencer.Derivative = 0;	
    LSencer.SetPoint   = 0;    
		LSencer.SumError   = 0;     
}

/*设置RSencer期望值*/
void PID_RSencer_SetPoint(float setpoint)
{	
		RSencer.SetPoint = setpoint;	
}

/*设置LSencer期望值*/
void PID_LSencer_SetPoint(float setpoint)
{	
		LSencer.SetPoint = setpoint;	
}

/*设置RSencer的PID参数*/
void PID_RSencer_SetPID(float P,float I,float D)
{
		RSencer.Proportion = P;			
    RSencer.Integral   = I;		
    RSencer.Derivative = D;
}

/*设置LSencer的PID参数*/
void PID_LSencer_SetPID(float P,float I,float D)
{
	LSencer.Proportion = P;
    LSencer.Integral   = I;			
    LSencer.Derivative = D;	
}

/*RSencer位置式PID计算*/
//调入参数为当前传感器测得的值
//返回值：PID计算后的输出值
int PID_RSencer_Calculate(float CurValue)
{
	float  iError,dError;                              //临时变量

	iError = RSencer.SetPoint - CurValue;              //偏差
	RSencer.SumError += iError;				                 //积分
	if(RSencer.SumError > 1500.0)					             //积分限幅
			RSencer.SumError = 1500.0;
	else if(RSencer.SumError < -1500.0)
			RSencer.SumError = -1500.0;	
	dError = iError - RSencer.LastError; 			         //当前微分
	RSencer.LastError = iError;
	
	return(int)(RSencer.Proportion * iError            //比例项
          	+ RSencer.Integral   * RSencer.SumError  //积分项
          	+ RSencer.Derivative * dError);          //微分项
}

/*LSencer位置式PID计算*/
//调入参数为当前传感器测得的值
//返回值：PID计算后的输出值
float PID_LSencer_Calculate(float CurValue)
{
	float  iError,dError;                              //临时变量

	iError = LSencer.SetPoint - CurValue;              //偏差
	LSencer.SumError += iError;				                 //积分
	if(LSencer.SumError > 1500.0)                      //积分限幅
			LSencer.SumError = 1500.0;
	else if(LSencer.SumError < -1500.0)
			LSencer.SumError = -1500.0;	
	dError = iError - LSencer.LastError; 			         //当前微分
	LSencer.LastError = iError;
	
	return(float)(LSencer.Proportion * iError            //比例项
          	+ LSencer.Integral   * LSencer.SumError  //积分项
            + LSencer.Derivative * dError);          //微分项
}

void pid_temp_process(float temp_value)
{
//	 int pid_count=0;
	 PID_LSencer_SetPoint(temp_setvalue0);
	 PID_LSencer_SetPID(0.1,0,1);
	 pid_recall=PID_LSencer_Calculate(temp_value);

	if((F_Start==1)&&(temp_value<37))
	{
		pid_count++;
		HAL_DAC_SetValue(&hdac,DAC_CHANNEL_1,DAC_ALIGN_8B_R,0xFF);
		if(pid_count>=180)
			F_Start=0;

	}
	else
	{
		if(temp_value>=37)
			F_Start=0;;

		if((temp_value<(temp_setvalue0))&&(pid_recall>0))
		{
	//		  HAL_DAC_SetValue(&hdac,DAC_CHANNEL_2,DAC_ALIGN_8B_R,0X20);//DAC CHANNEL INIT
	//		  HAL_DAC_Start(&hdac,DAC_CHANNEL_1);//DAC START CONVERT
	//		  HAL_DAC_SetValue(&hdac,DAC_CHANNEL_2,DAC_ALIGN_8B_R,0X50);//DAC CHANNEL INIT
			  temp++;
			  HAL_DAC_SetValue(&hdac,DAC_CHANNEL_1,DAC_ALIGN_8B_R,temp);//DAC CHANNEL INIT

	//		  if(pid_recall>0.01)
	//		  {
	//		  HAL_DAC_SetValue(&hdac,DAC_CHANNEL_1,DAC_ALIGN_8B_R,0X90);//DAC CHANNEL INIT
	//		  HAL_DAC_Start(&hdac,DAC_CHANNEL_1);//DAC START CONVERT
	//		  }
	//		  else
	//		  {
	//		  HAL_DAC_SetValue(&hdac,DAC_CHANNEL_1,DAC_ALIGN_8B_R,0X40);//DAC CHANNEL INIT
	//		  HAL_DAC_Start(&hdac,DAC_CHANNEL_1);//DAC START CONVERT
	//		  }

			  HAL_DAC_Start(&hdac,DAC_CHANNEL_1);//DAC START CONVERT
		}
		else
		{
	//		  HAL_DAC_SetValue(&hdac,DAC_CHANNEL_2,DAC_ALIGN_8B_R,0X50);//DAC CHANNEL INIT
	//		  HAL_DAC_Start(&hdac,DAC_CHANNEL_1);//DAC START CONVERT
	//		  HAL_DAC_SetValue(&hdac,DAC_CHANNEL_2,DAC_ALIGN_8B_R,0X20);//DAC CHANNEL INIT
			  temp--;
			  if (temp<0)
			   temp=0;
			  HAL_DAC_SetValue(&hdac,DAC_CHANNEL_1,DAC_ALIGN_8B_R,temp);//DAC CHANNEL INIT
			  HAL_DAC_Start(&hdac,DAC_CHANNEL_1);//DAC START CONVERT

	//		  HAL_DAC_Stop(&hdac,DAC_CHANNEL_1);//DAC STOP CONVERT
		}
	}
}
