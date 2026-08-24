/**
 * @file    physio_app.c
 * @brief   PHYSIO application layer
 */

#include "physio_app.h"
#include <string.h>
#include "usart.h"
#include "../../../../protocol.h"   /* 3.FIRMWARE/protocol.h */
#include "AFE4490.h"
#include "MAX31856drv.h"
#include "PID.h"
#include "i2c.h"

extern float f_linearized_tc_temperature;   /* MAX31856drv.c */

/* ------------------------------------------------------------------ */
/* UART5 TX (forwarded to the console via the ESP32 bridge)                                */
/* ------------------------------------------------------------------ */
#define PHY_UART_BAUD   819200   /* 32768000/819200 = 40, exact integer divider */

static uint8_t  phy_txbuf[PHY_HEADER_LEN + 64 + PHY_CRC_LEN];
static uint8_t  phy_tx_seq = 0;

static void physio_send(uint8_t msgid, const uint8_t *data, uint16_t len)
{
    uint32_t n = phy_build_frame(phy_txbuf, PHY_ADDR_STM32, PHY_ADDR_PC,
                                 phy_tx_seq++, msgid, data, len);
    HAL_UART_Transmit(&huart5, phy_txbuf, n, 20);
}

/* Pack signed 24-bit, big-endian */
static void pack_s24(uint8_t *p, int32_t v)
{
    if (v >  0x7FFFFF) v =  0x7FFFFF;
    if (v < -0x800000) v = -0x800000;
    p[0] = (uint8_t)(v >> 16);
    p[1] = (uint8_t)(v >> 8);
    p[2] = (uint8_t)v;
}

static void pack_f32(uint8_t *p, float f)
{
    memcpy(p, &f, 4);   /* Cortex-M4 is little-endian, matching the protocol */
}

/* ------------------------------------------------------------------ */
/* Simulated waveform generator (128-point sine LUT, no libm)                                */
/* ------------------------------------------------------------------ */
static const float sin_lut[128] = {
0.00000f, 0.04907f, 0.09802f, 0.14673f, 0.19509f, 0.24298f, 0.29028f, 0.33689f,
0.38268f, 0.42756f, 0.47140f, 0.51410f, 0.55557f, 0.59570f, 0.63439f, 0.67156f,
0.70711f, 0.74095f, 0.77301f, 0.80321f, 0.83147f, 0.85773f, 0.88192f, 0.90399f,
0.92388f, 0.94154f, 0.95694f, 0.97003f, 0.98079f, 0.98918f, 0.99518f, 0.99880f,
1.00000f, 0.99880f, 0.99518f, 0.98918f, 0.98079f, 0.97003f, 0.95694f, 0.94154f,
0.92388f, 0.90399f, 0.88192f, 0.85773f, 0.83147f, 0.80321f, 0.77301f, 0.74095f,
0.70711f, 0.67156f, 0.63439f, 0.59570f, 0.55557f, 0.51410f, 0.47140f, 0.42756f,
0.38268f, 0.33689f, 0.29028f, 0.24298f, 0.19509f, 0.14673f, 0.09802f, 0.04907f,
0.00000f,-0.04907f,-0.09802f,-0.14673f,-0.19509f,-0.24298f,-0.29028f,-0.33689f,
-0.38268f,-0.42756f,-0.47140f,-0.51410f,-0.55557f,-0.59570f,-0.63439f,-0.67156f,
-0.70711f,-0.74095f,-0.77301f,-0.80321f,-0.83147f,-0.85773f,-0.88192f,-0.90399f,
-0.92388f,-0.94154f,-0.95694f,-0.97003f,-0.98079f,-0.98918f,-0.99518f,-0.99880f,
-1.00000f,-0.99880f,-0.99518f,-0.98918f,-0.98079f,-0.97003f,-0.95694f,-0.94154f,
-0.92388f,-0.90399f,-0.88192f,-0.85773f,-0.83147f,-0.80321f,-0.77301f,-0.74095f,
-0.70711f,-0.67156f,-0.63439f,-0.59570f,-0.55557f,-0.51410f,-0.47140f,-0.42756f,
-0.38268f,-0.33689f,-0.29028f,-0.24298f,-0.19509f,-0.14673f,-0.09802f,-0.04907f
};

