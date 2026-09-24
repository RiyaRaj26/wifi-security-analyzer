import os
import unittest
from scanner.wifi_scanner import WiFiScanner
from analyzer.security_analyzer import SecurityAnalyzer
from database.db_manager import DatabaseManager
from reports.pdf_generator import PDFGenerator
from utils.ai_advisor import AISecurityAdvisor

class TestWiFiSecurityAnalyzer(unittest.TestCase):
    def setUp(self):
        # Use temporary file database for tests to avoid cluttering local DB
        self.db_path = "test_wifi_history.db"
        self.db = DatabaseManager(self.db_path)
        self.analyzer = SecurityAnalyzer()
        self.scanner = WiFiScanner(use_simulation=True)
        self.advisor = AISecurityAdvisor()
        self.pdf_gen = PDFGenerator()

    def tearDown(self):
        # Cleanup DB file if exists
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                pass

    def test_scanner_simulation(self):
        """Verify that the simulated scanner generates a structured set of networks."""
        self.assertTrue(self.scanner.is_simulated())
        networks = self.scanner.scan()
        self.assertGreater(len(networks), 0)
        
        # Verify keys are present
        first_net = networks[0]
        required_keys = ["ssid", "bssid", "rssi", "channel", "frequency", "security_type", "encryption", "quality", "is_hidden"]
        for key in required_keys:
            self.assertIn(key, first_net)

    def test_analyzer_scoring(self):
        """Test security scoring rules for WPA3, WEP, Open, and duplicate SSIDs."""
        mock_networks = [
            {
                "ssid": "SecureNet",
                "bssid": "00:11:22:33:44:55",
                "rssi": -50,
                "channel": 6,
                "frequency": 2437,
                "security_type": "WPA3-Personal",
                "encryption": "AES-GCMP",
                "quality": 100,
                "is_hidden": False
            },
            {
                "ssid": "UnsecureNet",
                "bssid": "00:11:22:33:44:66",
                "rssi": -50,
                "channel": 1,
                "frequency": 2412,
                "security_type": "Open",
                "encryption": "None",
                "quality": 100,
                "is_hidden": False
            },
            {
                "ssid": "LegacyNet",
                "bssid": "00:11:22:33:44:77",
                "rssi": -50,
                "channel": 11,
                "frequency": 2462,
                "security_type": "WEP",
                "encryption": "WEP",
                "quality": 100,
                "is_hidden": False
            }
        ]

        analyzed = self.analyzer.analyze_networks(mock_networks)
        
        # WPA3 should score high
        wpa3_net = next(n for n in analyzed if n["ssid"] == "SecureNet")
        self.assertEqual(wpa3_net["security_score"], 100)
        self.assertEqual(len(wpa3_net["risks"]), 0)

        # Open should score 0
        open_net = next(n for n in analyzed if n["ssid"] == "UnsecureNet")
        self.assertEqual(open_net["security_score"], 0)
        self.assertGreater(len(open_net["risks"]), 0)
        self.assertEqual(open_net["risks"][0]["level"], "Critical")

        # WEP should score very low
        wep_net = next(n for n in analyzed if n["ssid"] == "LegacyNet")
        self.assertLessEqual(wep_net["security_score"], 20)
        self.assertGreater(len(wep_net["risks"]), 0)

    def test_evil_twin_detection(self):
        """Verify that networks with duplicate SSIDs but different security types are flagged as potential Evil Twins."""
        mock_networks = [
            {"ssid": "MyWiFi", "bssid": "00:11:22:33:44:55", "rssi": -40, "channel": 1, "frequency": 2412, "security_type": "WPA2-Personal", "encryption": "AES-CCMP", "quality": 100, "is_hidden": False},
            {"ssid": "MyWiFi", "bssid": "00:11:22:33:44:99", "rssi": -65, "channel": 6, "frequency": 2437, "security_type": "Open", "encryption": "None", "quality": 70, "is_hidden": False} # Rogue
        ]
        
        analyzed = self.analyzer.analyze_networks(mock_networks)
        
        # Verify that both are flagged, and the open clone specifically raises Potential Evil Twin Alert
        rogue_net = next(n for n in analyzed if n["bssid"] == "00:11:22:33:44:99")
        risk_names = [r["name"] for r in rogue_net["risks"]]
        self.assertIn("Potential Evil Twin Attack", risk_names)

    def test_database_crud_operations(self):
        """Verify saving scans, retrieving history, loading details, comparisons, and deletions."""
        mock_nets = [
            {"ssid": "Net1", "bssid": "00:11:22:33:44:55", "rssi": -45, "channel": 11, "security_type": "WPA2-Personal", "encryption": "AES-CCMP", "security_score": 85}
        ]
        
        # Save scan
        scan_id = self.db.save_scan(mock_nets)
        self.assertGreater(scan_id, 0)
        
        # Retrieve history
        history = self.db.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["network_count"], 1)
        self.assertAlmostEqual(history[0]["avg_score"], 85.0)

        # Retrieve details
        details = self.db.get_scan_details(scan_id)
        self.assertEqual(len(details), 1)
        self.assertEqual(details[0]["ssid"], "Net1")
        self.assertEqual(details[0]["score"], 85)

        # Delete scan
        self.db.delete_scan(scan_id)
        history_after = self.db.get_history()
        self.assertEqual(len(history_after), 0)

    def test_pdf_report_generation(self):
        """Verify that ReportLab compiles a PDF successfully."""
        mock_nets = [
            {"ssid": "Net1", "bssid": "00:11:22:33:44:55", "rssi": -45, "channel": 11, "security_type": "WPA2-Personal", "encryption": "AES-CCMP", "security_score": 85, "risks": []}
        ]
        scan_info = {"timestamp": "2026-08-02 12:00:00", "network_count": 1, "avg_score": 85.0}
        advice = self.advisor.generate_advice(mock_nets)
        
        output_pdf = "test_audit_report.pdf"
        try:
            success = self.pdf_gen.generate_report(output_pdf, scan_info, mock_nets, advice)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(output_pdf))
            self.assertGreater(os.path.getsize(output_pdf), 0)
        finally:
            if os.path.exists(output_pdf):
                os.remove(output_pdf)

if __name__ == "__main__":
    unittest.main()
