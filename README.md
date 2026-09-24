# 🛡️ Wi-Fi Security Analyzer

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-CustomTkinter-0ea5e9.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Security](https://img.shields.io/badge/Focus-Defensive%20Security-10b981.svg)]()
[![License](https://img.shields.io/badge/License-MIT-slate.svg)]()

A modern, cybersecurity-focused desktop application built with Python and CustomTkinter designed to audit, analyze, and educate users on the security posture of nearby Wi-Fi networks.

> [!IMPORTANT]
> **Defensive & Educational Use Only:**
> This tool is strictly designed for network defense, awareness, and auditing your own wireless environment. It does **not** perform unauthorized access, password cracking, packet injection, or deauthentication attacks.

---

## 📸 Overview & Features

### 1. 🛡️ Network Scanner & Dashboard
- **Live Hardware Scanning:** Leverages `pywifi` and Windows Native Wi-Fi APIs to scan live, real-time wireless access points.
- **Simulated Scan Mode:** Automatically provides a realistic multi-AP simulation environment if physical wireless interfaces or permissions are absent.
- **Detailed Network Attributes:** SSID, BSSID (MAC Address), Signal Strength (RSSI dBm), Frequency, Channel, Security Protocol, Encryption Cipher, Signal Quality %, and Hidden SSID detection.
- **Sort & Filter:** Instant sorting by Signal Strength, Security Score, Channel, or SSID; filter networks by WPA3, WPA2, Legacy (WPA/WEP), or Open.

### 2. 🔍 Security Analyzer & Risk Detection
- **Dynamic Security Scoring (0–100):** Evaluates protocol strength (WPA3: 100, WPA2: 85, WPA/TKIP: 50, WEP: 20, Open: 0) and applies modifiers for signal degradation and channel crowding.
- **Color-Coded Risk Badges:** Highlights risks as Critical (Red), High (Dark Orange), Medium (Amber), or Low (Slate).
- **Vulnerability Engine:**
  - **Open Wi-Fi:** Unencrypted data exposure risk.
  - **Deprecated WEP / TKIP:** Outdated ciphers subject to automated statistical cracking.
  - **Duplicate SSIDs / Evil Twin Warning:** Alerts when multiple access points share the same SSID with mismatched security configurations (rogue AP behavior).
  - **Signal Degradation:** Explains packet loss and re-authentication handshake exposure.
  - **Crowded Channels:** Identifies overlapping channel saturation.
- **Actionable Mitigations:** Clear, beginner-friendly instructions on how to harden your router.

### 3. 📊 Channel Analyzer
- **Overlapping Signal Domes:** Embedded dark-mode Matplotlib visualizer showing 2.4 GHz channel parabolas and signal overlap.
- **Smart Channel Recommendations:** Identifies the least congested non-overlapping channels (Channels 1, 6, 11 for 2.4 GHz, and optimal 5 GHz channels).

### 4. 🤖 AI Security Advisor
- Summarizes scan findings into plain-English defensive summaries.
- Evaluates environmental threat levels and generates personalized recommendations for your wireless setup.

### 5. 📚 Cybersecurity Awareness Hub
- Educational reference covering:
  - WPA vs. WPA2 vs. WPA3 differences
  - Why WEP is insecure
  - Dangers of Public Wi-Fi & Man-in-the-Middle (MitM) attacks
  - Evil Twin attacks & Rogue Access Points
  - VPN encryption fundamentals
  - Router hardening checklist (admin passwords, disabling WPS, isolating IoT guest networks)

### 6. 📄 PDF Audit Reports & History Logging
- **PDF Generation:** Downloadable, clean security reports using ReportLab detailing executive summaries, network tables, vulnerability breakdowns, and mitigations.
- **SQLite Database:** Automatically logs scan sessions with timestamps, network counts, and average scores.
- **Scan Comparisons:** Side-by-side comparison between any two historical scans to identify newly added access points, security configuration changes, or rogue networks.
- **Export Formats:** Export scan logs to CSV, JSON, or PDF.

### 7. 🔮 Concept Labs (Interactive Simulations)
- **Speed Test Simulator:** Interactive speedometer dial checking simulated ping, download, and upload speeds.
- **Live Signal Wave:** Real-time animating canvas charting signal RSSI fluctuations.
- **RF Coverage Heatmap:** Interactive 8x6 building grid simulator calculating signal attenuation and dead zones.
- **AI Advisor Chatbot:** Offline security chatbot answering queries about wireless protocols and protections.
- **Router Audit Checker:** Simulated gateway test checking for default credentials and DNS leaks.

---

## 🏗️ Architecture (MVC Pattern)

The project follows a strict **Model-View-Controller** design:

```
wifi-security-analyzer/
├── main.py                     # Entry point & application lifecycle
├── requirements.txt            # Dependency list
├── test_app.py                 # Automated unit tests
├── scanner/                    # Model: Wi-Fi interfaces & scanning
│   └── wifi_scanner.py         # PyWiFi wrapper + Simulated scanner
├── analyzer/                   # Model: Security scoring & vulnerability checks
│   └── security_analyzer.py    # Scoring formulas, risk rules, and mitigations
├── database/                   # Model: SQLite storage & data management
│   └── db_manager.py           # SQLite CRUD, history compare, CSV/JSON export
├── reports/                    # Model: PDF document compilation
│   └── pdf_generator.py        # ReportLab PDF styling & generation
├── utils/                      # Helper & advisory utilities
│   └── ai_advisor.py           # Rule-based expert advisor & channel algorithm
├── ui/                         # Views: CustomTkinter presentation layer
│   ├── theme.py                # Color palette, dark theme tokens, styled cards
│   ├── main_window.py          # Window frame, sidebar navigation, status bar
│   ├── dashboard_view.py       # Scanner table, filters, sorting, scan controls
│   ├── analyzer_view.py        # Circular score gauge, vulnerability details
│   ├── channel_view.py         # Matplotlib channel graphs & recommendations
│   ├── education_view.py       # Awareness cards & router hardening guide
│   ├── history_view.py         # Past audit logs, comparison engine, exports
│   └── future_view.py          # Concept Labs: speed test, heatmap, chatbot
└── controller/                 # Controller: Orchestrates flow & background tasks
    └── main_controller.py     # Background threading, event handling, MVC glue
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Windows 10/11 (with Wi-Fi card enabled for live scanning)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd "wifi security analyzer"
   ```

2. **Create and activate a virtual environment:**
   ```powershell
   # Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Running the Application

Launch the desktop GUI:

```powershell
# Using the virtual environment python
.\.venv\Scripts\python main.py

# Or if virtual environment is already activated:
python main.py
```

### Quick Workflow
1. Click **⚡ Scan Networks** on the dashboard.
2. Filter or sort by security type, signal strength, or channel.
3. Double-click any network (or click **Analyze**) to open the in-depth **Security Analyzer** with the circular score gauge and vulnerability breakdown.
4. Navigate to **📊 Channel Analyzer** to view 2.4 GHz channel congestion and optimal channel recommendations for your router.
5. Navigate to **⏳ Scan History** to compare scans or export reports to **PDF**, **CSV**, or **JSON**.

---

## 🧪 Running Automated Tests

Run the test suite to verify the scanner, scoring engine, SQLite database operations, and PDF generation:

```powershell
.\.venv\Scripts\python -m unittest test_app.py
```

---

## 🛡️ Educational & Defensive Disclaimer

This software is developed strictly for **educational and defensive cybersecurity purposes**. The security scores and analysis are intended to help home and office administrators identify weak wireless protocols (such as unencrypted Open networks or deprecated WEP/TKIP) and recognize unauthorized rogue access points. 

Users are responsible for ensuring compliance with all local laws and organizational policies.