static float lut_sinf(float x)   /* x in [0,1), returns sin(2*pi*x) */
{
    int i = (int)(x * 128.0f) & 0x7F;
    return sin_lut[i];
}

/* Simulation parameters (typical rodent values) */
#define SIM_ECG_FS      500     /* ECG sample rate */
#define SIM_HEART_FS    7.5f    /* heart rate 450bpm */
#define SIM_RESP_FS     1.2f    /* resp rate 72bpm */
#define SIM_PPG_FS      100     /* PPG sample rate */

static float sim_ecg_phase = 0.0f;
static float sim_resp_phase = 0.0f;
static float sim_ppg_phase = 0.0f;

/* PQRST complex: phase in [0,1) */
static float sim_pqrst(float phase)
{
    float v = 0;
    float p, qrs, t;

    p = phase - 0.10f;                          /* P wave */
    if (p > -0.10f && p < 0.10f) v += 0.15f * lut_sinf(p * 5.0f + 0.5f);

    qrs = phase - 0.30f;                        /* QRS complex */
    if (qrs > -0.05f && qrs < 0.05f) v += 1.0f * lut_sinf(qrs * 10.0f + 0.5f);
    if (qrs > -0.02f && qrs < 0.02f) v += 0.3f * lut_sinf(qrs * 25.0f + 0.5f);

    t = phase - 0.50f;                          /* T wave */
    if (t > -0.15f && t < 0.15f) v += 0.3f * lut_sinf(t * 3.333f + 0.5f);

    return v;
}

static int32_t sim_ecg_ch(int ch)               /* CH0=resp, CH1..3=ECG */
{
    if (ch == 0)
        return (int32_t)(lut_sinf(sim_resp_phase) * 2000000);
    {
        float scale = (ch == 1) ? 1.0f : (ch == 2) ? 1.5f : 0.8f;
        return (int32_t)(sim_pqrst(sim_ecg_phase) * scale * 4000000);
    }
}

static int32_t sim_ppg_ch(int ch)               /* CH0=IR, CH1=RED */
{
    float amp = (ch == 0) ? 1.0f : 0.75f;
    float v = 0.55f + 0.45f * lut_sinf(sim_ppg_phase);
    return (int32_t)(v * amp * 1500000);
}

/* ------------------------------------------------------------------ */
/* Real mode: ISR buffers                                                   */
/* ------------------------------------------------------------------ */
#define SPO2_DECIM  10          /* AFE4490 PRF ~1kHz -> 100sps output */

#if !PHYSIO_SIM_MODE
static uint8_t  ecg_pending[PHY_LEN_ADS129X_DATA];
static volatile uint8_t ecg_pending_ready = 0;
static uint8_t  ecg_sample_cnt = 0;

static uint8_t  ppg_pending[PHY_LEN_SPO2_PPG];
static volatile uint8_t ppg_pending_ready = 0;
static uint8_t  ppg_sample_cnt = 0;
static uint16_t ppg_decim_cnt = 0;
#endif

void physio_app_ecg_from_isr(const uint8_t ads_raw[27])
{
#if !PHYSIO_SIM_MODE
    /* ADS1298R 27-byte frame: [0..2]status [3..5]CH1 resp [6..8]CH2 lead-I
     * [9..11]CH3 lead-II [12..14]CH4 lead-III *
    uint8_t *p = &ecg_pending[ecg_sample_cnt * 12];
    pack_s24(p + 0,  phy_s24_to_i32(&ads_raw[3]));    /* CH0 respiration     */
    pack_s24(p + 3,  phy_s24_to_i32(&ads_raw[6]));    /* CH1 lead I   */
    pack_s24(p + 6,  phy_s24_to_i32(&ads_raw[9]));    /* CH2 lead II  */
    pack_s24(p + 9,  phy_s24_to_i32(&ads_raw[12]));   /* CH3 lead III */

    if (++ecg_sample_cnt >= PHY_SAMPLES_PER_FRAME) {
        ecg_sample_cnt = 0;
        ecg_pending_ready = 1;
    }
#else
    (void)ads_raw;
#endif
}

