/*  WiFi softAP Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_mac.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"

#include "lwip/err.h"
#include "lwip/sys.h"
#include <stdio.h>

#include "esp_system.h"
#include "esp_err.h"
#include <sys/socket.h>
#include "freertos/event_groups.h"

#include "protocol_examples_common.h"

#define EXAMPLE_ESP_WIFI_SSID      "esp32-ap"
#define EXAMPLE_ESP_WIFI_PASS      ""
#define EXAMPLE_ESP_WIFI_CHANNEL   CONFIG_ESP_WIFI_CHANNEL
#define EXAMPLE_MAX_STA_CONN       CONFIG_ESP_MAX_STA_CONN

#define debug 0
#define CONFIG_EXAMPLE_IPV4 1
//static const char *TAG = "wifi softAP";
int32_t ClientCnt = 0;

#include "driver/uart.h"
#include "driver/gpio.h"
#include "lwip/err.h"
#include "lwip/sockets.h"
#include "lwip/sys.h"
#include <lwip/netdb.h>


#define KEEPALIVE_IDLE              5
#define KEEPALIVE_INTERVAL          5
#define KEEPALIVE_COUNT             3

static const char *TAG = "example";

#define ECHO_TEST_TXD (GPIO_NUM_1)
#define ECHO_TEST_RXD (GPIO_NUM_3)
#define ECHO_TEST_RTS (UART_PIN_NO_CHANGE)
#define ECHO_TEST_CTS (UART_PIN_NO_CHANGE)

#define ECHO_UART_PORT_NUM      (0)
#define ECHO_UART_BAUD_RATE     (115200)
#define ECHO_TASK_STACK_SIZE    (1024)

int len_UART;
int target_sock;
#define BUF_SIZE (1024)
char send_buffer[128];


static void echo_task(void *arg)
{
    /* Configure parameters of an UART driver,
     * communication pins and install the driver */
    uart_config_t uart_config = {
        .baud_rate = ECHO_UART_BAUD_RATE,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };
    int intr_alloc_flags = 0;

#if CONFIG_UART_ISR_IN_IRAM
    intr_alloc_flags = ESP_INTR_FLAG_IRAM;
#endif

    ESP_ERROR_CHECK(uart_driver_install(ECHO_UART_PORT_NUM, BUF_SIZE * 2, 0, 0, NULL, intr_alloc_flags));
    ESP_ERROR_CHECK(uart_param_config(ECHO_UART_PORT_NUM, &uart_config));
    ESP_ERROR_CHECK(uart_set_pin(ECHO_UART_PORT_NUM, ECHO_TEST_TXD, ECHO_TEST_RXD, ECHO_TEST_RTS, ECHO_TEST_CTS));

    // Configure a temporary buffer for the incoming data
    uint8_t *data = (uint8_t *) malloc(BUF_SIZE);

    while (1) {
        // Read data from the UART
    	len_UART = uart_read_bytes(ECHO_UART_PORT_NUM, data, (BUF_SIZE - 1), 20 / portTICK_PERIOD_MS);
        // Write data back to the UART
        uart_write_bytes(ECHO_UART_PORT_NUM, (const char *) data, len_UART);
        if (len_UART) {
            data[len_UART] = '\0';
#if debug
            ESP_LOGI(TAG, "Recv str: %s", (char *) data);
#endif

        }
    }
}








