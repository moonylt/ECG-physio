/**
 * ECG WiFi Bridge - main program
 *
 * - Creates a WiFi SoftAP
 * - Runs a TCP server
 * - Sends simulated ECG data (test mode) or forwards STM32 data (real mode)
 */

#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <errno.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_netif.h"
#include "lwip/err.h"
#include "lwip/sockets.h"
#include "lwip/sys.h"
#include "driver/uart.h"

// MAC 地址打印宏
#ifndef MACSTR
#define MACSTR "%02x:%02x:%02x:%02x:%02x:%02x"
#endif
#ifndef MAC2STR
#define MAC2STR(a) (a)[0], (a)[1], (a)[2], (a)[3], (a)[4], (a)[5]
#endif

static const char *TAG = "ECG_BRIDGE";

// 配置参数（从 Kconfig 读取）
#define ECG_SSID        CONFIG_ECG_WIFI_SSID
#define ECG_PASSWORD    CONFIG_ECG_WIFI_PASSWORD
#define ECG_CHANNEL     CONFIG_ECG_WIFI_CHANNEL
#define ECG_TCP_PORT    CONFIG_ECG_TCP_PORT
#define ECG_DATA_MODE   CONFIG_ECG_DATA_MODE
#define ECG_FRAME_RATE  CONFIG_ECG_FRAME_RATE
#define ECG_UART_BAUD   CONFIG_ECG_UART_BAUD

// ECG frame format (matches the console protocol)
// STX0 + STX1 + LEN_L + LEN_H + SRC + DST + SEQ + MSGID + DATA(48B) + CRC = 57 bytes
#define ECG_FRAME_SIZE      57
#define ECG_STX0            0x55
#define ECG_STX1            0xAA
#define ECG_MSG_ADS129X_DATA 0x20
#define ECG_NUM_CHANNELS    4
#define ECG_SAMPLES_PER_FRAME 4

// TCP 缓冲区
#define TCP_BUF_SIZE        4096

// 全局变量
static int server_socket = -1;
static int client_socket = -1;
static volatile bool client_connected = false;

// 模拟 ECG 波形参数
static float ecg_phase[ECG_NUM_CHANNELS] = {0, 0, 0, 0};
static uint16_t frame_counter = 0;

/**
 * Compute the CRC8 checksum
 */
