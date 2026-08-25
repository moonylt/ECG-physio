/*
*/
#ifndef PID_H
#define PID_H	 
//#include "sys.h"

/* PID struct definition */
typedef struct
{
	float  SetPoint; 	// Desired target
	double  SumError;	// Accumulated error
		
	float  Proportion;  // Proportional coefficient
	float  Integral;    // Integral coefficient
	float  Derivative;  // Derivative coefficient

	float  LastError;   // Previous error
	float  PrevError;   // Error before previous
}PIDTypdDef;

extern PIDTypdDef RSencer,LSencer;
//float temp_setvalue0=38;//default test

void pid_temp_process(float temp_value);
/* Initialize RSencer struct */
void PID_RSencer_Init(void);
/* Initialize LSencer struct */
void PID_LSencer_Init(void);
/* Set RSencer setpoint */
void PID_RSencer_SetPoint(float setpoint);
/* Set LSencer setpoint */
void PID_LSencer_SetPoint(float setpoint);
/* Set RSencer PID parameters */
void PID_RSencer_SetPID(float P,float I,float D);
	/* Set LSencer PID parameters */
void PID_LSencer_SetPID(float P,float I,float D);
/* RSencer positional PID */
// Input: currently measured value
// Output: PID-computed result
int PID_RSencer_Calculate(float CurValue);
/* LSencer positional PID */
// Input: currently measured value
// Output: PID-computed result
float PID_LSencer_Calculate(float CurValue);
		 				    
#endif
