# PHYSIO FOR RODENT - Rodent Physiological Signal Monitoring System

[![中文](https://img.shields.io/badge/中文-简体-blue)](README_CN.md) [![English](https://img.shields.io/badge/English-EN-green)](README_EN.md)

A multi-parameter physiological signal monitoring system designed for rodents (rats/mice), supporting ECG, respiration, SPO2, temperature, and blood pressure measurements.

---

## 📊 System Block Diagram

```
                    ┌─────────────────────────────────────────────────────────────────────────┐
                    │                 Physiological Signal Monitoring System (PHYSIO)          │
                    │                       STM32F429ZGT6 Main Controller                      │
                    └─────────────────────────────────────────────────────────────────────────┘
                                            ▲                    ▲
                                            │ UART               │ WiFi (ESP32)
                    ┌─────────────────────────────────────────────────────────────────────────┐
                    │  ┌─────────────┐    ┌───────────────────────────────────┐    ┌─────────┐│
   Physiological ──│  │ ADS1298R    │    │          STM32F429ZGT6            │    │ ESP32   ││───► WiFi
   Signals         │  │ ECG+Resp    │SPI │                                   │UART│ WiFi    ││    Transfer
   (ECG/Resp)      │  │ AFE Chip    │────│  • SPI Interface (ADS1298R/MAX31856)│────│ Module  ││
                    │  └─────────────┘    │  • I2C Interface (TMP117/AFE4490) │    └─────────┘│
                    │                     │  • DAC Output (PID Temp Control)  │               │
   Oximetry ───────│  ┌─────────────┐    │  • UART Data Transmission         │               │
   (SPO2)          │  │ AFE4490     │I2C │                                   │               │
                    │  │ SPO2 AFE    │────│  ┌───────────────────────────┐    │               │
                    │  └─────────────┘    │  │    PID Temperature Control │    │               │
                    │                     │  │    ECG/Resp Signal Process  │    │               │
   Temperature ────│  ┌─────────────┐    │  │    SPO2 Calculation         │    │               │
   (Body Temp)     │  │ TMP117      │I2C │  │    Data Packaging/Transfer  │    │               │
                    │  │ Temp Sensor │────│  └───────────────────────────┘    │               │
                    │  └─────────────┘    │                                   │               │
                    │                     │  ┌─────────┐    ┌─────────────┐   │               │
   Thermocouple ───│  ┌─────────────┐    │  │ DAC     │    │ PWM Output  │   │               │
   (Animal Temp)   │  │ MAX31856    │SPI │  │ Temp Ctrl│    │ Clock Signal│   │               │
                    │  │ TC Interface│────│  └─────────┘    └─────────────┘   │               │
                    │  └─────────────┘    │                                   │               │
                    │                     └───────────────────────────────────┘               │
                    │  ┌─────────────┐                                                        │
   Heater ─────────│  │ PNP Heater  │──────────────────────────────────────────────────────│───► Maintain
   (Temp Maintain) │  │ PCB Heater  │                                                        │    Body Temp
                    │  └─────────────┘                                                        │
                    └─────────────────────────────────────────────────────────────────────────┘
                                            │ UART/USB
                                            ▼
                    ┌─────────────────────────────────────────────────────────────────────────┐
                    │                      Python Console Software                             │
                    │  ┌─────────────────────────────────────────────────────────────────────┐│
                    │  │  • 4-Channel ECG Waveform Display  • Real-time FFT Spectrum Analysis ││
                    │  │  • Respiration Waveform Display     • Heart Rate/Resp Rate Calculation││
                    │  │  • Temperature Monitoring           • PID Temperature Control          ││
                    │  │  • Data Save (CSV)                  • WiFi/Serial Dual-mode Comm       ││
                    │  └─────────────────────────────────────────────────────────────────────┘│
                    └─────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
ECG-physio/
├── 1.HW/                           # Hardware Design Files
│   ├── PHYSIO_PCB.jpg              # Main Board PCB Design
│   ├── PNP_HEATER_PCB.jpg          # Heater PCB Design
│   ├── SCH_Physio_*.pdf            # Schematic PDF
│   └── Netlist_Physio_*.tel        # Netlist File
├── 2.MATLAB/                       # MATLAB Algorithm Verification
│   ├── ECG.m                       # ECG Signal Processing Script
│   └── pan1985.pdf                 # Pan-Tompkins Algorithm Reference
├── 3.FIRMWARE/                     # Firmware Code
│   ├── 1.ST MCU/                   # STM32F429 Firmware
│   │   └── Physio/                 # STM32CubeIDE Project
│   │       ├── Core/               # Core Code
│   │       │   ├── Inc/            # Header Files
│   │       │   └── Src/            # Source Files
│   │       │       ├── ADS1294.c   # ADS1298R Driver
│   │       │       ├── PID.c       # PID Temperature Control
│   │       │       ├── MAX31856drv.c # Thermocouple Driver
│   │       │       └── main.c      # Main Program
│   │       └ Drivers/              # STM32 HAL Library
│   └── 2.ESP32/                    # ESP32 WiFi Module Firmware
├── 4.Python console/               # Python Console Software
│   ├── V1/                         # Version 1 (Basic)
│   │   ├── main.py                 # Main Program
│   │   └── phsio.py                # Signal Processing
│   └── V2/                         # Version 2 (Enhanced)
│       ├── main.py                 # Main Entry Point
│       ├── ui/                     # UI Components
│       ├── comms/                  # Communication Module (Serial/WiFi)
│       ├── signal_processing/      # Signal Processing Algorithms
│       ├── data/                   # Data Processing
│       └ utils/                    # Utility Functions
└── README.md                       # Project Documentation
```

---

## 🔧 Hardware Requirements

| Component | Model | Description |
|-----------|-------|-------------|
| Main MCU | STM32F429ZGT6 | 180MHz, 1MB Flash, 256KB RAM |
| ECG+Resp Chip | ADS1298R | 8-channel 24-bit ADC, built-in respiration measurement |
| SPO2 Chip | AFE4490 | Pulse oximetry frontend |
| Temperature Sensor | TMP117 | High-precision digital temperature sensor |
| Thermocouple Interface | MAX31856 | Thermocouple digital converter |
| WiFi Module | ESP32 | WiFi data transmission |
| Heater | PNP Heater PCB | Maintain animal body temperature |

---

## 📋 Features

### Hardware Features
- **ECG Acquisition** - 4-channel ECG signal acquisition, 24-bit precision
- **Respiration Monitoring** - Impedance-based respiration waveform measurement
- **SPO2 Measurement** - Pulse oxygen saturation monitoring
- **Temperature Monitoring** - Body and environmental temperature measurement
- **PID Temperature Control** - Automatic heating to maintain animal body temperature
- **Blood Pressure Measurement** - Invasive blood pressure signal acquisition (in development)
- **Data Transmission** - WiFi and serial dual-mode output

### Software Features (Python Console)
- **Real-time Waveform Display** - 4-channel ECG + respiration waveforms
- **FFT Spectrum Analysis** - 0-250Hz real-time spectrum
- **Heart Rate Detection** - Pan-Tompkins R-wave detection algorithm
- **Respiration Rate Detection** - Impedance respiration waveform analysis
- **Digital Filtering** - 50Hz notch filter, bandpass filter
- **Data Saving** - CSV format export
- **WiFi Support** - Remote data transmission

---

## 🚀 Quick Start

### Hardware Setup
1. Assemble PHYSIO PCB main board
2. Connect ADS1298R ECG acquisition module
3. Connect TMP117/MAX31856 temperature sensors
4. Connect heater board (for body temperature maintenance)
5. Connect ESP32 WiFi module (optional)

### Firmware Compilation
1. Open `3.FIRMWARE/1.ST MCU/Physio` with STM32CubeIDE
2. Compile and download to STM32F429
3. ESP32 firmware compiled with Arduino IDE

### Python Console
```bash
cd "4.Python console/V2"
pip install -r requirements.txt
python main.py
```

---

## 📄 Documentation

| Document | Description |
|----------|-------------|
| [Hardware Design](1.HW/README.md) | PCB and schematic documentation |
| [MATLAB Algorithm](2.MATLAB/README.md) | ECG processing algorithm verification |
| [Python Console](4.Python%20console/V2/README.md) | Software usage guide |
| [WiFi Test](4.Python%20console/V2/tests/README_WIFI_TEST.md) | WiFi functionality test |

---

## 🛠️ Tool Versions

- STM32CubeIDE 1.x
- STM32 HAL Library
- Python 3.8+
- PyQt5 5.15+
- Arduino IDE (ESP32)

---

## 📅 Project Dates

- Initial Release: 2023-10-21
- Updated Version: 2025-09-23

---

## 📧 Contact

For issues, please submit an Issue or contact the project maintainer.

---

## Hardware Prototype

![PHYSIO_PCB](https://github.com/user-attachments/assets/7622d6b0-4796-47c3-825c-8e8744fa1f35)

## Python Console

![python console](https://github.com/user-attachments/assets/d1b41586-4a6b-4fd0-b74a-d3e5fb1b1cc0)

<img width="1400" height="930" alt="image" src="https://github.com/user-attachments/assets/2ca9f4a7-1213-45cd-bbab-9d5b22ac40f3" />