static void do_retransmit(const int sock)
{
    int len;
    char rx_buffer[128];

//    do {
//        len = recv(sock, rx_buffer, sizeof(rx_buffer) - 1, 0);
//        if (len < 0) {
//            ESP_LOGE(TAG, "Error occurred during receiving: errno %d", errno);
//        } else if (len == 0) {
//            ESP_LOGW(TAG, "Connection closed");
//        } else {
//            rx_buffer[len] = 0; // Null-terminate whatever is received and treat it like a string
//            ESP_LOGI(TAG, "Received %d bytes: %s", len, rx_buffer);
//
//            // send() can return less bytes than supplied length.
//            // Walk-around for robust implementation.
//            int to_write = len;
//            while (to_write > 0) {
//                int written = send(sock, rx_buffer + (len - to_write), to_write, 0);
//                if (written < 0) {
//                    ESP_LOGE(TAG, "Error occurred during sending: errno %d", errno);
//                    // Failed to retransmit, giving up
//                    return;
//                }
//                to_write -= written;
//            }
//        }
//    } while (len > 0);



        len = recv(sock, rx_buffer, sizeof(rx_buffer) - 1, 0);
        if (len < 0) {
#if debug
            ESP_LOGE(TAG, "Error occurred during receiving: errno %d", errno);
#endif

        } else if (len == 0) {
#if debug
            ESP_LOGW(TAG, "Connection closed");
#endif


        } else {
            rx_buffer[len] = 0; // Null-terminate whatever is received and treat it like a string
            ESP_LOGI(TAG, "Received %d bytes: %s", len, rx_buffer);
            send(sock, rx_buffer, strlen(rx_buffer), 0);

            // send() can return less bytes than supplied length.
            // Walk-around for robust implementation.
            int to_write = len;
            while (to_write > 0) {
                int written = send(sock, rx_buffer + (len - to_write), to_write, 0);
                if (written < 0) {
#if debug
            ESP_LOGE(TAG, "Error occurred during sending: errno %d", errno);
#endif

                    // Failed to retransmit, giving up
                    return;
                }
                to_write -= written;
            }
        }

}


static void wifi_event_handler(void* arg, esp_event_base_t event_base,
                                    int32_t event_id, void* event_data)
{
    if (event_id == WIFI_EVENT_AP_STACONNECTED) {
        wifi_event_ap_staconnected_t* event = (wifi_event_ap_staconnected_t*) event_data;
#if debug
          ESP_LOGI(TAG, "station "MACSTR" join, AID=%d",
        	MAC2STR(event->mac), event->aid);
#endif

    } else if (event_id == WIFI_EVENT_AP_STADISCONNECTED) {
        wifi_event_ap_stadisconnected_t* event = (wifi_event_ap_stadisconnected_t*) event_data;

#if debug
           ESP_LOGI(TAG, "station "MACSTR" leave, AID=%d",
        		 MAC2STR(event->mac), event->aid);
#endif

    }
}

void wifi_init_softap(void)
{

    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_ap();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT,
                                                        ESP_EVENT_ANY_ID,
                                                        &wifi_event_handler,
                                                        NULL,
                                                        NULL));

    wifi_config_t wifi_config = {
        .ap = {
            .ssid = EXAMPLE_ESP_WIFI_SSID,
            .ssid_len = strlen(EXAMPLE_ESP_WIFI_SSID),
            .channel = EXAMPLE_ESP_WIFI_CHANNEL,
            .password = EXAMPLE_ESP_WIFI_PASS,
            .max_connection = EXAMPLE_MAX_STA_CONN,
#ifdef CONFIG_ESP_WIFI_SOFTAP_SAE_SUPPORT
            .authmode = WIFI_AUTH_WPA3_PSK,
            .sae_pwe_h2e = WPA3_SAE_PWE_BOTH,
#else /* CONFIG_ESP_WIFI_SOFTAP_SAE_SUPPORT */
            .authmode = WIFI_AUTH_OPEN,
#endif
            .pmf_cfg = {
                    .required = true,
            },
        },
    };
    if (strlen(EXAMPLE_ESP_WIFI_PASS) == 0) {
        wifi_config.ap.authmode = WIFI_AUTH_OPEN;
    }

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

#if debug
    ESP_LOGI(TAG, "wifi_init_softap finished. SSID:%s password:%s channel:%d",
             EXAMPLE_ESP_WIFI_SSID, EXAMPLE_ESP_WIFI_PASS, EXAMPLE_ESP_WIFI_CHANNEL);
#endif

}



#define PORT 12345
#define TCP_SERVER_ADRESS "192.168.4.1"
int connect_socket;

