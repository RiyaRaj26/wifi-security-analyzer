import time
import random
import logging

logger = logging.getLogger("WiFiScanner")

# Attempt to import pywifi. If not available, we will rely on SimulatedScanner.
PYWIFI_AVAILABLE = False
try:
    import pywifi
    from pywifi import const
    PYWIFI_AVAILABLE = True
except ImportError:
    pass

class WiFiNetwork:
    def __init__(self, ssid, bssid, rssi, channel, frequency, security_type, encryption, quality, is_hidden=False):
        self.ssid = ssid
        self.bssid = bssid  # MAC address
        self.rssi = rssi  # Signal strength in dBm (e.g., -60)
        self.channel = channel
        self.frequency = frequency  # in MHz (e.g., 2412)
        self.security_type = security_type  # e.g., "WPA3-Personal", "WPA2-Personal", "WEP", "Open"
        self.encryption = encryption  # e.g., "CCMP", "TKIP", "WEP", "None"
        self.quality = quality  # percentage 0-100
        self.is_hidden = is_hidden

    def to_dict(self):
        return {
            "ssid": self.ssid,
            "bssid": self.bssid,
            "rssi": self.rssi,
            "channel": self.channel,
            "frequency": self.frequency,
            "security_type": self.security_type,
            "encryption": self.encryption,
            "quality": self.quality,
            "is_hidden": self.is_hidden
        }

