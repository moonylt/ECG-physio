/**
 * @file    protocol.h
 * @brief   PHYSIO v2 communication protocol definitions (STM32 / ESP32)
 *
 * See 3.FIRMWARE/PROTOCOL.md for the full specification.
 * Frame: STX0(0x55) STX1(0xAA) LEN_L LEN_H SRC DST SEQ MSGID DATA[N] CRC8
 * CRC8: polynomial 0x07, init 0x00, over all bytes except the CRC itself.
 */
#ifndef PHYSIO_PROTOCOL_H
#define PHYSIO_PROTOCOL_H

#include <stdint.h>

/* Frame header and fixed fields */
#define PHY_STX0            0x55u
#define PHY_STX1            0xAAu
#define PHY_HEADER_LEN      8u    /* STX0..MSGID */
#define PHY_CRC_LEN         1u
#define PHY_FRAME_OVERHEAD  (PHY_HEADER_LEN + PHY_CRC_LEN)

/* Node addresses */
#define PHY_ADDR_PC         0x00u
#define PHY_ADDR_ESP32      0x01u
#define PHY_ADDR_STM32      0x02u

/* Message IDs */
#define PHY_MSG_ADS129X_DATA    0x20u  /* ECG/resp waveform: 4 samples x 4 ch x 3B */
#define PHY_MSG_SPO2_PPG        0x21u  /* SpO2 PPG waveform: 4 samples x 2 ch x 3B */
#define PHY_MSG_SPO2_RESULT     0x22u  /* SpO2 result: SpO2 / pulse rate / status */
#define PHY_MSG_IBP_DATA        0x23u  /* IBP waveform: 4 samples x 2 ch x 3B */
#define PHY_MSG_NIBP_RESULT     0x24u  /* NIBP result: SYS/DIA/MAP */
#define PHY_MSG_TEMP_DATA       0x25u  /* Temperature telemetry: 4 x f32 + flags */
#define PHY_MSG_LEADOFF_STATUS  0x26u  /* Lead-off status bitmask */

#define PHY_MSG_DEVICE_STATUS   0xF0u  /* accessory announce */
#define PHY_MSG_SET_GAIN        0xA0u  /* PC->device: set gain */
#define PHY_MSG_SET_TEMP_TARGET 0xA1u  /* PC->device: target temperature */
#define PHY_MSG_ACQ_CTRL        0xA2u  /* PC->device: acquisition start/stop */

/* Accessory bitmask (PHY_MSG_DEVICE_STATUS) */
#define PHY_ACC_ECG     (1u << 0)
#define PHY_ACC_SPO2    (1u << 1)
#define PHY_ACC_TSKIN   (1u << 2)   /* skin temperature, TMP117 */
#define PHY_ACC_TRECT   (1u << 3)   /* rectal temp, MAX31856 */
#define PHY_ACC_IBP     (1u << 4)
#define PHY_ACC_NIBP    (1u << 5)
#define PHY_ACC_HEATER  (1u << 6)

/* Waveform channel counts */
#define PHY_ECG_CHANNELS    4u
#define PHY_SPO2_CHANNELS   2u
#define PHY_IBP_CHANNELS    2u
#define PHY_SAMPLES_PER_FRAME 4u

/* DATA payload lengths */
#define PHY_LEN_ADS129X_DATA  (PHY_SAMPLES_PER_FRAME * PHY_ECG_CHANNELS * 3u)   /* 48 */
#define PHY_LEN_SPO2_PPG      (PHY_SAMPLES_PER_FRAME * PHY_SPO2_CHANNELS * 3u)  /* 24 */
#define PHY_LEN_IBP_DATA      (PHY_SAMPLES_PER_FRAME * PHY_IBP_CHANNELS * 3u)   /* 24 */
#define PHY_LEN_SPO2_RESULT   8u
#define PHY_LEN_NIBP_RESULT   8u
#define PHY_LEN_TEMP_DATA     (4u * 4u + 1u)                                     /* 17 */
#define PHY_LEN_LEADOFF       2u
#define PHY_LEN_DEVICE_STATUS 4u

/* TEMP_DATA flag bits */
#define PHY_TEMP_FLAG_TSKIN_OK   (1u << 0)
#define PHY_TEMP_FLAG_TRECT_OK   (1u << 1)
#define PHY_TEMP_FLAG_HEATER_OT  (1u << 2)  /* heater over-temperature */
#define PHY_TEMP_FLAG_TC_OPEN    (1u << 3)  /* thermocouple open */

/**
 * @brief  CRC8 (poly 0x07, init 0x00)
 */
static inline uint8_t phy_crc8(const uint8_t *data, uint32_t len)
{
    uint8_t crc = 0;
    for (uint32_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            crc = (crc & 0x80u) ? (uint8_t)((crc << 1) ^ 0x07u) : (uint8_t)(crc << 1);
        }
    }
    return crc;
}

/**
 * @brief  Build one frame. buf must hold >= header + data_len + crc bytes.
 * @return total frame length in bytes
 */
static inline uint32_t phy_build_frame(uint8_t *buf, uint8_t src, uint8_t dst,
                                       uint8_t seq, uint8_t msgid,
                                       const uint8_t *data, uint16_t data_len)
{
    uint32_t idx = 0;
    buf[idx++] = PHY_STX0;
    buf[idx++] = PHY_STX1;
    buf[idx++] = (uint8_t)(data_len & 0xFFu);        /* LEN low byte */
    buf[idx++] = (uint8_t)((data_len >> 8) & 0xFFu); /* LEN high byte */
    buf[idx++] = src;
    buf[idx++] = dst;
    buf[idx++] = seq;
    buf[idx++] = msgid;
    for (uint16_t i = 0; i < data_len; i++) {
        buf[idx++] = data[i];
    }
    buf[idx] = phy_crc8(buf, idx);
    return idx + 1;
}

/**
 * @brief  Convert big-endian signed 24-bit sample to int32
 */
static inline int32_t phy_s24_to_i32(const uint8_t *p)
{
    int32_t v = ((int32_t)p[0] << 16) | ((int32_t)p[1] << 8) | (int32_t)p[2];
    if (v >= 0x800000) {
        v -= 0x1000000;
    }
    return v;
}

#endif /* PHYSIO_PROTOCOL_H */