// 建立tcp client
//esp_err_t create_tcp_client()
//{
//    ESP_LOGI(TAG, "will connect gateway ssid : %s port:%d",TCP_SERVER_ADRESS, PORT);
//    //新建socket
//    connect_socket = socket(AF_INET, SOCK_STREAM, 0);
//    if (connect_socket < 0){
//    	ESP_LOGI(TAG, "socket create fail ");
////        show_socket_error_reason("create client", connect_socket);//打印报错信息
//        close(connect_socket);//新建失败后，关闭新建的socket，等待下次新建
//        return ESP_FAIL;
//    }
//    //配置连接服务器信息
//    struct sockaddr_in server_addr;
//    server_addr.sin_family = AF_INET;
//    server_addr.sin_port = htons(PORT);
//    server_addr.sin_addr.s_addr = inet_addr(TCP_SERVER_ADRESS);
//    ESP_LOGI(TAG, "Connecting server...");
//    //连接服务器
//    if (connect(connect_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0){
////        show_socket_error_reason("client connect", connect_socket);//打印报错信息
//        ESP_LOGE(TAG, "connect failed!");
//        //连接失败后，关闭之前新建的socket，等待下次新建
//        close(connect_socket);
//        return ESP_FAIL;
//    }
//    ESP_LOGI(TAG, "connect success!");
//    return ESP_OK;
//}







bool g_rxtx_need_restart;


char temp_tmp117;

// 接收数据任务
void recv_data(void *pvParameters)
{
    int len = 0;            //长度
    char databuff[1024];    //缓存
    while (1){
        //清空缓存
        memset(databuff, 0x00, sizeof(databuff));
        //读取接收数据
        len = recv(connect_socket, databuff, sizeof(databuff), 0);
        g_rxtx_need_restart = false;
        if (len > 0){
#if debug
            ESP_LOGI(TAG, "recvData: %s", databuff);//打印接收到的数组
#endif
            //接收数据回发
            send(connect_socket, databuff, strlen(databuff), 0);
            //清空缓存
            memset(databuff, 0x00, sizeof(databuff));
            //放入传感器数据
//            databuff[0]=temp_tmp117;
//            send(connect_socket, databuff, strlen(databuff), 0);
            //sendto(connect_socket, databuff , sizeof(databuff), 0, (struct sockaddr *) &remote_addr,sizeof(remote_addr));
        }else{
//            show_socket_error_reason("recv_data", connect_socket);//打印错误信息
            g_rxtx_need_restart = true;//服务器故障，标记重连
            break;
        }
    }
    close(connect_socket);
    g_rxtx_need_restart = true;//标记重连
    vTaskDelete(NULL);
}





void tcp_send_task(void * pvParameters)
{

    send_buffer[0]=0x5A;
    send(target_sock, send_buffer, strlen(send_buffer), 0);
//    shutdown(target_sock, 0);
//    close(target_sock);

    TickType_t xTicksToWait = portMAX_DELAY;

    for(;;)
    {
        if (ClientCnt > 0)
        {
            ulTaskNotifyTake(pdTRUE, xTicksToWait);
        } else {
        #if debug
            ESP_LOGI(TAG, "Send wait connect");
        #endif
            ulTaskNotifyTake(pdTRUE, xTicksToWait);
        }
    }
    close(target_sock);
    vTaskDelete(NULL);
}


