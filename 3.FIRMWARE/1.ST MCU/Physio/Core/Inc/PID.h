/*
PID regulation library.
2026-08: rewritten for auto-tuning - all parameters are runtime-writable
globals (g_ prefix) so they can be adjusted via J-Link RAM access without
rebuilding. Structure: feedforward (FF) + PI + derivative-on-measurement (D)
+ actuator slew-rate limit.
*/
#ifndef PID_H
#define PID_H

#include <stdint.h>

/* Target temperature, degC. May be changed at runtime (J-Link or ISR test hook) */
extern float temp_setvalue0;

void pid_temp_process(float temp_value);

/* Runtime-writable tuning parameters (see PID.c for meanings) */
extern volatile float   g_ff;
extern volatile float   g_kp;
extern volatile float   g_ki;
extern volatile float   g_kd;
extern volatile float   g_amb;
extern volatile uint8_t g_slew;
extern volatile uint8_t g_preheat;
extern volatile uint8_t g_enable;

#endif
