import logging
from collections import Counter

logger = logging.getLogger("SecurityAnalyzer")

class RiskItem:
    def __init__(self, name, level, explanation, mitigation):
        self.name = name  # e.g., "Open Wi-Fi Network"
        self.level = level  # "Critical", "High", "Medium", "Low"
        self.explanation = explanation
        self.mitigation = mitigation

    def to_dict(self):
        return {
            "name": self.name,
            "level": self.level,
            "explanation": self.explanation,
            "mitigation": self.mitigation
        }

class SecurityAnalyzer:
    def __init__(self):
        pass

    def analyze_networks(self, networks: list[dict]) -> list[dict]:
        """
        Analyzes a list of Wi-Fi networks. Calculates security scores and attaches
        detected risks to each network. Returns the list of networks with 'score' and 'risks' added.
        """
        # Count SSID frequencies to detect duplicate SSIDs (potential Evil Twin)
        ssid_counts = Counter(net["ssid"] for net in networks if net["ssid"] != "<Hidden Network>")
        
        # Count channel usage to detect crowded channels
        channel_counts = Counter(net["channel"] for net in networks)

        analyzed_networks = []
        for net in networks:
            ssid = net["ssid"]
            bssid = net["bssid"]
            rssi = net["rssi"]
            channel = net["channel"]
            sec_type = net["security_type"]
            encryption = net["encryption"]

            # 1. Base Security Score
            score, base_risks = self._calculate_base_score_and_risks(sec_type, encryption)
            
            # 2. Duplicate SSID (Evil Twin) Detection
            evil_twin_risks = []
            if ssid != "<Hidden Network>" and ssid_counts[ssid] > 1:
                # Find all networks with the same SSID
                siblings = [n for n in networks if n["ssid"] == ssid and n["bssid"] != bssid]
                
                # Check if sibling has a different security type (e.g. one secure, one open)
                different_security = any(sib["security_type"] != sec_type for sib in siblings)
                
                if different_security:
                    # High Risk: Same SSID, different security protocol
                    evil_twin_risks.append(RiskItem(
                        name="Potential Evil Twin Attack",
                        level="High",
                        explanation=f"Another network is broadcasting the exact same SSID ('{ssid}') but using a different security protocol. This is a common indicator of an Evil Twin rogue access point attempting to intercept your traffic.",
                        mitigation="Do not connect to this network. Verify with the administrator which MAC address and security standard is official."
                    ))
                else:
                    # Low/Medium Risk: Duplicate SSID (likely normal multi-AP roaming or mesh, but good to note)
                    evil_twin_risks.append(RiskItem(
                        name="Duplicate SSID Detected",
                        level="Low",
                        explanation=f"Multiple access points are broadcasting the SSID '{ssid}'. While common in mesh networks or large buildings, attackers can sometimes clone SSIDs to perform rogue access point actions.",
                        mitigation="Ensure you are connecting to the access point with the strongest signal and verify the MAC address if security is a high priority."
                    ))

            # 3. Crowded Channel Detection
            channel_risks = []
            # In 2.4GHz band (Channels 1 to 14), channels overlap unless they are 1, 6, or 11.
            # Let's count how many APs are sharing the channel
            aps_on_channel = channel_counts[channel]
            if aps_on_channel >= 4:
                channel_risks.append(RiskItem(
                    name="Crowded Wi-Fi Channel",
                    level="Medium",
                    explanation=f"Channel {channel} is heavily congested with {aps_on_channel} access points operating on it. This causes signal interference, high packet collisions, and slower speeds.",
                    mitigation="If this is your router, change your channel settings to a less congested one (e.g., 1, 6, or 11 in the 2.4GHz band, or switch to 5GHz)."
                ))

            # 4. Weak Signal Strength
            signal_risks = []
            if rssi < -80:
                signal_risks.append(RiskItem(
                    name="Extremely Weak Signal Strength",
                    level="Medium",
                    explanation=f"The signal strength is very low ({rssi} dBm). Low signals lead to packet loss, frequent dropouts, and trigger re-authentications which attackers can sniff to launch offline password-cracking attacks.",
                    mitigation="Move closer to the router or install a range extender to increase signal quality and reduce connection instability."
                ))
            elif rssi < -70:
                signal_risks.append(RiskItem(
                    name="Moderate Signal Strength",
                    level="Low",
                    explanation=f"The signal strength is moderate ({rssi} dBm). While functional, signal attenuation makes it slightly more vulnerable to disconnection.",
                    mitigation="Optimize the router's physical position away from walls or metal interference."
                ))

            # Accumulate risks
            all_risks = base_risks + evil_twin_risks + channel_risks + signal_risks
            
            # Score adjustments based on issues
            final_score = score
            for r in all_risks:
                if r.level == "Critical":
                    final_score -= 30
                elif r.level == "High":
                    final_score -= 20
                elif r.level == "Medium":
                    final_score -= 10
                elif r.level == "Low":
                    final_score -= 5
            
            final_score = max(0, min(100, final_score))

            net_copy = net.copy()
            net_copy["security_score"] = final_score
            net_copy["risks"] = [r.to_dict() for r in all_risks]
            analyzed_networks.append(net_copy)

        return analyzed_networks

    def _calculate_base_score_and_risks(self, sec_type: str, encryption: str) -> tuple[int, list[RiskItem]]:
        score = 100
        risks = []

        # Convert to upper case for safe string matching
        sec_upper = sec_type.upper()
        enc_upper = encryption.upper()

        if "OPEN" in sec_upper:
            score = 0
            risks.append(RiskItem(
                name="Open (Unencrypted) Wi-Fi",
                level="Critical",
                explanation="This network does not require a password or encrypt data. Any traffic sent over this network (emails, passwords, financial details) can be sniffed by anyone nearby using simple tools like Wireshark.",
                mitigation="Avoid connecting to this network. If you must use it, run a trusted Virtual Private Network (VPN) immediately to encrypt your data stream, and never access sensitive bank or personal accounts."
            ))
        elif "WEP" in sec_upper or "WEP" in enc_upper:
            score = 20
            risks.append(RiskItem(
                name="Deprecated WEP Encryption",
                level="Critical",
                explanation="WEP (Wired Equivalent Privacy) encryption is obsolete and has major cryptographic vulnerabilities. Attackers can crack the Wi-Fi key in less than a minute using automated tools.",
                mitigation="Change your router's security configuration from WEP to WPA2-Personal (AES) or WPA3. WEP is highly insecure and should never be used."
            ))
        elif "WPA-PERSONAL" in sec_upper or "TKIP" in enc_upper or "WPA" == sec_upper:
            score = 50
            risks.append(RiskItem(
                name="Outdated WPA or TKIP Encryption",
                level="High",
                explanation="WPA1 (Wi-Fi Protected Access) or the TKIP cipher has known security weaknesses and can be compromised. Many modern devices will show a security warning when connecting to TKIP networks.",
                mitigation="Upgrade your access point settings to WPA2-Personal with AES (CCMP) encryption. Disable TKIP entirely in your router's admin console."
            ))
        elif "WPA2" in sec_upper:
            # WPA2 is good, but check if cipher is TKIP (can happen on mixed WPA/WPA2 networks)
            if "TKIP" in enc_upper:
                score = 65
                risks.append(RiskItem(
                    name="WPA2 with TKIP Cipher",
                    level="Medium",
                    explanation="Although using WPA2, the TKIP encryption cipher is active. TKIP is deprecated, slower, and vulnerable to security compromises compared to AES.",
                    mitigation="Configure your wireless router to support 'AES only' (or CCMP) rather than 'WPA2 Mixed' or 'TKIP'."
                ))
            else:
                score = 85 # Good security baseline
        elif "WPA3" in sec_upper:
            score = 100 # Excellent, state-of-the-art security
        else:
            # Unknown security, play it safe
            score = 60
            risks.append(RiskItem(
                name="Non-Standard Security Protocol",
                level="Medium",
                explanation=f"The network reports security type '{sec_type}'. If this is a custom enterprise captive portal or non-standard protocol, its cryptographical strength is unverified.",
                mitigation="Verify with the network administrator that a secure protocol is being used, and use a VPN to be safe."
            ))

        return score, risks