class WiFiScanner:
    def __init__(self, use_simulation=False):
        self.use_simulation = use_simulation or not PYWIFI_AVAILABLE
        self.wifi = None
        self.interface = None
        
        if not self.use_simulation and PYWIFI_AVAILABLE:
            try:
                self.wifi = pywifi.PyWiFi()
                interfaces = self.wifi.interfaces()
                if interfaces:
                    self.interface = interfaces[0]
                    logger.info(f"Using Wi-Fi interface: {self.interface.name()}")
                else:
                    logger.warning("No Wi-Fi interfaces found. Falling back to simulation.")
                    self.use_simulation = True
            except Exception as e:
                logger.error(f"Error initializing pywifi: {e}. Falling back to simulation.")
                self.use_simulation = True

    def scan(self) -> list[dict]:
        """Scans for networks and returns a list of dictionaries representing the networks."""
        if self.use_simulation:
            return self._simulate_scan()
        
        try:
            return self._live_scan()
        except Exception as e:
            logger.error(f"Live scan failed: {e}. Attempting simulated scan.")
            return self._simulate_scan()

    def is_simulated(self) -> bool:
        return self.use_simulation

    def _live_scan(self) -> list[dict]:
        if not self.interface:
            raise Exception("No physical interface selected.")
        
        # Trigger scan
        self.interface.scan()
        time.sleep(2.0)  # Wait for scanning to complete
        
        raw_results = self.interface.scan_results()
        networks = []
        seen_bssids = set()
        
        for profile in raw_results:
            bssid = profile.bssid
            # Sometimes BSSID comes as a bytes object or string. Make it clean format.
            if isinstance(bssid, bytes):
                bssid = ":".join(f"{b:02x}" for b in bssid)
            elif not bssid or bssid == '00:00:00:00:00:00':
                bssid = "00:11:22:33:44:55" # fallback helper
            else:
                bssid = str(bssid).strip().rstrip(":")
            
            # Skip duplicates in this single scan
            if bssid in seen_bssids:
                continue
            seen_bssids.add(bssid)
            
            ssid = profile.ssid
            is_hidden = False
            if not ssid or ssid == '\x00' * len(ssid):
                ssid = "<Hidden Network>"
                is_hidden = True
            
            # Map RSSI (typically raw signal percentage or dBm depending on PyWiFi version)
            raw_sig = profile.signal
            if raw_sig > 0:
                quality = min(raw_sig, 100)
                rssi = int((quality / 2) - 100) # approximate 100% -> -50dBm, 0% -> -100dBm
            else:
                rssi = raw_sig if raw_sig != 0 else -100
                quality = min(max(2 * (rssi + 100), 0), 100) # simple conversion
            
            # Parse frequency & channel
            freq = getattr(profile, 'freq', 0)
            if freq > 100000:
                freq = freq // 1000 # Convert kHz (e.g., 2412000) to MHz (2412)
            if not freq:
                freq = 2412
            
            channel = self._frequency_to_channel(freq)
            
            # Security types parsing
            sec_type, encryption = self._parse_security(profile)
            
            # If encryption is None/Unknown but WPA2/WPA3 is detected, default to AES-CCMP / GCMP
            if encryption in ["None", "Unknown"]:
                if "WPA3" in sec_type:
                    encryption = "AES-GCMP"
                elif "WPA2" in sec_type:
                    encryption = "AES-CCMP"
                elif "WPA" in sec_type:
                    encryption = "TKIP"
            
            networks.append(WiFiNetwork(
                ssid=ssid,
                bssid=bssid.upper(),
                rssi=rssi,
                channel=channel,
                frequency=freq,
                security_type=sec_type,
                encryption=encryption,
                quality=quality,
                is_hidden=is_hidden
            ).to_dict())
            
        # Sort by signal strength by default
        networks.sort(key=lambda x: x["rssi"], reverse=True)
        return networks

    def _frequency_to_channel(self, freq_mhz: int) -> int:
        if freq_mhz > 100000:
            freq_mhz = freq_mhz // 1000
        if freq_mhz == 2484:
            return 14
        elif 2407 < freq_mhz < 2484:
            return (freq_mhz - 2407) // 5
        elif 5030 <= freq_mhz <= 5900:
            return (freq_mhz - 5000) // 5
        # Fallback to a common 2.4GHz channel if invalid
        return 1

    def _parse_security(self, profile) -> tuple[str, str]:
        # PyWiFi security constants:
        # const.AKM_TYPE_NONE = 0
        # const.AKM_TYPE_WPA = 1
        # const.AKM_TYPE_WPAPSK = 2
        # const.AKM_TYPE_WPA2 = 3
        # const.AKM_TYPE_WPA2PSK = 4
        # const.AKM_TYPE_WPA3 = 8 (SAE, varies by version)
        
        akm = profile.akm
        cipher = getattr(profile, 'cipher', None)
        
        # Cipher types map
        # const.CIPHER_TYPE_NONE = 0
        # const.CIPHER_TYPE_WEP = 1
        # const.CIPHER_TYPE_TKIP = 2
        # const.CIPHER_TYPE_CCMP = 3
        
        # Get cipher string
        cipher_str = "Unknown"
        if cipher == 0:
            cipher_str = "None"
        elif cipher == 1:
            cipher_str = "WEP"
        elif cipher == 2:
            cipher_str = "TKIP"
        elif cipher == 3:
            cipher_str = "AES-CCMP"
            
        if not akm:
            # If no AKM but cipher is WEP, it's WEP
            if cipher == 1:
                return "WEP", "WEP"
            return "Open", "None"
            
        primary_akm = akm[0] if isinstance(akm, list) and len(akm) > 0 else akm
        
        if primary_akm == 0: # NONE
            if cipher == 1:
                return "WEP", "WEP"
            return "Open", "None"
        elif primary_akm == 1: # WPA
            return "WPA-Enterprise", cipher_str
        elif primary_akm == 2: # WPAPSK
            return "WPA-Personal", cipher_str
        elif primary_akm == 3: # WPA2
            return "WPA2-Enterprise", cipher_str
        elif primary_akm == 4: # WPA2PSK
            return "WPA2-Personal", cipher_str
        elif primary_akm in [8, 'WPA3', 'WPA3PSK', 'SAE']:
            return "WPA3-Personal", "AES-GCMP" if cipher_str == "Unknown" else cipher_str
        else:
            # Guess based on name/value
            if "WPA3" in str(primary_akm):
                return "WPA3-Personal", "AES-CCMP"
            return "WPA2-Personal", cipher_str

    def _simulate_scan(self) -> list[dict]:
        """Generates a realistic set of Wi-Fi networks in the area."""
        time.sleep(1.2) # Simulate scan latency
        
        simulated_data = [
            # Standard strong home network (WPA2)
            {"ssid": "Home-Network-Secure", "bssid": "B4:F2:E8:1A:2B:3C", "rssi": -42, "channel": 6, "frequency": 2437, "security_type": "WPA2-Personal", "encryption": "AES-CCMP", "quality": 95, "is_hidden": False},
            # Open network (Dangerous)
            {"ssid": "CoffeeShop_FreeWiFi", "bssid": "00:14:22:01:23:45", "rssi": -65, "channel": 1, "frequency": 2412, "security_type": "Open", "encryption": "None", "quality": 70, "is_hidden": False},
            # WEP network (Ancient/Insecure)
            {"ssid": "Legacy_Printer_Net", "bssid": "00:1E:58:FE:DC:BA", "rssi": -85, "channel": 11, "frequency": 2462, "security_type": "WEP", "encryption": "WEP", "quality": 30, "is_hidden": False},
            # WPA3 network (Excellent Security)
            {"ssid": "CyberShield_HQ", "bssid": "E8:94:F6:A3:B2:C1", "rssi": -55, "channel": 36, "frequency": 5180, "security_type": "WPA3-Personal", "encryption": "AES-GCMP", "quality": 85, "is_hidden": False},
            # Duplicate SSID (Potential Evil Twin Attack simulation)
            # This is an open network duplicating "Home-Network-Secure" but with weaker signal
            {"ssid": "Home-Network-Secure", "bssid": "00:25:9C:AB:CD:EF", "rssi": -72, "channel": 11, "frequency": 2462, "security_type": "Open", "encryption": "None", "quality": 55, "is_hidden": False},
            # A hidden network
            {"ssid": "<Hidden Network>", "bssid": "9C:D3:6D:7E:8F:90", "rssi": -68, "channel": 6, "frequency": 2437, "security_type": "WPA2-Personal", "encryption": "AES-CCMP", "quality": 64, "is_hidden": True},
            # WPA network (Weak)
            {"ssid": "Warehouse_Scanner", "bssid": "00:1B:77:22:33:44", "rssi": -78, "channel": 1, "frequency": 2412, "security_type": "WPA-Personal", "encryption": "TKIP", "quality": 44, "is_hidden": False},
            # Another standard network in the area causing channel congestion on Ch 6
            {"ssid": "Netgear_Extender", "bssid": "C4:04:15:3A:4B:5C", "rssi": -70, "channel": 6, "frequency": 2437, "security_type": "WPA2-Personal", "encryption": "AES-CCMP", "quality": 60, "is_hidden": False},
            # Another standard network causing channel congestion on Ch 1
            {"ssid": "Linksys_Guest", "bssid": "00:23:69:4D:5E:6F", "rssi": -82, "channel": 1, "frequency": 2412, "security_type": "WPA2-Personal", "encryption": "AES-CCMP", "quality": 36, "is_hidden": False},
            # 5GHz WPA2 network
            {"ssid": "Comcast_5G", "bssid": "70:3E:AC:8D:9E:0F", "rssi": -62, "channel": 149, "frequency": 5745, "security_type": "WPA2-Personal", "encryption": "AES-CCMP", "quality": 76, "is_hidden": False},
        ]
        
        # Add slight randomness to signals to simulate real scans
        for net in simulated_data:
            net["rssi"] += random.randint(-3, 3)
            net["rssi"] = min(max(net["rssi"], -100), -30)
            net["quality"] = min(max(2 * (net["rssi"] + 100), 0), 100)
            
        return sorted(simulated_data, key=lambda x: x["rssi"], reverse=True)