static uint8_t calculate_crc8(const uint8_t *data, size_t len)
{
    uint8_t crc = 0;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int j = 0; j < 8; j++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x07;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

/**
 * Generate a simulated ECG sample value
 * 不同通道生成不同波形便于观察：
 * CH0: 呼吸波形（低频 0.2Hz）
 * CH1: 标准 ECG 波形
 * CH2: ECG 波形（幅度加大 50%）
 * CH3: ECG 波形（带更多噪声）
 */
static int32_t generate_ecg_sample(int channel, float phase)
{
    float value = 0;

    // CH0: 呼吸波形（低频正弦波）
    if (channel == 0) {
        // respiration waveform
        value = 0.5f * sinf(phase * 6.28f);
        // 添加一些小波动
        value += 0.1f * sinf(phase * 12.56f);
        // 缩放
        int32_t sample = (int32_t)(value * 2000000);  // 较小幅度
        return sample;
    }

    // CH1-CH3: ECG 波形（不同参数）
    float amplitude_scale = 1.0f;
    float noise_level = 0.02f;

    if (channel == 1) {
        amplitude_scale = 1.0f;    // 标准 ECG
        noise_level = 0.01f;
    } else if (channel == 2) {
        amplitude_scale = 1.5f;    // 幅度加大 50%
        noise_level = 0.02f;
    } else if (channel == 3) {
        amplitude_scale = 0.8f;    // 幅度减小
        noise_level = 0.05f;       // 更多噪声
    }

    // P wave
    float p_phase = phase - 0.1f;
    if (p_phase > -0.1f && p_phase < 0.1f) {
        value += 0.15f * amplitude_scale * sinf(p_phase * 31.4f);
    }

    // QRS complex
    float qrs_phase = phase - 0.3f;
    if (qrs_phase > -0.05f && qrs_phase < 0.05f) {
        value += 1.0f * amplitude_scale * sinf(qrs_phase * 62.8f);
    }
    if (qrs_phase > -0.02f && qrs_phase < 0.02f) {
        value += 0.3f * amplitude_scale * sinf(qrs_phase * 157.0f);
    }

    // T wave
    float t_phase = phase - 0.5f;
    if (t_phase > -0.15f && t_phase < 0.15f) {
        value += 0.3f * amplitude_scale * sinf(t_phase * 20.9f);
    }

    // add noise
    value += (float)(rand() % 100 - 50) / 1000.0f * (noise_level * 50);

    // scale to 24-bit range (+/-8388608)
    int32_t sample = (int32_t)(value * 4000000);

    return sample;
}

/**
 * Build one ECG data frame
 * 帧格式：STX0(1B) + STX1(1B) + LEN_L(1B) + LEN_H(1B) + SRC(1B) + DST(1B) + SEQ(1B) + MSGID(1B) + DATA(48B) + CRC(1B) = 57 字节
 */
static void build_ecg_frame(uint8_t *frame)
{
    int idx = 0;

    // frame header
    frame[idx++] = ECG_STX0;
    frame[idx++] = ECG_STX1;

    // payload length (48 bytes)
    frame[idx++] = 48;          // LEN_L
    frame[idx++] = 0;           // LEN_H

    // source / destination addresses
    frame[idx++] = 0x01;        // SRC: ESP32
    frame[idx++] = 0x00;        // DST: PC

    // sequence number
    frame[idx++] = frame_counter & 0xFF;
    frame_counter++;

    // message type
    frame[idx++] = ECG_MSG_ADS129X_DATA;

    // 4 samples x 4 channels per frame (48 bytes)
    for (int sample = 0; sample < ECG_SAMPLES_PER_FRAME; sample++) {
        for (int ch = 0; ch < ECG_NUM_CHANNELS; ch++) {
            // 更新相位
            float phase = ecg_phase[ch];
            ecg_phase[ch] += 0.02f;  // 每个样本相位增加
            if (ecg_phase[ch] > 1.0f) {
                ecg_phase[ch] -= 1.0f;
            }

            // 生成样本
            int32_t value = generate_ecg_sample(ch, phase);

            // 3 字节，大端序
            frame[idx++] = (value >> 16) & 0xFF;
            frame[idx++] = (value >> 8) & 0xFF;
            frame[idx++] = value & 0xFF;
        }
    }

    // CRC8 校验
    frame[idx] = calculate_crc8(frame, ECG_FRAME_SIZE - 1);
}

/**
 * WiFi 事件处理
 */
static void wifi_event_handler(void *arg, esp_event_base_t event_base,
                               int32_t event_id, void *event_data)
{
    if (event_id == WIFI_EVENT_AP_STACONNECTED) {
        ESP_LOGI(TAG, "Station connected");
    } else if (event_id == WIFI_EVENT_AP_STADISCONNECTED) {
        ESP_LOGI(TAG, "Station disconnected");
    }
}

/**
 * 初始化 WiFi SoftAP
 */
static void wifi_init_softap(void)
{
    // 创建默认网络接口 (ESP-IDF v5.x API)
    // 注意：esp_netif_init() 和 esp_event_loop_create_default() 已在 main 中调用
    esp_netif_t *netif = esp_netif_create_default_wifi_ap();
    if (netif == NULL) {
        ESP_LOGE(TAG, "Failed to create WiFi AP netif");
        return;
    }

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_err_t ret = esp_wifi_init(&cfg);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "WiFi init failed: %s", esp_err_to_name(ret));
        return;
    }
    ESP_LOGI(TAG, "WiFi driver initialized");

    ret = esp_event_handler_instance_register(WIFI_EVENT,
                                               ESP_EVENT_ANY_ID,
                                               &wifi_event_handler,
                                               NULL,
                                               NULL);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Event handler register failed: %s", esp_err_to_name(ret));
        return;
    }

    wifi_config_t wifi_config = {
        .ap = {
            .ssid = ECG_SSID,
            .ssid_len = strlen(ECG_SSID),
            .channel = ECG_CHANNEL,
            .password = ECG_PASSWORD,
            .max_connection = 4,
            .authmode = WIFI_AUTH_OPEN,
        },
    };

    // use WPA2 when a password is configured
    if (strlen(ECG_PASSWORD) > 0) {
        wifi_config.ap.authmode = WIFI_AUTH_WPA2_PSK;
    }

    ret = esp_wifi_set_mode(WIFI_MODE_AP);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Set WiFi mode failed: %s", esp_err_to_name(ret));
        return;
    }

    ret = esp_wifi_set_config(WIFI_IF_AP, &wifi_config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Set WiFi config failed: %s", esp_err_to_name(ret));
        return;
    }

    ret = esp_wifi_start();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "WiFi start failed: %s", esp_err_to_name(ret));
        return;
    }

    ESP_LOGI(TAG, "WiFi SoftAP started successfully!");
    ESP_LOGI(TAG, "  SSID: %s", ECG_SSID);
    ESP_LOGI(TAG, "  Channel: %d", ECG_CHANNEL);
    ESP_LOGI(TAG, "  IP: 192.168.4.1");
    ESP_LOGI(TAG, "  TCP Port: %d", ECG_TCP_PORT);
}

