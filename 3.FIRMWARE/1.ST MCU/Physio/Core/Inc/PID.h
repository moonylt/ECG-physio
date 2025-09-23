/*
*/
#ifndef PID_H
#define PID_H	 
//#include "sys.h"

/*PID�ṹ�����*/
typedef struct
{
	float  SetPoint; 	//�趨Ŀ��
	double  SumError;	//����ۼ� 
		
	float  Proportion;  //�������� 
	float  Integral;    //���ֳ���
	float  Derivative;  //΢�ֳ���

	float  LastError;   //��һ�����
	float  PrevError;   //ǰһ�����
}PIDTypdDef;

extern PIDTypdDef RSencer,LSencer;
//float temp_setvalue0=38;//default test

void pid_temp_process(float temp_value);
/*��ʼ��RSencer�ṹ�����*/
void PID_RSencer_Init(void);
/*��ʼ��LSencer�ṹ�����*/
void PID_LSencer_Init(void);
/*����RSencer����ֵ*/
void PID_RSencer_SetPoint(float setpoint);
/*����LSencer����ֵ*/
void PID_LSencer_SetPoint(float setpoint);
/*����RSencer��PID����*/
void PID_RSencer_SetPID(float P,float I,float D);
	/*����LSencer��PID����*/
void PID_LSencer_SetPID(float P,float I,float D);
/*RSencerλ��ʽPID����*/
//�������Ϊ��ǰ��������õ�ֵ
//����ֵ��PID���������ֵ
int PID_RSencer_Calculate(float CurValue);
/*LSencerλ��ʽPID����*/
//�������Ϊ��ǰ��������õ�ֵ
//����ֵ��PID���������ֵ
float PID_LSencer_Calculate(float CurValue);
		 				    
#endif