void physio_app_spo2_from_isr(void)
{
#if !PHYSIO_SIM_MODE
    int32_t ir, red;

    if (++ppg_decim_cnt < SPO2_DECIM) return;
    ppg_decim_cnt = 0;

    AFE4490_ReadSample(&ir, &red);
    pack_s24(&ppg_pending[ppg_sample_cnt * 6],     ir);
    pack_s24(&ppg_pending[ppg_sample_cnt * 6 + 3], red);

    if (++ppg_sample_cnt >= PHY_SAMPLES_PER_FRAME) {
        ppg_sample_cnt = 0;
        ppg_pending_ready = 1;
    }
#endif
}

/* ------------------------------------------------------------------ */
/* Periodic task scheduler (polled from the main loop, non-blocking)                                    */
/* ------------------------------------------------------------------ */
void physio_app_init(void)
{
    /* Re-init UART5 at a higher rate (the CubeMX default lacks bandwidth for 4ch @ 500sps)
     * full DeInit->Init cycle so BRR and control registers are recomputed cleanly */
    HAL_UART_DeInit(&huart5);
    huart5.Init.BaudRate = PHY_UART_BAUD;
    HAL_UART_Init(&huart5);

#if !PHYSIO_SIM_MODE
    uint8_t d[PHY_LEN_DEVICE_STATUS];
    uint16_t acc;

    AFE4490_Init();
    HAL_NVIC_EnableIRQ(EXTI1_IRQn);       /* AFE4490 ADC_RDY (PG1) */

    acc = PHY_ACC_ECG | PHY_ACC_SPO2 | PHY_ACC_TSKIN | PHY_ACC_TRECT | PHY_ACC_HEATER;
    d[0] = acc & 0xFF; d[1] = acc >> 8;
    d[2] = 0x01; d[3] = 0;
    physio_send(PHY_MSG_DEVICE_STATUS, d, PHY_LEN_DEVICE_STATUS);
#endif
}

