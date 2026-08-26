/*
PID regulation library.
2026-08: rewritten for auto-tuning - all parameters are runtime-writable
globals (g_ prefix) so they can be adjusted via J-Link RAM access without
rebuilding. Structure: feedforward (FF) + PI + derivative-on-measurement (D)
+ actuator slew-rate limit.
*/
#include "PID.h"
#include "dac.h"

float temp_setvalue0=38;//default test
float pid_recall=0;
int temp=0X50;
int F_Start=1;

/* ---- Auto-tuning parameters (written at runtime via J-Link) ---- */
volatile float   g_ff      = 4.8f;   /* feedforward: DAC counts per degC */
volatile float   g_kp      = 14.0f;  /* proportional gain */
volatile float   g_ki      = 0.25f;  /* integral gain (per 2s cycle) */
volatile float   g_kd      = 10.0f;  /* derivative on measurement (avoids setpoint kick) */
volatile float   g_amb     = 26.0f;  /* assumed ambient temperature, degC */
volatile uint8_t g_slew    = 4;      /* actuator max change per cycle, counts */
volatile uint8_t g_preheat = 0x8C;   /* output upper clamp (cold-start power cap) */
volatile uint8_t g_enable  = 1;      /* 0 disables heating (natural cooldown) */

/* ---- Internal state ---- */
static float pid_integ  = 0.0f;
static float pid_last_t = 0.0f;
static float pid_dac_f  = 0.0f;

static float clampf(float v, float lo, float hi)
{
	return (v < lo) ? lo : (v > hi) ? hi : v;
}

void pid_temp_process(float temp_value)
{
	float err, u, d_t, ff;

	err = temp_setvalue0 - temp_value;
	pid_recall = err;                      /* for external observation */

	if (!g_enable) {                       /* cooldown mode: heater off */
		pid_integ = 0.0f;
		pid_dac_f = 0.0f;
		HAL_DAC_SetValue(&hdac,DAC_CHANNEL_1,DAC_ALIGN_8B_R,0);
		HAL_DAC_Start(&hdac,DAC_CHANNEL_1);
		pid_last_t = temp_value;
		return;
	}

	{
		/* Unified PID: FF + P + I (conditional + bleed-on-zero-cross) + D on
		 * measurement, output clamped to [0, g_preheat] */
		float u_raw;
		static float last_err = 0.0f;

		/* Error zero-cross: halve the integral to cancel approach-phase
		 * windup that would otherwise cause overshoot */
		if (err * last_err < 0.0f)
			pid_integ *= 0.5f;
		last_err = err;

		d_t = temp_value - pid_last_t;
		ff  = g_ff * (temp_setvalue0 - g_amb);

		u_raw = ff + g_kp * err + pid_integ - g_kd * d_t;

		/* Anti-windup: integrate only when unsaturated */
		if (u_raw > 0.0f && u_raw < (float)g_preheat)
			pid_integ = clampf(pid_integ + g_ki * err, -80.0f, 80.0f);

		u = clampf(ff + g_kp * err + pid_integ - g_kd * d_t, 0.0f, (float)g_preheat);

		/* Actuator slew-rate limit */
		if (u > pid_dac_f + g_slew)      u = pid_dac_f + g_slew;
		else if (u < pid_dac_f - g_slew) u = pid_dac_f - g_slew;
		pid_dac_f = u;
	}

	HAL_DAC_SetValue(&hdac,DAC_CHANNEL_1,DAC_ALIGN_8B_R,(uint32_t)pid_dac_f);
	HAL_DAC_Start(&hdac,DAC_CHANNEL_1);
	pid_last_t = temp_value;

	/* Legacy debug observables */
	temp = (int)pid_dac_f;
	F_Start = (temp_value < temp_setvalue0 - 2.0f) ? 1 : 0;
}