//// 任务：建立TCP连接并从TCP接收数据
//static void tcp_connect(void *pvParameters)
//{
//    while (1){
//        g_rxtx_need_restart = false;
// //       //等待WIFI连接信号量，死等
//       xEventGroupWaitBits(tcp_event_group, WIFI_CONNECTED_BIT, false, true, portMAX_DELAY);
//        ESP_LOGI(TAG, "start tcp connected");
//        TaskHandle_t tx_rx_task = NULL;
//        //延时3S准备建立clien
////        vTaskDelay(3000 / portTICK_RATE_MS);
////        ESP_LOGI(TAG, "create tcp Client");
//        ESP_LOGI(TAG, "create tcp Server");
//        //建立client
//        int socket_ret = create_tcp_Server();
//        if (socket_ret == ESP_FAIL){
//            ESP_LOGI(TAG, "create tcp socket error,stop...");
//            continue;
//        }else{
//            ESP_LOGI(TAG, "create tcp socket succeed...");
//            //建立tcp接收数据任务
//            if (pdPASS != xTaskCreate(&recv_data, "recv_data", 4096, NULL, 4, &tx_rx_task)){
//                ESP_LOGI(TAG, "Recv task create fail!");
//            }else{
//                ESP_LOGI(TAG, "Recv task create succeed!");
//            }
//        }
//        while (1){
////            vTaskDelay(3000 / portTICK_RATE_MS);
//            //重新建立client，流程和上面一样
//            if (g_rxtx_need_restart){
////                vTaskDelay(3000 / portTICK_RATE_MS);
//                ESP_LOGI(TAG, "reStart create tcp client...");
//                //建立client
//                int socket_ret = create_tcp_Server();
//                if (socket_ret == ESP_FAIL){
//                    ESP_LOGE(TAG, "reStart create tcp socket error,stop...");
//                    continue;
//                }else{
//                    ESP_LOGI(TAG, "reStart create tcp socket succeed...");
//                    //重新建立完成，清除标记
//                    g_rxtx_need_restart = false;
//                    //建立tcp接收数据任务
//                    if (pdPASS != xTaskCreate(&recv_data, "recv_data", 4096, NULL, 4, &tx_rx_task)){
//                        ESP_LOGE(TAG, "reStart Recv task create fail!");
//                    }else{
//                        ESP_LOGI(TAG, "reStart Recv task create succeed!");
//                    }
//                }
//            }
//        }
//    }
//    vTaskDelete(NULL);
//}