/**
 * TCP Server 任务
 */
static void tcp_server_task(void *pvParameters)
{
    char addr_str[128];
    int keepalive = 1;
    int keepidle = 5;
    int keepinterval = 5;
    int keepcount = 3;

    struct sockaddr_in dest_addr;
    dest_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(ECG_TCP_PORT);

    server_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
    if (server_socket < 0) {
        ESP_LOGE(TAG, "Unable to create socket: errno %d", errno);
        vTaskDelete(NULL);
        return;
    }

    int opt = 1;
    setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    int err = bind(server_socket, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    if (err != 0) {
        ESP_LOGE(TAG, "Socket unable to bind: errno %d", errno);
        close(server_socket);
        vTaskDelete(NULL);
        return;
    }

    err = listen(server_socket, 1);
    if (err != 0) {
        ESP_LOGE(TAG, "Error during listen: errno %d", errno);
        close(server_socket);
        vTaskDelete(NULL);
        return;
    }

    ESP_LOGI(TAG, "TCP Server listening on port %d", ECG_TCP_PORT);

    while (1) {
        ESP_LOGI(TAG, "Waiting for client connection...");

        struct sockaddr_in source_addr;
        socklen_t addr_len = sizeof(source_addr);
        client_socket = accept(server_socket, (struct sockaddr *)&source_addr, &addr_len);

        if (client_socket < 0) {
            ESP_LOGE(TAG, "Unable to accept connection: errno %d", errno);
            continue;
        }

        // keepalive
        setsockopt(client_socket, SOL_SOCKET, SO_KEEPALIVE, &keepalive, sizeof(int));
        setsockopt(client_socket, IPPROTO_TCP, TCP_KEEPIDLE, &keepidle, sizeof(int));
        setsockopt(client_socket, IPPROTO_TCP, TCP_KEEPINTVL, &keepinterval, sizeof(int));
        setsockopt(client_socket, IPPROTO_TCP, TCP_KEEPCNT, &keepcount, sizeof(int));

        // format the client address
        inet_ntoa_r(source_addr.sin_addr, addr_str, sizeof(addr_str) - 1);
        ESP_LOGI(TAG, "Client connected: %s", addr_str);

        client_connected = true;

        // 等待客户端断开
        while (client_connected) {
            // check connection state
            char dummy;
            int ret = recv(client_socket, &dummy, 1, MSG_PEEK | MSG_DONTWAIT);
            if (ret == 0 || (ret < 0 && errno != EAGAIN && errno != EWOULDBLOCK)) {
                ESP_LOGI(TAG, "Client disconnected");
                client_connected = false;
                break;
            }
            vTaskDelay(pdMS_TO_TICKS(100));
        }

        // close the client socket
        if (client_socket >= 0) {
            close(client_socket);
            client_socket = -1;
        }
    }
}

/**
 * 发送 ECG 数据任务
 */
static void ecg_sender_task(void *pvParameters)
{
    uint8_t frame[ECG_FRAME_SIZE];
    int frame_interval_ms = 1000 / ECG_FRAME_RATE;

    ESP_LOGI(TAG, "ECG sender started, frame rate: %d FPS", ECG_FRAME_RATE);

    while (1) {
        if (!client_connected || client_socket < 0) {
            vTaskDelay(pdMS_TO_TICKS(100));
            continue;
        }

        // build the frame
        build_ecg_frame(frame);

        // send
        int sent = send(client_socket, frame, ECG_FRAME_SIZE, 0);
        if (sent < 0) {
            ESP_LOGE(TAG, "Send failed: errno %d", errno);
            client_connected = false;
            continue;
        }

        // frame pacing
        vTaskDelay(pdMS_TO_TICKS(frame_interval_ms));
    }
}

/**
 * UART receive task (real-data mode)
 */
static uint8_t uart_buf[TCP_BUF_SIZE];   /* static: a task-local buffer once
 * overflowed the 4KB task stack and corrupted the heap */

static void uart_rx_task(void *pvParameters)
{
    int uart_num = UART_NUM_1;

    // UART configuration
    uart_config_t uart_config = {
        .baud_rate = ECG_UART_BAUD,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_APB,
    };

    ESP_ERROR_CHECK(uart_driver_install(uart_num, TCP_BUF_SIZE * 2, 0, 0, NULL, 0));
    ESP_ERROR_CHECK(uart_param_config(uart_num, &uart_config));
    // Pin mapping verified against the board netlist:
    //   STM32 UART5_TX(PC12) -> ESP32 IO5  (WIFI_RXD2, R337)
    //   STM32 UART5_RX(PD2)  <- ESP32 IO18 (WIFI_TXD2, R338)
    // Backup link: STM32 UART8(PE0/PE1) <-> ESP32 IO19/IO22 (R339/R340)
    ESP_ERROR_CHECK(uart_set_pin(uart_num, 18, 5, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));

    ESP_LOGI(TAG, "UART initialized: %d baud", ECG_UART_BAUD);

    while (1) {
        if (!client_connected || client_socket < 0) {
            vTaskDelay(pdMS_TO_TICKS(100));
            continue;
        }

        // read from UART
        int len = uart_read_bytes(uart_num, uart_buf, TCP_BUF_SIZE, pdMS_TO_TICKS(10));
        if (len > 0) {
            // forward verbatim to TCP
            int sent = send(client_socket, uart_buf, len, 0);
            if (sent < 0) {
                ESP_LOGE(TAG, "UART->TCP send failed");
                client_connected = false;
            }
        }

        // downlink: TCP -> UART (PC commands, e.g. set temp target, forwarded to STM32)
        int rlen = recv(client_socket, uart_buf, TCP_BUF_SIZE, MSG_DONTWAIT);
        if (rlen > 0) {
            uart_write_bytes(uart_num, (const char *)uart_buf, rlen);
        } else if (rlen < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
            ESP_LOGE(TAG, "TCP->UART recv failed: errno %d", errno);
            client_connected = false;
        }
    }
}

/**
 * 主程序入口
 */
void app_main(void)
{
    ESP_LOGI(TAG, "ECG WiFi Bridge starting...");
    ESP_LOGI(TAG, "WiFi SSID: %s", ECG_SSID);
    ESP_LOGI(TAG, "TCP Port: %d", ECG_TCP_PORT);
    ESP_LOGI(TAG, "Data Mode: %d", ECG_DATA_MODE);

    // init NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_LOGW(TAG, "NVS partition need erase, erasing...");
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
    ESP_LOGI(TAG, "NVS initialized");

    // init the TCP/IP stack
    ESP_LOGI(TAG, "Initializing TCP/IP stack...");
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_LOGI(TAG, "TCP/IP stack initialized");

    // create the default event loop
    ESP_LOGI(TAG, "Creating default event loop...");
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    ESP_LOGI(TAG, "Event loop created");

    // init WiFi
    ESP_LOGI(TAG, "Initializing WiFi...");
    wifi_init_softap();
    ESP_LOGI(TAG, "WiFi initialized");

    // start the TCP server task
    xTaskCreate(tcp_server_task, "tcp_server", 4096, NULL, 5, NULL);

    // start the data task selected by the configured mode
    if (ECG_DATA_MODE == 0) {
        // simulated data mode
        ESP_LOGI(TAG, "Running in SIMULATED DATA mode");
        xTaskCreate(ecg_sender_task, "ecg_sender", 4096, NULL, 5, NULL);
    } else {
        // real-data mode (UART)
        ESP_LOGI(TAG, "Running in UART DATA mode");
        xTaskCreate(uart_rx_task, "uart_rx", 6144, NULL, 5, NULL);   /* big buffer moved out of the stack */
    }

    ESP_LOGI(TAG, "ECG WiFi Bridge ready!");
    ESP_LOGI(TAG, "Please connect to WiFi AP: %s", ECG_SSID);
}