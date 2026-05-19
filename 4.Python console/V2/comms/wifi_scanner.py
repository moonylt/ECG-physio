# -*- coding: utf-8 -*-
"""
WiFi AP Scanner
Cross-platform WiFi network scanning for ECG-Physio device discovery
"""

import subprocess
import re
import platform
from dataclasses import dataclass
from typing import List, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QThread


@dataclass
class WiFiAPInfo:
    """WiFi AP information"""
    ssid: str
    bssid: str          # MAC address
    signal: int         # Signal strength (0-100)
    channel: int        # WiFi channel
    security: str       # Security type (Open/WPA2/etc)

    def __str__(self) -> str:
        return f"{self.ssid} ({self.signal}%)"


class WiFiScanner:
    """
    WiFi AP Scanner

    Scans nearby WiFi networks and filters for ECG-Physio devices.
    Uses system commands for cross-platform support.
    """

    # Target SSID prefix for ECG devices
    TARGET_SSID_PREFIX = "ECG-Physio"

    def __init__(self):
        self._system = platform.system()

    def scan(self) -> List[WiFiAPInfo]:
        """
        Scan all nearby WiFi APs

        Returns:
            List of WiFiAPInfo objects
        """
        if self._system == "Windows":
            return self._scan_windows()
        elif self._system == "Darwin":
            return self._scan_macos()
        elif self._system == "Linux":
            return self._scan_linux()
        else:
            return []

    def scan_ecg_devices(self) -> List[WiFiAPInfo]:
        """
        Scan and filter ECG-Physio devices

        Returns:
            List of WiFiAPInfo objects matching ECG-Physio SSID
        """
        all_aps = self.scan()
        return [
            ap for ap in all_aps
            if ap.ssid and ap.ssid.startswith(self.TARGET_SSID_PREFIX)
        ]

    def get_current_connection(self) -> dict:
        """
        Get current WiFi connection status

        Returns:
            dict with 'ssid', 'bssid', 'connected' keys
        """
        if self._system == "Windows":
            return self._get_current_connection_windows()
        elif self._system == "Darwin":
            return self._get_current_connection_macos()
        elif self._system == "Linux":
            return self._get_current_connection_linux()
        else:
            return {'ssid': '', 'connected': False}

    # ==================== Windows Implementation ====================

    def _scan_windows(self) -> List[WiFiAPInfo]:
        """Scan WiFi APs on Windows using netsh command"""
        try:
            # Run netsh wlan show networks mode=bssid
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
                capture_output=True,
                text=True,
                encoding='gbk',  # Windows Chinese encoding
                timeout=10
            )
            return self._parse_netsh_output(result.stdout)
        except subprocess.TimeoutExpired:
            return []
        except Exception as e:
            print(f"WiFi scan error: {e}")
            return []

    def _parse_netsh_output(self, output: str) -> List[WiFiAPInfo]:
        """
        Parse netsh wlan show networks output

        Output format example:
        SSID 1 : ECG-Physio
            Network type             : Infrastructure
            Authentication           : Open
            Encryption               : WEP
            BSSID 1                  : aa:bb:cc:dd:ee:ff
                Signal               : 85%
                Radio type           : 802.11g
                Channel              : 6
        """
        aps = []
        current_ssid = None
        current_security = "Open"
        current_bssid = None
        current_signal = 0
        current_channel = 0

        lines = output.split('\n')

        for line in lines:
            line = line.strip()

            # SSID line
            ssid_match = re.match(r'SSID \d+ : (.+)', line)
            if ssid_match:
                # Save previous AP if exists
                if current_ssid and current_bssid:
                    aps.append(WiFiAPInfo(
                        ssid=current_ssid,
                        bssid=current_bssid,
                        signal=current_signal,
                        channel=current_channel,
                        security=current_security
                    ))
                current_ssid = ssid_match.group(1).strip()
                current_bssid = None
                continue

            # Authentication line
            auth_match = re.match(r'Authentication\s*:\s*(.+)', line)
            if auth_match:
                current_security = auth_match.group(1).strip()
                continue

            # BSSID line
            bssid_match = re.match(r'BSSID \d+\s*:\s*([0-9a-fA-F:]+)', line)
            if bssid_match:
                current_bssid = bssid_match.group(1).strip()
                continue

            # Signal line
            signal_match = re.match(r'Signal\s*:\s*(\d+)%', line)
            if signal_match:
                current_signal = int(signal_match.group(1))
                continue

            # Channel line
            channel_match = re.match(r'Channel\s*:\s*(\d+)', line)
            if channel_match:
                current_channel = int(channel_match.group(1))
                continue

        # Save last AP
        if current_ssid and current_bssid:
            aps.append(WiFiAPInfo(
                ssid=current_ssid,
                bssid=current_bssid,
                signal=current_signal,
                channel=current_channel,
                security=current_security
            ))

        return aps

    def _get_current_connection_windows(self) -> dict:
        """Get current WiFi connection on Windows"""
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'interfaces'],
                capture_output=True,
                text=True,
                encoding='gbk',
                timeout=5
            )
            return self._parse_interface_output(result.stdout)
        except Exception:
            return {'ssid': '', 'connected': False}

    def _parse_interface_output(self, output: str) -> dict:
        """Parse netsh wlan show interfaces output"""
        ssid = ''
        bssid = ''
        connected = False

        for line in output.split('\n'):
            line = line.strip()

            # SSID line
            ssid_match = re.match(r'SSID\s*:\s*(.+)', line)
            if ssid_match and ssid_match.group(1).strip() != '':
                ssid = ssid_match.group(1).strip()
                connected = True

            # BSSID line
            bssid_match = re.match(r'BSSID\s*:\s*([0-9a-fA-F:]+)', line)
            if bssid_match:
                bssid = bssid_match.group(1).strip()

        return {
            'ssid': ssid,
            'bssid': bssid,
            'connected': connected and ssid != ''
        }

    # ==================== macOS Implementation ====================

    def _scan_macos(self) -> List[WiFiAPInfo]:
        """Scan WiFi APs on macOS"""
        try:
            # Use airport command
            result = subprocess.run(
                ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-s'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return self._parse_airport_output(result.stdout)
        except Exception:
            return []

    def _parse_airport_output(self, output: str) -> List[WiFiAPInfo]:
        """Parse airport -s output"""
        aps = []
        lines = output.split('\n')

        # Skip header line
        for line in lines[1:]:
            if not line.strip():
                continue

            # Airport output format: SSID BSSID RSSI CHANNEL HT CC SECURITY
            parts = line.strip().split()
            if len(parts) >= 5:
                ssid = parts[0]
                bssid = parts[1]
                rssi = int(parts[2])
                channel = int(parts[3])
                security = parts[-1] if len(parts) >= 7 else "Open"

                # Convert RSSI to percentage (approximate)
                # RSSI range: -100 (weak) to 0 (strong)
                signal = max(0, min(100, (rssi + 100)))

                aps.append(WiFiAPInfo(
                    ssid=ssid,
                    bssid=bssid,
                    signal=signal,
                    channel=channel,
                    security=security
                ))

        return aps

    def _get_current_connection_macos(self) -> dict:
        """Get current WiFi connection on macOS"""
        try:
            result = subprocess.run(
                ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I'],
                capture_output=True,
                text=True,
                timeout=5
            )
            ssid = ''
            bssid = ''

            for line in result.stdout.split('\n'):
                if 'SSID:' in line:
                    ssid = line.split('SSID:')[1].strip()
                if 'BSSID:' in line:
                    bssid = line.split('BSSID:')[1].strip()

            return {
                'ssid': ssid,
                'bssid': bssid,
                'connected': ssid != ''
            }
        except Exception:
            return {'ssid': '', 'connected': False}

    # ==================== Linux Implementation ====================

    def _scan_linux(self) -> List[WiFiAPInfo]:
        """Scan WiFi APs on Linux using nmcli"""
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'SSID,BSSID,SIGNAL,CHAN,SECURITY', 'dev', 'wifi', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return self._parse_nmcli_output(result.stdout)
        except Exception:
            return []

    def _parse_nmcli_output(self, output: str) -> List[WiFiAPInfo]:
        """Parse nmcli output"""
        aps = []

        for line in output.split('\n'):
            if not line.strip():
                continue

            # nmcli -t output: SSID:BSSID:SIGNAL:CHAN:SECURITY
            parts = line.split(':')
            if len(parts) >= 5:
                ssid = parts[0] if parts[0] != '' else '<hidden>'
                bssid = parts[1]
                signal = int(parts[2])
                channel = int(parts[3]) if parts[3] else 0
                security = parts[4] if parts[4] else 'Open'

                aps.append(WiFiAPInfo(
                    ssid=ssid,
                    bssid=bssid,
                    signal=signal,
                    channel=channel,
                    security=security
                ))

        return aps

    def _get_current_connection_linux(self) -> dict:
        """Get current WiFi connection on Linux"""
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'ACTIVE,SSID,BSSID', 'dev', 'wifi', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )

            for line in result.stdout.split('\n'):
                parts = line.split(':')
                if len(parts) >= 3 and parts[0] == 'yes':
                    return {
                        'ssid': parts[1],
                        'bssid': parts[2],
                        'connected': True
                    }

            return {'ssid': '', 'connected': False}
        except Exception:
            return {'ssid': '', 'connected': False}


