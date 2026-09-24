import sqlite3
import os
import json
import csv
import logging
from datetime import datetime

logger = logging.getLogger("DatabaseManager")

class DatabaseManager:
    def __init__(self, db_path="wifi_history.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enable Foreign Key support
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Table for overall scan sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    network_count INTEGER NOT NULL,
                    avg_score REAL NOT NULL
                )
            """)
            
            # Table for specific network details in each scan
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scan_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER NOT NULL,
                    ssid TEXT NOT NULL,
                    bssid TEXT NOT NULL,
                    rssi INTEGER NOT NULL,
                    channel INTEGER NOT NULL,
                    security_type TEXT NOT NULL,
                    encryption TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    FOREIGN KEY (scan_id) REFERENCES scans (id) ON DELETE CASCADE
                )
            """)
            conn.commit()
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
        finally:
            if conn:
                conn.close()

    def save_scan(self, networks: list[dict]) -> int:
        """Saves scan result to database and returns the new scan ID."""
        if not networks:
            return -1

        avg_score = sum(net.get("security_score", 0) for net in networks) / len(networks)
        network_count = len(networks)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            # Insert master record
            cursor.execute(
                "INSERT INTO scans (timestamp, network_count, avg_score) VALUES (?, ?, ?)",
                (timestamp, network_count, avg_score)
            )
            scan_id = cursor.lastrowid

            # Insert details
            for net in networks:
                cursor.execute("""
                    INSERT INTO scan_details (
                        scan_id, ssid, bssid, rssi, channel, security_type, encryption, score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    scan_id,
                    net.get("ssid", "<Unknown>"),
                    net.get("bssid", "00:00:00:00:00:00"),
                    net.get("rssi", -100),
                    net.get("channel", 0),
                    net.get("security_type", "Open"),
                    net.get("encryption", "None"),
                    net.get("security_score", 0)
                ))
            conn.commit()
            logger.info(f"Saved scan {scan_id} with {network_count} networks.")
            return scan_id
        except Exception as e:
            logger.error(f"Error saving scan to database: {e}")
            return -1
        finally:
            if conn:
                conn.close()

    def get_history(self) -> list[dict]:
        """Returns list of overall scans sorted by date descending."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scans ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching scan history: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_scan_details(self, scan_id: int) -> list[dict]:
        """Returns detailed network list for a specific scan ID."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scan_details WHERE scan_id = ? ORDER BY score DESC", (scan_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching scan details for ID {scan_id}: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def delete_scan(self, scan_id: int) -> bool:
        """Deletes a scan and associated details. Returns success bool."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
            conn.commit()
            logger.info(f"Deleted scan ID {scan_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting scan ID {scan_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def compare_scans(self, scan_id_1: int, scan_id_2: int) -> dict:
        """
        Compares two scans and returns stats and structural changes.
        scan_id_1: older scan (baseline)
        scan_id_2: newer scan (target)
        """
        details1 = self.get_scan_details(scan_id_1)
        details2 = self.get_scan_details(scan_id_2)

        # Get scans timestamps
        scan_info1 = self._get_scan_info(scan_id_1)
        scan_info2 = self._get_scan_info(scan_id_2)

        nets1 = {n["bssid"]: n for n in details1}
        nets2 = {n["bssid"]: n for n in details2}

        added = []
        removed = []
        changed = []

        for bssid, net2 in nets2.items():
            if bssid not in nets1:
                added.append(net2)
            else:
                net1 = nets1[bssid]
                # Compare security or channel
                if net1["security_type"] != net2["security_type"] or net1["score"] != net2["score"]:
                    changed.append({
                        "ssid": net2["ssid"],
                        "bssid": bssid,
                        "old_security": net1["security_type"],
                        "new_security": net2["security_type"],
                        "old_score": net1["score"],
                        "new_score": net2["score"]
                    })

        for bssid, net1 in nets1.items():
            if bssid not in nets2:
                removed.append(net1)

        avg_score_diff = 0
        if scan_info1 and scan_info2:
            avg_score_diff = scan_info2["avg_score"] - scan_info1["avg_score"]

        return {
            "scan_1": scan_info1,
            "scan_2": scan_info2,
            "added_count": len(added),
            "removed_count": len(removed),
            "changed_count": len(changed),
            "added": added,
            "removed": removed,
            "changed": changed,
            "avg_score_diff": avg_score_diff
        }

    def _get_scan_info(self, scan_id: int) -> dict:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error fetching scan master info: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def export_to_csv(self, scan_id: int, file_path: str) -> bool:
        """Exports a single scan session's details to CSV."""
        details = self.get_scan_details(scan_id)
        scan_info = self._get_scan_info(scan_id)
        if not details or not scan_info:
            return False

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Scan ID", scan_id])
                writer.writerow(["Timestamp", scan_info["timestamp"]])
                writer.writerow(["Total Networks", scan_info["network_count"]])
                writer.writerow(["Average Security Score", f"{scan_info['avg_score']:.1f}"])
                writer.writerow([])
                writer.writerow(["SSID", "BSSID", "Signal Strength (RSSI)", "Channel", "Security Type", "Encryption", "Security Score"])
                
                for net in details:
                    writer.writerow([
                        net["ssid"],
                        net["bssid"],
                        net["rssi"],
                        net["channel"],
                        net["security_type"],
                        net["encryption"],
                        net["score"]
                    ])
            return True
        except Exception as e:
            logger.error(f"Failed to export scan to CSV: {e}")
            return False

    def export_to_json(self, scan_id: int, file_path: str) -> bool:
        """Exports a single scan session's details to JSON."""
        details = self.get_scan_details(scan_id)
        scan_info = self._get_scan_info(scan_id)
        if not details or not scan_info:
            return False

        data = {
            "scan_id": scan_id,
            "timestamp": scan_info["timestamp"],
            "network_count": scan_info["network_count"],
            "avg_score": scan_info["avg_score"],
            "networks": [dict(net) for net in details]
        }

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Failed to export scan to JSON: {e}")
            return False