static void tcp_server_task(void *pvParameters)
{
    char addr_str[128];
    int addr_family = (int)pvParameters;
    int ip_protocol = 0;
    int keepAlive = 1;
    int keepIdle = KEEPALIVE_IDLE;
    int keepInterval = KEEPALIVE_INTERVAL;
    int keepCount = KEEPALIVE_COUNT;
    struct sockaddr_storage dest_addr;

#ifdef CONFIG_EXAMPLE_IPV4
    if (addr_family == AF_INET) {
        struct sockaddr_in *dest_addr_ip4 = (struct sockaddr_in *)&dest_addr;
        dest_addr_ip4->sin_addr.s_addr = htonl(INADDR_ANY);
        dest_addr_ip4->sin_family = AF_INET;
        dest_addr_ip4->sin_port = htons(PORT);
        ip_protocol = IPPROTO_IP;
    }
#endif
#ifdef CONFIG_EXAMPLE_IPV6
    if (addr_family == AF_INET6) {
        struct sockaddr_in6 *dest_addr_ip6 = (struct sockaddr_in6 *)&dest_addr;
        bzero(&dest_addr_ip6->sin6_addr.un, sizeof(dest_addr_ip6->sin6_addr.un));
        dest_addr_ip6->sin6_family = AF_INET6;
        dest_addr_ip6->sin6_port = htons(PORT);
        ip_protocol = IPPROTO_IPV6;
    }
#endif

    int listen_sock = socket(addr_family, SOCK_STREAM, ip_protocol);
    if (listen_sock < 0) {
#if debug
     ESP_LOGE(TAG, "Unable to create socket: errno %d", errno);
#endif
        vTaskDelete(NULL);
        return;
    }
    int opt = 1;
    setsockopt(listen_sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#if defined(CONFIG_EXAMPLE_IPV4) && defined(CONFIG_EXAMPLE_IPV6)
    // Note that by default IPV6 binds to both protocols, it is must be disabled
    // if both protocols used at the same time (used in CI)
    setsockopt(listen_sock, IPPROTO_IPV6, IPV6_V6ONLY, &opt, sizeof(opt));
#endif

#if debug
    ESP_LOGI(TAG, "Socket created");
#endif

    int err = bind(listen_sock, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    if (err != 0) {
#if debug
        ESP_LOGE(TAG, "Socket unable to bind: errno %d", errno);
        ESP_LOGE(TAG, "IPPROTO: %d", addr_family);
#endif

        goto CLEAN_UP;
    }

#if debug
      ESP_LOGI(TAG, "Socket bound, port %d", PORT);
#endif


    err = listen(listen_sock, 1);
    if (err != 0) {
#if debug
        ESP_LOGE(TAG, "Error occurred during listen: errno %d", errno);
#endif
        goto CLEAN_UP;
    }

    while (1) {

#if debug
        ESP_LOGI(TAG, "Socket listening");
#endif


        struct sockaddr_storage source_addr; // Large enough for both IPv4 or IPv6
        socklen_t addr_len = sizeof(source_addr);
        target_sock = accept(listen_sock, (struct sockaddr *)&source_addr, &addr_len);
        if (target_sock < 0) {
#if debug
            ESP_LOGE(TAG, "Unable to accept connection: errno %d", errno);
#endif
            ClientCnt=0;
            break;
        }
        xTaskCreate(tcp_send_task, "tcp_server_send", 4096, (void*)AF_INET, 5, NULL);
//        target_sock=sock;
//        send_buffer[0]=0x5A;
//        while(1)
//        {
//        send(target_sock, send_buffer, strlen(send_buffer), 0);
//        }
        ClientCnt=1;
        close(listen_sock);

        // Set tcp keepalive option
        setsockopt(target_sock, SOL_SOCKET, SO_KEEPALIVE, &keepAlive, sizeof(int));
        setsockopt(target_sock, IPPROTO_TCP, TCP_KEEPIDLE, &keepIdle, sizeof(int));
        setsockopt(target_sock, IPPROTO_TCP, TCP_KEEPINTVL, &keepInterval, sizeof(int));
        setsockopt(target_sock, IPPROTO_TCP, TCP_KEEPCNT, &keepCount, sizeof(int));
        // Convert ip address to string
#ifdef CONFIG_EXAMPLE_IPV4
        if (source_addr.ss_family == PF_INET) {
            inet_ntoa_r(((struct sockaddr_in *)&source_addr)->sin_addr, addr_str, sizeof(addr_str) - 1);
        }
#endif
#ifdef CONFIG_EXAMPLE_IPV6
        if (source_addr.ss_family == PF_INET6) {
            inet6_ntoa_r(((struct sockaddr_in6 *)&source_addr)->sin6_addr, addr_str, sizeof(addr_str) - 1);
        }
#endif
#if debug
        ESP_LOGI(TAG, "Socket accepted ip address: %s", addr_str);
#endif
//        do_retransmit(target_sock);

//        shutdown(target_sock, 0);
//        close(target_sock);


//        ClientCnt=0;
//        ESP_LOGI(TAG, "ClientCnt=0");

    }

CLEAN_UP:
    close(listen_sock);
    vTaskDelete(NULL);
}


void app_main(void)
{
    //Initialize NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
      ESP_ERROR_CHECK(nvs_flash_erase());
      ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
//    ESP_ERROR_CHECK(esp_netif_init());
//    ESP_ERROR_CHECK(i2c_master_init());
//    xTaskCreate(i2c_test_task, "i2c_test_task_0", 1024 * 2, (void *)0, 10, NULL);
#if debug
      ESP_LOGI(TAG, "ESP_WIFI_MODE_AP");
#endif
    wifi_init_softap();

//    ESP_ERROR_CHECK(example_connect());
//    xTaskCreate(echo_task, "uart_echo_task", ECHO_TASK_STACK_SIZE, NULL, 5, NULL);

#ifdef CONFIG_EXAMPLE_IPV4
    xTaskCreate(tcp_server_task, "tcp_server", 4096, (void*)AF_INET, 5, NULL);
#endif
#ifdef CONFIG_EXAMPLE_IPV6
    xTaskCreate(tcp_server_task, "tcp_server", 4096, (void*)AF_INET6, 5, NULL);
#endif


}