void physio_app_poll(void)
{
    uint32_t now = HAL_GetTick();

    /* ---- Pending frames (filled by ISRs in real mode) ---- */
#if !PHYSIO_SIM_MODE
    if (ecg_pending_ready) {
        ecg_pending_ready = 0;
        physio_send(PHY_MSG_ADS129X_DATA, ecg_pending, PHY_LEN_ADS129X_DATA);
    }
    if (ppg_pending_ready) {
        ppg_pending_ready = 0;
        physio_send(PHY_MSG_SPO2_PPG, ppg_pending, PHY_LEN_SPO2_PPG);
    }
#endif

#if PHYSIO_SIM_MODE
    /* ---- Simulated data (hardcoded, for console bring-up) ---- */
    static uint32_t t_ecg, t_ppg, t_slow, t_stat;

    if (now - t_ecg >= 8) {                       /* 500sps / 4 samples = 125fps */
        uint8_t d[PHY_LEN_ADS129X_DATA];
        int s, ch;
        t_ecg = now;
        for (s = 0; s < PHY_SAMPLES_PER_FRAME; s++) {
            for (ch = 0; ch < PHY_ECG_CHANNELS; ch++)
                pack_s24(&d[(s * 4 + ch) * 3], sim_ecg_ch(ch));
            sim_ecg_phase  = sim_ecg_phase  + SIM_HEART_FS / SIM_ECG_FS;
            sim_resp_phase = sim_resp_phase + SIM_RESP_FS / SIM_ECG_FS;
            if (sim_ecg_phase  >= 1.0f) sim_ecg_phase  -= 1.0f;
            if (sim_resp_phase >= 1.0f) sim_resp_phase -= 1.0f;
        }
        physio_send(PHY_MSG_ADS129X_DATA, d, PHY_LEN_ADS129X_DATA);
    }

    if (now - t_ppg >= 40) {                      /* 100sps / 4 samples = 25fps */
        uint8_t d[PHY_LEN_SPO2_PPG];
        int s, ch;
        t_ppg = now;
        for (s = 0; s < PHY_SAMPLES_PER_FRAME; s++) {
            for (ch = 0; ch < PHY_SPO2_CHANNELS; ch++)
                pack_s24(&d[(s * 2 + ch) * 3], sim_ppg_ch(ch));
            sim_ppg_phase += SIM_HEART_FS / SIM_PPG_FS;
            if (sim_ppg_phase >= 1.0f) sim_ppg_phase -= 1.0f;
        }
        physio_send(PHY_MSG_SPO2_PPG, d, PHY_LEN_SPO2_PPG);
    }

    if (now - t_slow >= 2000) {                   /* temp + SpO2 result @ 0.5Hz */
        uint8_t d[PHY_LEN_TEMP_DATA];
        uint8_t r[PHY_LEN_SPO2_RESULT];
        t_slow = now;
        pack_f32(&d[0],  37.5f);                  /* skin temp */
        pack_f32(&d[4],  38.2f);                  /* rectal temp     */
        pack_f32(&d[8],  40.0f);                  /* heater plate   */
        pack_f32(&d[12], 25.0f);                  /* cold junction     */
        d[16] = PHY_TEMP_FLAG_TSKIN_OK | PHY_TEMP_FLAG_TRECT_OK;
        physio_send(PHY_MSG_TEMP_DATA, d, PHY_LEN_TEMP_DATA);

        r[0] = 980 & 0xFF; r[1] = 980 >> 8;    /* SpO2 98.0% (u16, %x10) */
        r[2] = 450 & 0xFF; r[3] = 450 >> 8;    /* pulse rate 450bpm (u16) */
        r[4] = 0x01; r[5] = 0; r[6] = 0; r[7] = 0;
        physio_send(PHY_MSG_SPO2_RESULT, r, PHY_LEN_SPO2_RESULT);
    }

    if (now - t_stat >= 5000) {                   /* accessory announce 0.2Hz */
        uint8_t d[PHY_LEN_DEVICE_STATUS];
        uint16_t acc = PHY_ACC_ECG | PHY_ACC_SPO2 | PHY_ACC_TSKIN |
                       PHY_ACC_TRECT | PHY_ACC_HEATER;
        t_stat = now;
        d[0] = acc & 0xFF; d[1] = acc >> 8;
        d[2] = 0x01;                              /* FW v0.1 */
        d[3] = 0;
        physio_send(PHY_MSG_DEVICE_STATUS, d, PHY_LEN_DEVICE_STATUS);
    }

#else /* real mode */
    /* ---- Temperature + PID (2s period) ---- */
    static uint32_t t_temp;
    static uint8_t  tmp_raw[2];
    static uint8_t  tmp_cold[2];

    if (now - t_temp >= 2000) {
        uint8_t d[PHY_LEN_TEMP_DATA];
        float t_rect;
        t_temp = now;
        TMP_I2C_Read(TMP117_2, 0x00, tmp_raw, 2);              /* heater plate temp */
        pid_temp_process(TMP_data_process(tmp_raw));
        maxim_31856_conversion_result_process();               /* rectal (thermocouple) */
        TMP_I2C_Read(TMP117_1, 0x00, tmp_cold, 2);             /* thermocouple cold junction */

        /* Gate implausible values: an open or unplugged thermocouple reads full scale */
        t_rect = f_linearized_tc_temperature;

        pack_f32(&d[0],  0.0f);                                /* skin NTC: not yet implemented */
        pack_f32(&d[4],  t_rect);
        pack_f32(&d[8],  TMP_data_process(tmp_raw));
        pack_f32(&d[12], TMP_data_process(tmp_cold));
        d[16] = 0;
        if (t_rect > -20.0f && t_rect < 200.0f)
            d[16] |= PHY_TEMP_FLAG_TRECT_OK;
        else {
            pack_f32(&d[4], 0.0f);                             /* open: zero + fault flag */
            d[16] |= PHY_TEMP_FLAG_TC_OPEN;
        }
        physio_send(PHY_MSG_TEMP_DATA, d, PHY_LEN_TEMP_DATA);
    }

    /* ---- accessory announce ---- */
    {
        static uint32_t t_stat;
        if (now - t_stat >= 5000) {
            uint8_t d[PHY_LEN_DEVICE_STATUS];
            uint16_t acc = PHY_ACC_ECG | PHY_ACC_TSKIN | PHY_ACC_TRECT | PHY_ACC_HEATER;
            t_stat = now;
            d[0] = acc & 0xFF; d[1] = acc >> 8;
            d[2] = 0x01;
            d[3] = 0;
            physio_send(PHY_MSG_DEVICE_STATUS, d, PHY_LEN_DEVICE_STATUS);
        }
    }
#endif
}
