import threading
import logging
from scanner.wifi_scanner import WiFiScanner
from analyzer.security_analyzer import SecurityAnalyzer
from database.db_manager import DatabaseManager
from reports.pdf_generator import PDFGenerator
from utils.ai_advisor import AISecurityAdvisor

logger = logging.getLogger("MainController")

class MainController:
    def __init__(self):
        # Models
        self.scanner = WiFiScanner()
        self.analyzer = SecurityAnalyzer()
        self.db = DatabaseManager()
        self.pdf_gen = PDFGenerator()
        self.advisor = AISecurityAdvisor()
        
        # View (Will be injected by main entry point)
        self.view = None
        
        # In-memory store of current scan results
        self.current_networks = []
        self.current_advice = {}

    def set_view(self, view):
        self.view = view
        # Inform the main window about whether it is simulated or live
        self.view.update_scan_mode(self.scanner.is_simulated())

    def trigger_scan(self):
        """Triggers a Wi-Fi scan in a background thread to prevent UI freezing."""
        if not self.view:
            return
            
        self.view.dashboard.show_loading()
        self.view.update_status("Scanning wireless frequencies...")

        def thread_target():
            try:
                # 1. Perform network scan (Simulated or PyWiFi Live)
                raw_nets = self.scanner.scan()
                
                # 2. Run security score and vulnerability analysis
                analyzed_nets = self.analyzer.analyze_networks(raw_nets)
                
                # 3. Generate AI Security advisor recommendations
                advice = self.advisor.generate_advice(analyzed_nets)
                
                # 4. Save results to database history
                scan_id = self.db.save_scan(analyzed_nets)
                
                # 5. Safe callback into main thread to update UI
                self.view.after(0, lambda: self._on_scan_complete(analyzed_nets, advice, scan_id))
            except Exception as e:
                logger.error(f"Background scanning thread failed: {e}", exc_info=True)
                self.view.after(0, self._on_scan_failed)

        threading.Thread(target=thread_target, daemon=True).start()

    def _on_scan_complete(self, networks: list[dict], advice: dict, scan_id: int):
        self.current_networks = networks
        self.current_advice = advice
        
        # Update dashboard widgets
        self.view.dashboard.set_networks(networks)
        self.view.dashboard.hide_loading()
        
        # Update Channel Analyzer widgets
        self.view.channel.set_networks_data(networks, advice)
        
        # Reload scan history list
        self.load_history()
        
        self.view.update_status("Scan complete. Network environment audited.")
        logger.info(f"Scan complete. ID: {scan_id}")

    def _on_scan_failed(self):
        self.view.dashboard.hide_loading()
        self.view.update_status("Error: Scan failed to complete.")
        from tkinter import messagebox
        messagebox.showerror("Scan Failure", "An error occurred during scanning. Check log files.")

    def select_network_for_analysis(self, network: dict):
        """Switches to the Security Analyzer tab and populates it with a specific AP."""
        if not self.view:
            return
        
        # Save in-memory chosen network
        self.view.analyzer.selected_network = network
        self.view.switch_tab("analyzer")

    # --- HISTORICAL RECORDS ACCESS ---
    def load_history(self):
        if not self.view:
            return
            
        history = self.db.get_history()
        # Find history view instance
        history_tab = self.view.tabs["history"]["instance"]
        if history_tab:
            history_tab.set_history_records(history)

    def delete_scan(self, scan_id: int) -> bool:
        success = self.db.delete_scan(scan_id)
        if success:
            self.view.update_status(f"Deleted scan log #{scan_id}")
        return success

    def export_scan_csv(self, scan_id: int, file_path: str) -> bool:
        return self.db.export_to_csv(scan_id, file_path)

    def export_scan_json(self, scan_id: int, file_path: str) -> bool:
        return self.db.export_to_json(scan_id, file_path)

    def export_scan_pdf(self, scan_id: int, file_path: str) -> bool:
        # Load details from DB
        networks = self.db.get_scan_details(scan_id)
        scan_info = self.db._get_scan_info(scan_id)
        if not networks or not scan_info:
            return False

        # Build analysis dictionaries for PDF generator
        # The DB stores raw strings. The analyzer accepts dictionaries and rebuilds risks.
        # We need to map DB keys back to keys used by analyzer/pdf_gen (e.g. 'score' -> 'security_score')
        mapped_networks = []
        for n in networks:
            net_dict = {
                "ssid": n["ssid"],
                "bssid": n["bssid"],
                "rssi": n["rssi"],
                "channel": n["channel"],
                # We approximate freq based on channel
                "frequency": 2400 + (n["channel"] * 5) if n["channel"] <= 14 else 5000 + (n["channel"] * 5),
                "security_type": n["security_type"],
                "encryption": n["encryption"]
            }
            # Re-analyze to generate risk items list
            analyzed = self.analyzer.analyze_networks([net_dict])[0]
            mapped_networks.append(analyzed)

        advice = self.advisor.generate_advice(mapped_networks)
        return self.pdf_gen.generate_report(file_path, scan_info, mapped_networks, advice)

    def compare_scans(self, scan_id_1: int, scan_id_2: int) -> dict:
        return self.db.compare_scans(scan_id_1, scan_id_2)
