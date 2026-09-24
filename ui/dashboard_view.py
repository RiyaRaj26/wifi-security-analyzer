import customtkinter as ctk
from ui.theme import *

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        
        # Current networks displayed
        self.current_networks = []
        
        # Sorting state: (sort_by_column, reverse_boolean)
        self.sort_state = ("rssi", True)
        
        self._setup_ui()

    def _setup_ui(self):
        # 1. Header Frame (Title + Top Stats)
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 15))
        
        self.title_lbl = ctk.CTkLabel(self.header_frame, text="Network Scanner", font=FONT_TITLE, text_color=COLOR_TEXT)
        self.title_lbl.pack(side="left")
        
        # Stats container
        self.stats_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.stats_frame.pack(side="right")
        
        self.net_count_lbl = ctk.CTkLabel(self.stats_frame, text="Networks: 0", font=FONT_BODY_BOLD, text_color=COLOR_PRIMARY)
        self.net_count_lbl.pack(side="left", padx=15)
        
        self.avg_score_lbl = ctk.CTkLabel(self.stats_frame, text="Avg Score: 0/100", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        self.avg_score_lbl.pack(side="left", padx=15)

        # 2. Controls Toolbar (Scan, Search, Filter)
        self.toolbar_card = StyledCard(self)
        self.toolbar_card.pack(fill="x", pady=(0, 15), ipady=5)
        
        # Scan and Refresh Buttons
        self.btn_scan = ctk.CTkButton(
            self.toolbar_card,
            text="⚡ Scan Networks",
            font=FONT_BODY_BOLD,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_HOVER,
            command=self.controller.trigger_scan
        )
        self.btn_scan.pack(side="left", padx=12, pady=10)
        
        self.btn_refresh = ctk.CTkButton(
            self.toolbar_card,
            text="🔄 Refresh",
            font=FONT_BODY_BOLD,
            fg_color="transparent",
            border_color=COLOR_PRIMARY,
            border_width=1,
            text_color=COLOR_PRIMARY,
            hover_color="#1E293B",
            width=100,
            command=self.controller.trigger_scan
        )
        self.btn_refresh.pack(side="left", padx=(0, 12), pady=10)
        
        # Search Entry
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.apply_filters_and_sorting())
        self.search_entry = ctk.CTkEntry(
            self.toolbar_card,
            placeholder_text="🔍 Search SSID or BSSID...",
            textvariable=self.search_var,
            width=250,
            fg_color=BG_MAIN,
            border_color="#1E293B"
        )
        self.search_entry.pack(side="left", padx=10, pady=10)
        
        # Security Filter Dropdown
        self.filter_var = ctk.StringVar(value="All Security Types")
        self.filter_menu = ctk.CTkOptionMenu(
            self.toolbar_card,
            values=["All Security Types", "WPA3 Only", "WPA2 Only", "WPA/WEP Only", "Open Only"],
            variable=self.filter_var,
            command=lambda v: self.apply_filters_and_sorting(),
            fg_color=BG_MAIN,
            button_color=COLOR_PRIMARY,
            button_hover_color=COLOR_HOVER,
            dropdown_fg_color=BG_CARD,
            dropdown_hover_color=COLOR_HOVER,
            text_color=COLOR_TEXT
        )
        self.filter_menu.pack(side="right", padx=12, pady=10)

        # 3. Scanning Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self, fg_color=BG_CARD, progress_color=COLOR_PRIMARY)
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(0)
        self.progress_bar.pack_forget() # Hide by default

        # 4. Table Header Frame (Interactive headers to allow sorting)
        self.table_header_frame = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, height=35, corner_radius=6)
        self.table_header_frame.pack(fill="x", pady=(0, 5))
        
        # Define table columns & headers: (column_id, display_label, relative_width)
        self.columns = [
            ("ssid", "SSID ↕", 0.28),
            ("bssid", "BSSID (MAC)", 0.18),
            ("rssi", "Signal ↕", 0.12),
            ("channel", "Ch ↕", 0.08),
            ("security_type", "Security ↕", 0.16),
            ("encryption", "Encryption", 0.10),
            ("security_score", "Score", 0.08)
        ]
        
        # Render Table Headers
        for col_id, label, width_pct in self.columns:
            btn = ctk.CTkButton(
                self.table_header_frame,
                text=label,
                font=FONT_BODY_BOLD,
                text_color=COLOR_TEXT_MUTED,
                fg_color="transparent",
                hover_color="#1E293B",
                corner_radius=0,
                anchor="w",
                command=lambda cid=col_id: self.header_click(cid)
            )
            # We use pack with relative widths inside a responsive layout
            btn.pack(side="left", fill="both", expand=True)

        # 5. Table Rows Scrollable Container
        self.table_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.table_scroll.pack(fill="both", expand=True)
        
        # Display initial placeholder
        self.placeholder_lbl = ctk.CTkLabel(
            self.table_scroll,
            text="No network data available. Click '⚡ Scan Networks' to search for access points.",
            font=FONT_BODY,
            text_color=COLOR_TEXT_MUTED
        )
        self.placeholder_lbl.pack(pady=100)

    def show_loading(self):
        self.btn_scan.configure(state="disabled")
        self.btn_refresh.configure(state="disabled")
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.start()

    def hide_loading(self):
        self.btn_scan.configure(state="enabled")
        self.btn_refresh.configure(state="enabled")
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

    def set_networks(self, networks: list[dict]):
        self.current_networks = networks
        self.apply_filters_and_sorting()
        
        # Update quick stats
        self.net_count_lbl.configure(text=f"Networks: {len(networks)}")
        if networks:
            avg = sum(n.get("security_score", 0) for n in networks) / len(networks)
            self.avg_score_lbl.configure(text=f"Avg Score: {avg:.1f}/100")
            if avg >= 80:
                self.avg_score_lbl.configure(text_color=COLOR_SAFE)
            elif avg >= 50:
                self.avg_score_lbl.configure(text_color=COLOR_WARN)
            else:
                self.avg_score_lbl.configure(text_color=COLOR_DANGER)
        else:
            self.avg_score_lbl.configure(text="Avg Score: N/A", text_color=COLOR_TEXT)

    def header_click(self, column_id: str):
        # Click toggle sorting direction or column
        current_col, is_reverse = self.sort_state
        if current_col == column_id:
            # Toggle reverse
            self.sort_state = (column_id, not is_reverse)
        else:
            # Set new sorting column
            # Numeric fields sort descending by default (RSSI, Channel, Score)
            # SSID sorts ascending by default
            default_reverse = column_id in ["rssi", "security_score", "channel"]
            self.sort_state = (column_id, default_reverse)
            
        self.apply_filters_and_sorting()

    def apply_filters_and_sorting(self):
        filtered = self.current_networks.copy()
        
        # Apply Search filter (SSID or BSSID)
        search_query = self.search_var.get().lower().strip()
        if search_query:
            filtered = [
                n for n in filtered 
                if search_query in n["ssid"].lower() or search_query in n["bssid"].lower()
            ]
            
        # Apply Dropdown security filter
        sec_filter = self.filter_var.get()
        if sec_filter == "WPA3 Only":
            filtered = [n for n in filtered if "WPA3" in n["security_type"].upper()]
        elif sec_filter == "WPA2 Only":
            filtered = [n for n in filtered if "WPA2" in n["security_type"].upper()]
        elif sec_filter == "WPA/WEP Only":
            filtered = [
                n for n in filtered 
                if any(x in n["security_type"].upper() for x in ["WPA-", "WEP"])
            ]
        elif sec_filter == "Open Only":
            filtered = [n for n in filtered if "OPEN" in n["security_type"].upper()]

        # Apply Sorting
        sort_col, reverse = self.sort_state
        
        # Sort helper
        def sort_key(net):
            val = net.get(sort_col)
            # Case insensitive sorting for strings
            if isinstance(val, str):
                return val.lower()
            return val if val is not None else 0

        filtered.sort(key=sort_key, reverse=reverse)
        self.render_rows(filtered)

    def render_rows(self, networks: list[dict]):
        # Clear scrollable frame contents
        for child in self.table_scroll.winfo_children():
            child.destroy()
            
        if not networks:
            self.placeholder_lbl = ctk.CTkLabel(
                self.table_scroll,
                text="No networks match current search or filters.",
                font=FONT_BODY,
                text_color=COLOR_TEXT_MUTED
            )
            self.placeholder_lbl.pack(pady=80)
            return

        for net in networks:
            # Create a row container
            row_frame = ctk.CTkFrame(
                self.table_scroll,
                fg_color=BG_CARD,
                border_color="#1E293B",
                border_width=1,
                corner_radius=6,
                height=45
            )
            row_frame.pack(fill="x", pady=4, ipady=3)
            row_frame.pack_propagate(False) # lock height

            # Double click row triggers detail analysis
            row_frame.bind("<Double-Button-1>", lambda e, n=net: self.controller.select_network_for_analysis(n))

            # Helper method to add labels
            # SSID
            ssid = net["ssid"]
            is_hidden = net.get("is_hidden", False)
            ssid_txt = f"{ssid} (Hidden)" if is_hidden else ssid
            ssid_color = COLOR_TEXT_MUTED if is_hidden else COLOR_TEXT
            
            lbl_ssid = ctk.CTkLabel(row_frame, text=ssid_txt, font=FONT_BODY_BOLD, text_color=ssid_color, anchor="w")
            lbl_ssid.pack(side="left", fill="both", expand=True, padx=(12, 5))
            lbl_ssid.bind("<Double-Button-1>", lambda e, n=net: self.controller.select_network_for_analysis(n))

            # BSSID
            lbl_bssid = ctk.CTkLabel(row_frame, text=net["bssid"], font=FONT_CODE, text_color=COLOR_TEXT_MUTED, anchor="w")
            lbl_bssid.pack(side="left", fill="both", expand=True, padx=5)
            
            # RSSI (Signal strength)
            rssi = net["rssi"]
            quality = net["quality"]
            # Choose signal icon based on quality
            if quality > 75:
                sig_icon = "📶"
            elif quality > 45:
                sig_icon = "📶"
            else:
                sig_icon = "📶"
            
            lbl_rssi = ctk.CTkLabel(row_frame, text=f"{sig_icon} {rssi} dBm ({quality}%)", font=FONT_BODY, text_color=COLOR_TEXT, anchor="w")
            lbl_rssi.pack(side="left", fill="both", expand=True, padx=5)

            # Channel
            lbl_ch = ctk.CTkLabel(row_frame, text=f"{net['channel']}", font=FONT_BODY, text_color=COLOR_TEXT, anchor="w")
            lbl_ch.pack(side="left", fill="both", expand=True, padx=5)

            # Security Type Badge
            sec_type = net["security_type"]
            badge_color = COLOR_MUTED
            if "WPA3" in sec_type:
                badge_color = COLOR_SAFE
            elif "WPA2" in sec_type:
                badge_color = COLOR_PRIMARY
            elif "WEP" in sec_type or "OPEN" in sec_type.upper():
                badge_color = COLOR_DANGER
            elif "WPA" in sec_type:
                badge_color = COLOR_WARN
                
            lbl_sec = ctk.CTkLabel(
                row_frame,
                text=sec_type,
                font=FONT_BODY_BOLD,
                text_color=badge_color,
                anchor="w"
            )
            lbl_sec.pack(side="left", fill="both", expand=True, padx=5)

            # Encryption
            lbl_enc = ctk.CTkLabel(row_frame, text=net["encryption"], font=FONT_SMALL, text_color=COLOR_TEXT_MUTED, anchor="w")
            lbl_enc.pack(side="left", fill="both", expand=True, padx=5)

            # Score
            score = net["security_score"]
            score_color = COLOR_SAFE
            if score < 50:
                score_color = COLOR_DANGER
            elif score < 80:
                score_color = COLOR_WARN
                
            lbl_score = ctk.CTkLabel(row_frame, text=f"{score}/100", font=FONT_BODY_BOLD, text_color=score_color, anchor="w")
            lbl_score.pack(side="left", fill="both", expand=True, padx=5)

            # Analyze Row Action Button
            btn_act = ctk.CTkButton(
                row_frame,
                text="Analyze",
                font=FONT_SMALL,
                fg_color="transparent",
                border_color=COLOR_PRIMARY,
                border_width=1,
                text_color=COLOR_PRIMARY,
                hover_color="#1E293B",
                width=65,
                height=26,
                command=lambda n=net: self.controller.select_network_for_analysis(n)
            )
            btn_act.pack(side="right", padx=(5, 12))
