import customtkinter as ctk
from tkinter import filedialog, messagebox
from ui.theme import *

class HistoryView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        
        self.history_records = []
        self.selected_scan_id = None
        self._setup_ui()

    def _setup_ui(self):
        # Header
        self.header_lbl = ctk.CTkLabel(self, text="Scan History Logs", font=FONT_TITLE, text_color=COLOR_TEXT)
        self.header_lbl.pack(anchor="w", pady=(0, 15))

        # Split Layout (Left: Scan History Table, Right: Selected Scan Actions & Compare)
        self.main_split = ctk.CTkFrame(self, fg_color="transparent")
        self.main_split.pack(fill="both", expand=True)

        self.left_col = ctk.CTkFrame(self.main_split, fg_color="transparent")
        self.left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.right_col = ctk.CTkFrame(self.main_split, fg_color="transparent", width=380)
        self.right_col.pack(side="right", fill="both", padx=(10, 0))

        # --- LEFT COLUMN: HISTORY LIST ---
        self.list_card = StyledCard(self.left_col)
        self.list_card.pack(fill="both", expand=True)
        
        self.list_title = ctk.CTkLabel(self.list_card, text="Saved Historical Audits", font=FONT_SECTION, text_color=COLOR_TEXT)
        self.list_title.pack(pady=(12, 5), padx=15, anchor="w")

        # Table Header
        self.table_header = ctk.CTkFrame(self.list_card, fg_color=BG_SIDEBAR, height=30)
        self.table_header.pack(fill="x", padx=15, pady=5)
        
        lbl_id = ctk.CTkLabel(self.table_header, text="ID", font=FONT_BODY_BOLD, text_color=COLOR_TEXT_MUTED, width=40)
        lbl_id.pack(side="left", padx=10)
        
        lbl_time = ctk.CTkLabel(self.table_header, text="Date & Time", font=FONT_BODY_BOLD, text_color=COLOR_TEXT_MUTED, anchor="w")
        lbl_time.pack(side="left", fill="x", expand=True, padx=10)
        
        lbl_count = ctk.CTkLabel(self.table_header, text="Networks", font=FONT_BODY_BOLD, text_color=COLOR_TEXT_MUTED, width=80)
        lbl_count.pack(side="left", padx=10)
        
        lbl_score = ctk.CTkLabel(self.table_header, text="Avg Score", font=FONT_BODY_BOLD, text_color=COLOR_TEXT_MUTED, width=80)
        lbl_score.pack(side="right", padx=10)

        # Scrollable container for history items
        self.history_scroll = ctk.CTkScrollableFrame(self.list_card, fg_color="transparent")
        self.history_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # --- RIGHT COLUMN: ACTIONS & COMPARISONS ---
        # 1. Action Panel (details of selected item)
        self.action_card = StyledCard(self.right_col)
        self.action_card.pack(fill="x", pady=(0, 15), ipady=10)
        
        self.action_title = ctk.CTkLabel(self.action_card, text="Audit Management", font=FONT_SECTION, text_color=COLOR_TEXT)
        self.action_title.pack(pady=(12, 10), padx=15, anchor="w")
        
        self.selected_lbl = ctk.CTkLabel(self.action_card, text="No scan selected.", font=FONT_BODY, text_color=COLOR_TEXT_MUTED)
        self.selected_lbl.pack(anchor="w", padx=15, pady=5)

        # Buttons frame (PDF, CSV, JSON, Delete)
        self.buttons_frame = ctk.CTkFrame(self.action_card, fg_color="transparent")
        self.buttons_frame.pack(fill="x", padx=15, pady=10)
        
        self.btn_pdf = ctk.CTkButton(
            self.buttons_frame, text="📄 Generate PDF", font=FONT_SMALL,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_HOVER, state="disabled",
            command=self._export_pdf
        )
        self.btn_pdf.pack(fill="x", pady=4)

        self.btn_csv = ctk.CTkButton(
            self.buttons_frame, text="📊 Export CSV", font=FONT_SMALL,
            fg_color="transparent", border_color=COLOR_PRIMARY, border_width=1,
            text_color=COLOR_PRIMARY, hover_color="#1E293B", state="disabled",
            command=self._export_csv
        )
        self.btn_csv.pack(fill="x", pady=4)

        self.btn_json = ctk.CTkButton(
            self.buttons_frame, text="👾 Export JSON", font=FONT_SMALL,
            fg_color="transparent", border_color=COLOR_PRIMARY, border_width=1,
            text_color=COLOR_PRIMARY, hover_color="#1E293B", state="disabled",
            command=self._export_json
        )
        self.btn_json.pack(fill="x", pady=4)

        self.btn_delete = ctk.CTkButton(
            self.buttons_frame, text="🗑️ Delete Log", font=FONT_SMALL,
            fg_color="transparent", border_color=COLOR_DANGER, border_width=1,
            text_color=COLOR_DANGER, hover_color="#271313", state="disabled",
            command=self._delete_scan
        )
        self.btn_delete.pack(fill="x", pady=4)

        # 2. Compare Panel
        self.compare_card = StyledCard(self.right_col)
        self.compare_card.pack(fill="both", expand=True)

        self.compare_title = ctk.CTkLabel(self.compare_card, text="Compare Audits", font=FONT_SECTION, text_color=COLOR_TEXT)
        self.compare_title.pack(pady=(12, 10), padx=15, anchor="w")

        # Dropdowns for selection
        self.drop_base_var = ctk.StringVar(value="Select Baseline")
        self.drop_base = ctk.CTkOptionMenu(
            self.compare_card, values=["Select Baseline"], variable=self.drop_base_var,
            fg_color=BG_MAIN, button_color=COLOR_PRIMARY, button_hover_color=COLOR_HOVER
        )
        self.drop_base.pack(fill="x", padx=15, pady=5)

        self.drop_target_var = ctk.StringVar(value="Select Target")
        self.drop_target = ctk.CTkOptionMenu(
            self.compare_card, values=["Select Target"], variable=self.drop_target_var,
            fg_color=BG_MAIN, button_color=COLOR_PRIMARY, button_hover_color=COLOR_HOVER
        )
        self.drop_target.pack(fill="x", padx=15, pady=5)

        self.btn_compare = ctk.CTkButton(
            self.compare_card, text="⚖️ Compare Selected", font=FONT_BODY_BOLD,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_HOVER,
            command=self._compare_scans
        )
        self.btn_compare.pack(fill="x", padx=15, pady=10)

        # Comparison results text area
        self.compare_results_box = ctk.CTkTextbox(
            self.compare_card, 
            fg_color=BG_MAIN, 
            border_color="#1E293B", 
            border_width=1,
            font=FONT_SMALL,
            height=120
        )
        self.compare_results_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.compare_results_box.insert("1.0", "Select two scans and click 'Compare Selected' to see variations in security level, network count, or SSID configurations.")
        self.compare_results_box.configure(state="disabled")

    def set_history_records(self, records: list[dict]):
        self.history_records = records
        self.render_history_list()
        self.update_compare_dropdowns()

    def render_history_list(self):
        # Clear items
        for child in self.history_scroll.winfo_children():
            child.destroy()

        if not self.history_records:
            lbl = ctk.CTkLabel(
                self.history_scroll, 
                text="No scan records saved in database.", 
                font=FONT_BODY,
                text_color=COLOR_TEXT_MUTED
            )
            lbl.pack(pady=40)
            return

        for record in self.history_records:
            rec_id = record["id"]
            
            # Row button
            row_btn = ctk.CTkFrame(
                self.history_scroll, 
                fg_color=BG_CARD if rec_id != self.selected_scan_id else "#1E293B",
                border_color="#1E293B",
                border_width=1,
                corner_radius=6,
                height=35
            )
            row_btn.pack(fill="x", pady=3)
            row_btn.pack_propagate(False)
            
            # Make clickable
            row_btn.bind("<Button-1>", lambda e, rid=rec_id: self.select_scan(rid))

            # Render details
            lbl_id = ctk.CTkLabel(row_btn, text=f"#{rec_id}", font=FONT_BODY_BOLD, text_color=COLOR_PRIMARY, width=40)
            lbl_id.pack(side="left", padx=10)
            lbl_id.bind("<Button-1>", lambda e, rid=rec_id: self.select_scan(rid))

            lbl_time = ctk.CTkLabel(row_btn, text=record["timestamp"], font=FONT_BODY, text_color=COLOR_TEXT, anchor="w")
            lbl_time.pack(side="left", fill="x", expand=True, padx=10)
            lbl_time.bind("<Button-1>", lambda e, rid=rec_id: self.select_scan(rid))

            lbl_count = ctk.CTkLabel(row_btn, text=f"{record['network_count']} APs", font=FONT_BODY, text_color=COLOR_TEXT_MUTED, width=80)
            lbl_count.pack(side="left", padx=10)
            lbl_count.bind("<Button-1>", lambda e, rid=rec_id: self.select_scan(rid))

            # Color code average score
            score = record["avg_score"]
            score_color = COLOR_SAFE
            if score < 50:
                score_color = COLOR_DANGER
            elif score < 80:
                score_color = COLOR_WARN
                
            lbl_score = ctk.CTkLabel(row_btn, text=f"{score:.1f}/100", font=FONT_BODY_BOLD, text_color=score_color, width=80)
            lbl_score.pack(side="right", padx=10)
            lbl_score.bind("<Button-1>", lambda e, rid=rec_id: self.select_scan(rid))

    def update_compare_dropdowns(self):
        if not self.history_records:
            self.drop_base.configure(values=["Select Baseline"])
            self.drop_base_var.set("Select Baseline")
            self.drop_target.configure(values=["Select Target"])
            self.drop_target_var.set("Select Target")
            return

        options = [f"Scan #{r['id']} ({r['timestamp']})" for r in self.history_records]
        
        self.drop_base.configure(values=options)
        self.drop_target.configure(values=options)
        
        # Select first two as defaults if they exist
        if len(options) >= 2:
            self.drop_base_var.set(options[1]) # older
            self.drop_target_var.set(options[0]) # newer
        elif len(options) == 1:
            self.drop_base_var.set(options[0])
            self.drop_target_var.set(options[0])

    def select_scan(self, scan_id: int):
        self.selected_scan_id = scan_id
        self.render_history_list() # trigger redraw to show selection highlight
        
        # Find record details
        record = next((r for r in self.history_records if r["id"] == scan_id), None)
        if record:
            self.selected_lbl.configure(
                text=f"Selected: Scan #{record['id']}\n"
                     f"Date: {record['timestamp']}\n"
                     f"Count: {record['network_count']} access points\n"
                     f"Avg score: {record['avg_score']:.1f}/100",
                text_color=COLOR_TEXT
            )
            self.btn_pdf.configure(state="normal")
            self.btn_csv.configure(state="normal")
            self.btn_json.configure(state="normal")
            self.btn_delete.configure(state="normal")
        else:
            self.selected_lbl.configure(text="No scan selected.", text_color=COLOR_TEXT_MUTED)
            self.btn_pdf.configure(state="disabled")
            self.btn_csv.configure(state="disabled")
            self.btn_json.configure(state="disabled")
            self.btn_delete.configure(state="disabled")

    def _delete_scan(self):
        if not self.selected_scan_id:
            return
        
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to permanently delete Scan #{self.selected_scan_id} and all its detailed reports?"
        )
        if confirm:
            success = self.controller.delete_scan(self.selected_scan_id)
            if success:
                self.selected_scan_id = None
                self.select_scan(None)
                self.on_tab_active()

    def _export_csv(self):
        if not self.selected_scan_id:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"wifi_audit_scan_{self.selected_scan_id}.csv"
        )
        if file_path:
            success = self.controller.export_scan_csv(self.selected_scan_id, file_path)
            if success:
                messagebox.showinfo("Export Successful", f"Scan details successfully saved to:\n{file_path}")
            else:
                messagebox.showerror("Export Failed", "Could not export scan. Database or write error.")

    def _export_json(self):
        if not self.selected_scan_id:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            initialfile=f"wifi_audit_scan_{self.selected_scan_id}.json"
        )
        if file_path:
            success = self.controller.export_scan_json(self.selected_scan_id, file_path)
            if success:
                messagebox.showinfo("Export Successful", f"Scan details successfully saved to:\n{file_path}")
            else:
                messagebox.showerror("Export Failed", "Could not export scan. Database or write error.")

    def _export_pdf(self):
        if not self.selected_scan_id:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")],
            initialfile=f"wifi_audit_report_{self.selected_scan_id}.pdf"
        )
        if file_path:
            success = self.controller.export_scan_pdf(self.selected_scan_id, file_path)
            if success:
                messagebox.showinfo("Report Generated", f"PDF report successfully saved to:\n{file_path}")
            else:
                messagebox.showerror("PDF Generation Failed", "Failed to compile reportlab PDF.")

    def _compare_scans(self):
        base_str = self.drop_base_var.get()
        target_str = self.drop_target_var.get()
        
        if "Select" in base_str or "Select" in target_str:
            messagebox.showwarning("Incomplete Selection", "Please choose both a baseline scan and a target scan to run the comparison.")
            return

        try:
            # Parse scan IDs from strings like "Scan #5 (2026-08-02 ...)"
            base_id = int(base_str.split(" ")[0].replace("Scan", "").replace("#", ""))
            target_id = int(target_str.split(" ")[0].replace("Scan", "").replace("#", ""))
        except Exception:
            messagebox.showerror("Parsing Error", "Could not resolve the selected Scan IDs.")
            return

        comparison = self.controller.compare_scans(base_id, target_id)
        if not comparison:
            messagebox.showerror("Data Error", "Could not load scan data for comparison.")
            return

        # Format report
        report = []
        report.append(f"=== AUDIT COMPARISON: #{base_id} VS #{target_id} ===")
        report.append(f"Baseline Scan #{base_id}: {comparison['scan_1']['timestamp']}")
        report.append(f"Target Scan #{target_id}: {comparison['scan_2']['timestamp']}")
        report.append("-" * 35)
        
        # Score difference
        diff = comparison["avg_score_diff"]
        diff_str = f"+{diff:.1f}" if diff >= 0 else f"{diff:.1f}"
        report.append(f"Average Security Score Change: {diff_str}")
        report.append(f"Net Access Points Change: {comparison['scan_2']['network_count'] - comparison['scan_1']['network_count']} APs")
        report.append(f"  └─ Added: {comparison['added_count']} APs | Removed: {comparison['removed_count']} APs")
        
        # Change Details
        if comparison["changed"]:
            report.append("\n[Security Protocol Modifications]")
            for c in comparison["changed"]:
                report.append(
                    f"• {c['ssid']} ({c['bssid']}):\n"
                    f"  Old Security: {c['old_security']} (Score: {c['old_score']})\n"
                    f"  New Security: {c['new_security']} (Score: {c['new_score']})"
                )
                
        # Highlight potential rogue additions
        rogues = [n for n in comparison["added"] if "OPEN" in n["security_type"].upper() or "WEP" in n["security_type"].upper()]
        if rogues:
            report.append("\n[🚨 Rogue/Weak AP Additions!]")
            for r in rogues:
                report.append(f"• SSID: {r['ssid']} | BSSID: {r['bssid']} ({r['security_type']})")
                
        # Display report in text box
        self.compare_results_box.configure(state="normal")
        self.compare_results_box.delete("1.0", "end")
        self.compare_results_box.insert("1.0", "\n".join(report))
        self.compare_results_box.configure(state="disabled")

    def on_tab_active(self):
        """Refreshes records from the controller on activation."""
        self.controller.load_history()