class WiFiScannerWorker(QThread):
    """
    Background worker for WiFi scanning

    Runs scan in background thread to avoid UI blocking.
    """

    # Signals
    scan_complete = pyqtSignal(list)   # List[WiFiAPInfo]
    scan_error = pyqtSignal(str)       # Error message

    def __init__(self, filter_ecg: bool = True):
        super().__init__()
        self.filter_ecg = filter_ecg

    def run(self):
        """Run WiFi scan"""
        try:
            scanner = WiFiScanner()
            if self.filter_ecg:
                devices = scanner.scan_ecg_devices()
            else:
                devices = scanner.scan()
            self.scan_complete.emit([ap.__dict__ for ap in devices])
        except Exception as e:
            self.scan_error.emit(str(e))


class WiFiConnectionChecker(QObject):
    """
    WiFi connection status checker

    Periodically checks WiFi connection status.
    """

    # Signals
    connection_changed = pyqtSignal(dict)  # Connection info dict

    def __init__(self):
        super().__init__()
        self._scanner = WiFiScanner()

    def check_connection(self) -> dict:
        """Check current WiFi connection"""
        return self._scanner.get_current_connection()

    def is_connected_to_ecg(self) -> bool:
        """Check if connected to ECG-Physio AP"""
        conn = self.check_connection()
        return conn.get('ssid', '').startswith(WiFiScanner.TARGET_SSID_PREFIX)


# ==================== Test Code ====================

if __name__ == "__main__":
    print("Testing WiFi Scanner...")
    print(f"Platform: {platform.system()}")

    scanner = WiFiScanner()

    # Test scan
    print("\n--- All WiFi APs ---")
    all_aps = scanner.scan()
    for ap in all_aps:
        print(f"  {ap}")

    # Test ECG device filter
    print("\n--- ECG-Physio Devices ---")
    ecg_devices = scanner.scan_ecg_devices()
    for ap in ecg_devices:
        print(f"  {ap}")

    # Test current connection
    print("\n--- Current WiFi Connection ---")
    conn = scanner.get_current_connection()
    print(f"  SSID: {conn['ssid']}")
    print(f"  Connected: {conn['connected']}")
    print(f"  Is ECG Device: {scanner.get_current_connection()['ssid'].startswith('ECG-Physio')}")