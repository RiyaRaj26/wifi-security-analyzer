import logging
from collections import Counter

logger = logging.getLogger("AIAdvisor")

class AISecurityAdvisor:
    def __init__(self):
        pass

    def generate_advice(self, networks: list[dict]) -> dict:
        """
        Analyzes network scan results and generates educational/defensive
        cybersecurity recommendations, including channel optimizations and alerts.
        """
        if not networks:
            return {
                "summary": "No networks were detected. Ensure your Wi-Fi interface is enabled or that you are within range of an Access Point.",
                "recommendation": "Try moving closer to an window or scan again.",
                "channel_recommendations": {"2g": 1, "5g": 36},
                "status_level": "Unknown",
                "color": "#94A3B8"
            }

        # Analyze channels
        ch_recs = self.recommend_channels(networks)
        
        # Analyze overall security
        total_nets = len(networks)
        open_nets = [n for n in networks if "OPEN" in n["security_type"].upper()]
        wep_nets = [n for n in networks if "WEP" in n["security_type"].upper()]
        wpa_nets = [n for n in networks if n["security_type"] in ["WPA-Personal", "WPA-Enterprise"]]
        wpa3_nets = [n for n in networks if "WPA3" in n["security_type"].upper()]
        
        # Calculate average security score
        avg_score = sum(n.get("security_score", 0) for n in networks) / total_nets

        # Identify any critical flags
        has_evil_twin = False
        duplicate_ssids = []
        for n in networks:
            for risk in n.get("risks", []):
                if risk.get("name") == "Potential Evil Twin Attack":
                    has_evil_twin = True
                if risk.get("name") in ["Duplicate SSID Detected", "Potential Evil Twin Attack"]:
                    duplicate_ssids.append(n["ssid"])

        # Determine overall threat status level
        if has_evil_twin:
            status_level = "ACTIVE threat alert! Potential Rogue AP detected!"
            color = "#EF4444" # Red
        elif len(wep_nets) > 0 or len(open_nets) > 0:
            status_level = "Vulnerable networks present in the vicinity."
            color = "#F59E0B" # Orange
        elif avg_score < 70:
            status_level = "Moderate exposure. Several low-security networks nearby."
            color = "#F59E0B" # Orange
        else:
            status_level = "Low local threat environment."
            color = "#10B981" # Green

        # Build Executive Summary text
        summary = (
            f"Analyzed {total_nets} nearby Wi-Fi network(s) with an average security score of {avg_score:.1f}/100. "
        )
        
        findings = []
        if wpa3_nets:
            findings.append(f"{len(wpa3_nets)} network(s) utilize advanced WPA3 encryption (Excellent).")
        if open_nets:
            findings.append(f"{len(open_nets)} network(s) are completely OPEN (No encryption/password).")
        if wep_nets:
            findings.append(f"{len(wep_nets)} legacy network(s) use WEP (Highly vulnerable).")
        if wpa_nets:
            findings.append(f"{len(wpa_nets)} legacy network(s) use WPA1/TKIP (Outdated).")
            
        summary += " ".join(findings)

        # Build detailed advice checklist
        advice_list = []
        if has_evil_twin:
            duplicates_str = ", ".join(list(set(duplicate_ssids)))
            advice_list.append(
                f"🚨 **URGENT: Evil Twin Indicator Detected!** We detected duplicate access points for '{duplicates_str}' "
                "with mismatched security configurations. This frequently indicates an active phishing or packet-sniffing "
                "attempt using a Rogue Access Point. Do not associate with these networks."
            )
        elif duplicate_ssids:
            duplicates_str = ", ".join(list(set(duplicate_ssids)))
            advice_list.append(
                f"⚠️ **Duplicate SSIDs:** SSID '{duplicates_str}' is broadcasted by multiple physical radios. "
                "Ensure your system only connects to the authentic hardware MAC address (BSSID) for this network."
            )

        if open_nets:
            open_ssids = ", ".join([f"'{n['ssid']}'" for n in open_nets[:3]])
            advice_list.append(
                f"🔒 **Open Networks Nearby:** We detected unencrypted networks ({open_ssids}). "
                "Connecting to these exposes all unencrypted HTTP/DNS traffic to sniffing. "
                "Always run a trusted VPN if you must use public networks."
            )

        if wep_nets:
            advice_list.append(
                "❌ **Insecure WEP Detected:** Access points using legacy WEP are present. "
                "WEP keys can be extracted in seconds via automated statistical attacks. "
                "Never connect to WEP networks, and if you own these routers, immediately upgrade to WPA2/WPA3."
            )

        # Add Channel Recommendations
        rec_2g = ch_recs["2g"]
        rec_5g = ch_recs["5g"]
        advice_list.append(
            f"📶 **Optimal Channel Assignment:** To minimize RF collision and optimize speeds, "
            f"configure your 2.4GHz router to use **Channel {rec_2g}** and your 5GHz router to use **Channel {rec_5g}**. "
            f"These channels represent the lowest congestion levels in your current environment."
        )

        advice_text = "\n\n".join(advice_list)

        return {
            "summary": summary,
            "recommendation": advice_text,
            "channel_recommendations": ch_recs,
            "status_level": status_level,
            "color": color
        }

    def recommend_channels(self, networks: list[dict]) -> dict:
        """
        Examines channels in use and returns the best channels for 2.4GHz and 5GHz.
        For 2.4GHz, recommends one of the non-overlapping channels (1, 6, 11).
        For 5GHz, recommends from a set of common non-overlapping channels.
        """
        # 2.4GHz channels: 1 to 14. We want to evaluate the interference on the non-overlapping channels: 1, 6, 11.
        # We weigh networks by signal strength (stronger signal = more interference).
        # Weight = 100 + RSSI (e.g. -50 dBm -> weight 50, -80 dBm -> weight 20)
        channels_2g = {1: 0.0, 6: 0.0, 11: 0.0}
        
        # 5GHz channels to evaluate
        channels_5g = {36: 0.0, 40: 0.0, 44: 0.0, 48: 0.0, 149: 0.0, 153: 0.0, 157: 0.0, 161: 0.0}

        for net in networks:
            ch = net["channel"]
            rssi = net["rssi"]
            weight = max(10, 100 + rssi)  # Ensure a minimum weight

            # 2.4GHz overlap evaluation
            # Channels overlap with adjacent channels.
            # Channel 1 overlaps with 1, 2, 3, 4, 5
            # Channel 6 overlaps with 2, 3, 4, 5, 6, 7, 8, 9, 10
            # Channel 11 overlaps with 7, 8, 9, 10, 11, 12, 13, 14
            if ch <= 14:
                # Add weights to overlapping channels
                for standard_ch in [1, 6, 11]:
                    if abs(ch - standard_ch) < 5:
                        # Closer channels cause more co-channel or adjacent-channel interference
                        factor = 1.0 - (abs(ch - standard_ch) * 0.2)
                        channels_2g[standard_ch] += weight * max(0.2, factor)
            else:
                # 5GHz channels don't overlap with adjacent channels (except in bonded 40/80/160MHz channels,
                # but for simplicity we treat them as discrete).
                if ch in channels_5g:
                    channels_5g[ch] += weight
                else:
                    # If it's a 5GHz channel not in our standard list, find the closest one
                    for std_5g_ch in channels_5g.keys():
                        if abs(ch - std_5g_ch) < 4:
                            channels_5g[std_5g_ch] += weight * 0.5

        # Choose the channel with the minimum accumulated weight (interference score)
        best_2g = min(channels_2g, key=channels_2g.get)
        best_5g = min(channels_5g, key=channels_5g.get)

        return {
            "2g": best_2g,
            "5g": best_5g,
            "scores_2g": channels_2g,
            "scores_5g": channels_5g
        }
