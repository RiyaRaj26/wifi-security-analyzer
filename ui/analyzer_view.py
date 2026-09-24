import customtkinter as ctk
import tkinter as tk
from ui.theme import *

class AnalyzerView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        
        self.selected_network = None
        self._setup_ui()

    def _setup_ui(self):
        # Header
        self.header_lbl = ctk.CTkLabel(self, text="Security Analyzer", font=FONT_TITLE, text_color=COLOR_TEXT)
        self.header_lbl.pack(anchor="w", pady=(0, 15))

        # Main Split Layout (Left: Network Details & Score, Right: Risks & Mitigations)
        self.main_split = ctk.CTkFrame(self, fg_color="transparent")
        self.main_split.pack(fill="both", expand=True)

        # Left Column (Score Card & Details Card)
        self.left_col = ctk.CTkFrame(self.main_split, fg_color="transparent", width=350)
        self.left_col.pack(side="left", fill="both", padx=(0, 10))

        # Right Column (Vulnerabilities List)
        self.right_col = ctk.CTkFrame(self.main_split, fg_color="transparent")
        self.right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # --- LEFT COLUMN COMPONENTS ---
        # 1. Circular Score Gauge Card
        self.score_card = StyledCard(self.left_col)
        self.score_card.pack(fill="x", pady=(0, 15), ipady=15)
        
        self.score_title = ctk.CTkLabel(self.score_card, text="Security Score", font=FONT_SECTION, text_color=COLOR_TEXT_MUTED)
        self.score_title.pack(pady=(10, 5))
        
        # Canvas for Circular Gauge
        self.canvas_size = 140
        self.canvas = tk.Canvas(
            self.score_card, 
            width=self.canvas_size, 
            height=self.canvas_size, 
            bg=BG_CARD, 
            highlightthickness=0
        )
        self.canvas.pack(pady=10)
        self._draw_placeholder_gauge()

        # 2. Network Details Card
        self.details_card = StyledCard(self.left_col)
        self.details_card.pack(fill="both", expand=True)

        self.details_title = ctk.CTkLabel(self.details_card, text="Access Point Information", font=FONT_SECTION, text_color=COLOR_TEXT_MUTED)
        self.details_title.pack(pady=(12, 10), padx=15, anchor="w")

        # Labels for details
        self.detail_labels = {}
        detail_fields = [
            ("ssid", "SSID:"),
            ("bssid", "BSSID:"),
            ("rssi", "Signal strength:"),
            ("channel", "Channel:"),
            ("frequency", "Frequency:"),
            ("security", "Security Protocol:"),
            ("encryption", "Encryption Cipher:")
        ]
        
        for key, display in detail_fields:
            row = ctk.CTkFrame(self.details_card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=4)
            
            lbl_title = ctk.CTkLabel(row, text=display, font=FONT_BODY_BOLD, text_color=COLOR_TEXT_MUTED)
            lbl_title.pack(side="left")
            
            lbl_val = ctk.CTkLabel(row, text="N/A", font=FONT_BODY, text_color=COLOR_TEXT)
            lbl_val.pack(side="right")
            
            self.detail_labels[key] = lbl_val

        # --- RIGHT COLUMN COMPONENTS ---
        # 1. Risks Checklist
        self.risks_card = StyledCard(self.right_col)
        self.risks_card.pack(fill="both", expand=True)

        self.risks_title_lbl = ctk.CTkLabel(
            self.risks_card, 
            text="Vulnerabilities & Threat Risks", 
            font=FONT_SECTION, 
            text_color=COLOR_TEXT
        )
        self.risks_title_lbl.pack(pady=(12, 5), padx=15, anchor="w")

        self.risks_scroll = ctk.CTkScrollableFrame(self.risks_card, fg_color="transparent")
        self.risks_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Pre-select placeholder
        self.show_no_selection_placeholder()

    def show_no_selection_placeholder(self):
        # Clear right column
        for child in self.risks_scroll.winfo_children():
            child.destroy()
            
        self.placeholder_lbl = ctk.CTkLabel(
            self.risks_scroll,
            text="⚠️ No Network Selected\n\nGo to the 'Network Scan' tab and double-click\nany Wi-Fi network to run a security audit.",
            font=FONT_SECTION,
            text_color=COLOR_TEXT_MUTED,
            justify="center"
        )
        self.placeholder_lbl.pack(pady=100)

    def _draw_placeholder_gauge(self):
        self.canvas.delete("all")
        # Draw basic circular path
        padding = 10
        width = 12
        r = (self.canvas_size - 2 * padding) / 2
        cx, cy = self.canvas_size / 2, self.canvas_size / 2
        
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r, 
            outline="#1E293B", width=width
        )
        self.canvas.create_text(
            cx, cy, 
            text="--", font=("Segoe UI", 24, "bold"), 
            fill=COLOR_TEXT_MUTED
        )

    def draw_score_gauge(self, score: int):
        self.canvas.delete("all")
        
        padding = 10
        width = 12
        r = (self.canvas_size - 2 * padding) / 2
        cx, cy = self.canvas_size / 2, self.canvas_size / 2
        
        # Color based on score
        if score >= 80:
            score_color = COLOR_SAFE
        elif score >= 50:
            score_color = COLOR_WARN
        else:
            score_color = COLOR_DANGER
            
        # Draw background circle
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r, 
            outline="#1E293B", width=width
        )
        
        # Draw score arc
        # Tkinter arc extends counter-clockwise. Start is in degrees (0 is right, 90 is top, 180 left, 270 bottom).
        # We start at 90 degrees (top) and go clockwise (negative angle).
        extent = -int((score / 100) * 360)
        self.canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=90, extent=extent,
            outline=score_color, width=width, style="arc",
            extent_type="arc" if hasattr(self.canvas, "extent_type") else None
        )
        
        # Draw score text
        self.canvas.create_text(
            cx, cy, 
            text=f"{score}%", font=("Segoe UI", 24, "bold"), 
            fill=COLOR_TEXT
        )

    def set_network_analysis(self, network: dict):
        self.selected_network = network
        
        # 1. Update left column details
        self.detail_labels["ssid"].configure(text=network["ssid"])
        self.detail_labels["bssid"].configure(text=network["bssid"])
        self.detail_labels["rssi"].configure(text=f"{network['rssi']} dBm ({network['quality']}% quality)")
        self.placeholder_icon = "📶"
        
        self.detail_labels["channel"].configure(text=str(network["channel"]))
        self.detail_labels["frequency"].configure(text=f"{network['frequency']} MHz")
        self.detail_labels["security"].configure(text=network["security_type"])
        self.detail_labels["encryption"].configure(text=network["encryption"])

        # 2. Draw score gauge
        score = network["security_score"]
        self.draw_score_gauge(score)

        # 3. Clear risks list
        for child in self.risks_scroll.winfo_children():
            child.destroy()

        risks = network.get("risks", [])
        if not risks:
            # Safe network alert
            safe_frame = ctk.CTkFrame(self.risks_scroll, fg_color="#064E3B", border_color="#059669", border_width=1, corner_radius=8)
            safe_frame.pack(fill="x", pady=10, ipady=10, padx=5)
            
            lbl = ctk.CTkLabel(
                safe_frame,
                text="🛡️ No Vulnerabilities Detected\n\nThis network uses modern encryption protocols (WPA2/WPA3) and does not show typical rogue indicators. Connection security is excellent.",
                font=FONT_BODY,
                text_color="#A7F3D0",
                justify="center"
            )
            lbl.pack(fill="x", padx=15, pady=10)
            return

        # Render list of risks
        for r in risks:
            r_level = r["level"]
            
            # Select level badge color
            if r_level == "Critical":
                badge_bg = "#7F1D1D" # dark red
                badge_fg = "#FEE2E2" # light red
            elif r_level == "High":
                badge_bg = "#7C2D12" # dark orange
                badge_fg = "#FFEDD5" # light orange
            elif r_level == "Medium":
                badge_bg = "#78350F" # dark amber
                badge_fg = "#FEF3C7" # light amber
            else:
                badge_bg = "#334155" # slate
                badge_fg = "#F1F5F9" # light slate

            risk_card = ctk.CTkFrame(
                self.risks_scroll,
                fg_color=BG_CARD,
                border_color="#1E293B",
                border_width=1,
                corner_radius=8
            )
            risk_card.pack(fill="x", pady=6, ipady=8, padx=5)

            # Title block with badge
            title_row = ctk.CTkFrame(risk_card, fg_color="transparent")
            title_row.pack(fill="x", padx=15, pady=(5, 8))
            
            lbl_title = ctk.CTkLabel(
                title_row, 
                text=r["name"], 
                font=FONT_BODY_BOLD, 
                text_color=COLOR_TEXT
            )
            lbl_title.pack(side="left")
            
            lbl_badge = ctk.CTkLabel(
                title_row,
                text=f" {r_level.upper()} RISK ",
                font=FONT_SMALL,
                text_color=badge_fg,
                fg_color=badge_bg,
                corner_radius=4
            )
            lbl_badge.pack(side="right")

            # Explanation
            lbl_exp_title = ctk.CTkLabel(risk_card, text="What this means:", font=FONT_SMALL, text_color=COLOR_TEXT_MUTED)
            lbl_exp_title.pack(anchor="w", padx=15)
            
            lbl_exp = ctk.CTkLabel(
                risk_card, 
                text=r["explanation"], 
                font=FONT_SMALL, 
                text_color=COLOR_TEXT, 
                wraplength=500,
                justify="left"
            )
            lbl_exp.pack(anchor="w", padx=15, pady=(0, 8))

            # Mitigation
            lbl_mit_title = ctk.CTkLabel(risk_card, text="How to mitigate:", font=FONT_SMALL, text_color=COLOR_PRIMARY)
            lbl_mit_title.pack(anchor="w", padx=15)
            
            lbl_mit = ctk.CTkLabel(
                risk_card, 
                text=r["mitigation"], 
                font=FONT_SMALL, 
                text_color=COLOR_TEXT, 
                wraplength=500,
                justify="left"
            )
            lbl_mit.pack(anchor="w", padx=15, pady=(0, 5))

    def on_tab_active(self):
        """Called automatically when switching to this tab."""
        # If there is a selected network, update details. Otherwise show placeholder.
        if self.selected_network:
            self.set_network_analysis(self.selected_network)
        else:
            self.show_no_selection_placeholder()
