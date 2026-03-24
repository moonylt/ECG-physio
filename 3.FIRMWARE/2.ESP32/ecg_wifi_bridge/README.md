# ECG WiFi Bridge

WiFi 数据桥接固件，用于将 ECG 数据通过 WiFi 传输到上位机。

## 功能

- SoftAP 模式：创建热点 `ECG-Physio`
- TCP Server：端口 12345
- 模拟数据模式：发送模拟 ECG 波形用于测试
- UART 透传模式：从 STM32 接收真实 ECG 数据

## 编译

```bash
cd ecg_wifi_bridge
idf.py build
```

## 烧录

```bash
idf.py -p COMx flash
```

## 使用

1. ESP32 启动后创建热点 `ECG-Physio`（无密码）
2. 电脑连接热点后，IP 为 192.168.4.2
3. 运行上位机，选择 WiFi 模式连接 192.168.4.1:12345
4. 开始接收 ECG 数据

## 配置

运行 `idf.py menuconfig` 可配置：
- ECG_WIFI_BRIDGE 配置菜单
- SSID、密码、通道
- TCP 端口
- 数据模式（模拟/真实）