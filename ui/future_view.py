import customtkinter as ctk
import tkinter as tk
import random
import math
from ui.theme import *

class FutureView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Header
        self.header_lbl = ctk.CTkLabel(self, text="Concept Labs (Future Roadmap)", font=FONT_TITLE, text_color=COLOR_TEXT)
        self.header_lbl.pack(anchor="w", pady=(0, 10))
        
        self.desc_lbl = ctk.CTkLabel(
            self, 
            text="Explore conceptual and upcoming diagnostic capabilities designed for the Wi-Fi Security Analyzer suite. "
                 "These modules operate in simulation mode.",
            font=FONT_BODY,
            text_color=COLOR_TEXT_MUTED,
            justify="left",
            wraplength=900
        )
        self.desc_lbl.pack(anchor="w", pady=(0, 15))

        # Horizontal Tab Menu inside Concept Labs
        self.tab_menu = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, height=35, corner_radius=6)
        self.tab_menu.pack(fill="x", pady=(0, 15))
        
        self.lab_tabs = ["Speed Test", "Live Signal", "RF Heatmap", "Advisor Chat", "Router Audit"]
        self.tab_buttons = {}
        self.active_lab_tab = "Speed Test"
        
        for tab in self.lab_tabs:
            btn = ctk.CTkButton(
                self.tab_menu,
                text=tab,
                font=FONT_BODY_BOLD,
                fg_color="transparent",
                text_color=COLOR_TEXT_MUTED,
                hover_color="#1E293B",
                width=120,
                corner_radius=6,
                command=lambda t=tab: self.switch_lab_tab(t)
            )
            btn.pack(side="left", padx=5, pady=3, fill="y")
            self.tab_buttons[tab] = btn

        # Container for Concept panels
        self.panel_container = ctk.CTkFrame(self, fg_color="transparent")
        self.panel_container.pack(fill="both", expand=True)

        # Initialize the tab layouts
        self._init_speed_test_layout()
        self._init_live_signal_layout()
        self._init_heatmap_layout()
        self._init_chat_layout()
        self._init_router_audit_layout()
        
        # Open default tab
        self.switch_lab_tab("Speed Test")

    def switch_lab_tab(self, name: str):
        # Stop any animations if moving away
        if self.active_lab_tab == "Live Signal":
            self.stop_signal_anim()
        
        self.active_lab_tab = name
        
        # Color highlight
        for tab_name, btn in self.tab_buttons.items():
            if tab_name == name:
                btn.configure(fg_color=COLOR_PRIMARY, text_color=COLOR_TEXT)
            else:
                btn.configure(fg_color="transparent", text_color=COLOR_TEXT_MUTED)
                
        # Hide all panel containers
        self.speed_pane.pack_forget()
        self.signal_pane.pack_forget()
        self.heatmap_pane.pack_forget()
        self.chat_pane.pack_forget()
        self.router_pane.pack_forget()

        # Show selected pane
        if name == "Speed Test":
            self.speed_pane.pack(fill="both", expand=True)
        elif name == "Live Signal":
            self.signal_pane.pack(fill="both", expand=True)
            self.start_signal_anim()
        elif name == "RF Heatmap":
            self.heatmap_pane.pack(fill="both", expand=True)
        elif name == "Advisor Chat":
            self.chat_pane.pack(fill="both", expand=True)
        elif name == "Router Audit":
            self.router_pane.pack(fill="both", expand=True)

    # --- 1. SPEED TEST SIMULATOR ---
    def _init_speed_test_layout(self):
        self.speed_pane = StyledCard(self.panel_container)
        
        # Inner grid layout
        grid = ctk.CTkFrame(self.speed_pane, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left side: Meter gauge (Canvas)
        left = ctk.CTkFrame(grid, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)
        
        self.speed_canvas = tk.Canvas(left, width=220, height=220, bg=BG_CARD, highlightthickness=0)
        self.speed_canvas.pack(pady=10)
        self.draw_speed_gauge(0)
        
        self.btn_start_speed = ctk.CTkButton(
            left, text="Start speed test", font=FONT_BODY_BOLD,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_HOVER,
            command=self.run_speed_test
        )
        self.btn_start_speed.pack(pady=10)

        # Right side: Numeric readouts
        right = ctk.CTkFrame(grid, fg_color="transparent", width=250)
        right.pack(side="right", fill="y", padx=20)
        
        # Stats labels
        self.ping_lbl = self._create_speed_stat(right, "🏓 PING", "0 ms")
        self.download_lbl = self._create_speed_stat(right, "⬇️ DOWNLOAD", "0.00 Mbps")
        self.upload_lbl = self._create_speed_stat(right, "⬆️ UPLOAD", "0.00 Mbps")
        
        # Disclaimer
        disc = ctk.CTkLabel(
            right, text="* Simulation relies on mock sockets to outline upcoming speed-check features.",
            font=FONT_SMALL, text_color=COLOR_TEXT_MUTED, wraplength=220, justify="left"
        )
        disc.pack(side="bottom", pady=10)

        # Animation states
        self.speed_testing = False

    def _create_speed_stat(self, parent, title, val):
        f = ctk.CTkFrame(parent, fg_color=BG_MAIN, corner_radius=6, border_color="#1E293B", border_width=1)
        f.pack(fill="x", pady=5, ipady=5)
        t_lbl = ctk.CTkLabel(f, text=title, font=FONT_SMALL, text_color=COLOR_TEXT_MUTED)
        t_lbl.pack(anchor="w", padx=15, pady=(2, 0))
        v_lbl = ctk.CTkLabel(f, text=val, font=("Segoe UI", 16, "bold"), text_color=COLOR_TEXT)
        v_lbl.pack(anchor="w", padx=15, pady=(0, 2))
        return v_lbl

    def draw_speed_gauge(self, speed_mbps: float, max_speed: float = 100.0):
        self.speed_canvas.delete("all")
        cx, cy = 110, 110
        r = 85
        width = 12
        
        # Background arc (180 deg, from 180 to 0)
        self.speed_canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=180, extent=-180,
            outline="#1E293B", width=width, style="arc"
        )
        
        # Fill arc based on speed percentage
        pct = min(speed_mbps / max_speed, 1.0)
        extent = -180 * pct
        
        # Dial color based on speed
        if pct < 0.3:
            color = COLOR_DANGER
        elif pct < 0.7:
            color = COLOR_WARN
        else:
            color = COLOR_SAFE
            
        self.speed_canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=180, extent=extent,
            outline=color, width=width, style="arc"
        )
        
        # Value Text
        self.speed_canvas.create_text(
            cx, cy + 20,
            text=f"{speed_mbps:.1f}", font=("Segoe UI", 28, "bold"),
            fill=COLOR_TEXT
        )
        self.speed_canvas.create_text(
            cx, cy + 45,
            text="Mbps", font=FONT_SMALL,
            fill=COLOR_TEXT_MUTED
        )
        
        # Draw needle
        angle_rad = math.radians(180 - (pct * 180))
        nx = cx + (r - 15) * math.cos(angle_rad)
        ny = cy - (r - 15) * math.sin(angle_rad)
        self.speed_canvas.create_line(
            cx, cy + 10, nx, ny,
            fill=COLOR_PRIMARY, width=3, arrow="last"
        )
        self.speed_canvas.create_oval(
            cx - 6, cy + 4, cx + 6, cy + 16,
            fill=COLOR_PRIMARY, outline=COLOR_TEXT
        )

    def run_speed_test(self):
        if self.speed_testing:
            return
        
        self.speed_testing = True
        self.btn_start_speed.configure(state="disabled")
        
        # Reset labels
        self.ping_lbl.configure(text="Testing...")
        self.download_lbl.configure(text="0.00 Mbps")
        self.upload_lbl.configure(text="0.00 Mbps")

        # Step 1: Ping animation
        def test_ping(step=0):
            if step < 10:
                p = random.randint(10, 60)
                self.ping_lbl.configure(text=f"{p} ms")
                self.after(80, lambda: test_ping(step + 1))
            else:
                final_ping = random.randint(12, 28)
                self.ping_lbl.configure(text=f"{final_ping} ms")
                self.after(200, test_download)
                
        # Step 2: Download speed animation
        def test_download(step=0, val=0.0):
            if step < 25:
                # Target download speed is ~68 Mbps
                target = 68.4
                val += (target - val) * 0.15 + random.uniform(-3, 3)
                val = max(0, val)
                self.download_lbl.configure(text=f"{val:.2f} Mbps")
                self.draw_speed_gauge(val)
                self.after(80, lambda: test_download(step + 1, val))
            else:
                self.download_lbl.configure(text="68.45 Mbps")
                self.draw_speed_gauge(68.45)
                self.after(200, test_upload)

        # Step 3: Upload speed animation
        def test_upload(step=0, val=0.0):
            if step < 25:
                target = 22.8
                val += (target - val) * 0.15 + random.uniform(-1, 1)
                val = max(0, val)
                self.upload_lbl.configure(text=f"{val:.2f} Mbps")
                self.draw_speed_gauge(val)
                self.after(80, lambda: test_upload(step + 1, val))
            else:
                self.upload_lbl.configure(text="22.78 Mbps")
                self.draw_speed_gauge(0.0) # Reset meter
                self.btn_start_speed.configure(state="normal")
                self.speed_testing = False

        test_ping()

    # --- 2. LIVE SIGNAL WAVE GRAPH ---
    def _init_live_signal_layout(self):
        self.signal_pane = StyledCard(self.panel_container)
        
        header = ctk.CTkFrame(self.signal_pane, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        
        lbl = ctk.CTkLabel(header, text="Simulated Real-Time RSSI Tracking", font=FONT_SECTION, text_color=COLOR_TEXT)
        lbl.pack(side="left")
        
        # Legend/Color reference
        l_row = ctk.CTkFrame(header, fg_color="transparent")
        l_row.pack(side="right")
        for text, color in [("Good (> -60dBm)", COLOR_SAFE), ("Moderate (-75dBm)", COLOR_WARN), ("Poor (< -85dBm)", COLOR_DANGER)]:
            b = ctk.CTkLabel(l_row, text=f"• {text}", font=FONT_SMALL, text_color=color)
            b.pack(side="left", padx=10)

        # Canvas for drawing the wave
        self.sig_canvas = tk.Canvas(self.signal_pane, bg=BG_MAIN, highlightthickness=0, height=220)
        self.sig_canvas.pack(fill="both", expand=True, padx=15, pady=10)

        self.signal_points = [random.randint(-75, -55) for _ in range(70)]
        self.anim_running = False

    def start_signal_anim(self):
        self.anim_running = True
        self.update_signal_graph()

    def stop_signal_anim(self):
        self.anim_running = False

    def update_signal_graph(self):
        if not self.anim_running:
            return

        # Add new point, remove oldest
        # Simulate slight random walk in signal
        last = self.signal_points[-1]
        new_val = last + random.randint(-4, 4)
        new_val = min(max(new_val, -95), -35) # clip between -95 and -35
        self.signal_points.append(new_val)
        self.signal_points.pop(0)

        # Redraw canvas
        self.sig_canvas.delete("all")
        
        w = self.sig_canvas.winfo_width()
        h = self.sig_canvas.winfo_height()
        if w < 50: w = 600
        if h < 50: h = 200

        # Draw grid lines
        for dbm in [-40, -60, -80]:
            # Convert dbm (-100 to -30) to Y coordinate
            # Y = (dbm - (-100)) / (70) * (height)
            y = h - int(((dbm + 100) / 70) * (h - 40)) - 20
            self.sig_canvas.create_line(0, y, w, y, fill="#1E293B", dash=(4, 4))
            self.sig_canvas.create_text(25, y - 8, text=f"{dbm} dBm", fill=COLOR_TEXT_MUTED, font=FONT_SMALL)

        # Plot points as connected line segments
        points_count = len(self.signal_points)
        x_step = w / (points_count - 1)
        
        for i in range(points_count - 1):
            dbm1 = self.signal_points[i]
            dbm2 = self.signal_points[i+1]
            
            x1 = i * x_step
            y1 = h - int(((dbm1 + 100) / 70) * (h - 40)) - 20
            
            x2 = (i + 1) * x_step
            y2 = h - int(((dbm2 + 100) / 70) * (h - 40)) - 20
            
            # Line segment color depending on signal strength
            avg_dbm = (dbm1 + dbm2) / 2
            if avg_dbm >= -60:
                color = COLOR_SAFE
            elif avg_dbm >= -80:
                color = COLOR_WARN
            else:
                color = COLOR_DANGER
                
            self.sig_canvas.create_line(x1, y1, x2, y2, fill=color, width=2)
            
            # Glow effect under the line
            self.sig_canvas.create_polygon(
                x1, y1, x2, y2, x2, h, x1, h,
                fill=color, stipple="gray12" if hasattr(self.sig_canvas, "stipple") else "",
                outline=""
            )

        # Loop animation after 100ms
        self.after(100, self.update_signal_graph)

    # --- 3. RF HEATMAP GENERATOR ---
    def _init_heatmap_layout(self):
        self.heatmap_pane = StyledCard(self.panel_container)
        
        header = ctk.CTkFrame(self.heatmap_pane, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        
        lbl = ctk.CTkLabel(header, text="Simulated Building Wi-Fi Coverage Heatmap", font=FONT_SECTION, text_color=COLOR_TEXT)
        lbl.pack(side="left")
        
        btn_reset = ctk.CTkButton(
            header, text="Re-map RF", font=FONT_SMALL,
            fg_color="transparent", border_color=COLOR_PRIMARY, border_width=1,
            text_color=COLOR_PRIMARY, hover_color="#1E293B", width=90,
            command=self.reset_heatmap
        )
        btn_reset.pack(side="right")

        # Layout Split: Grid mapping vs legend details
        body = ctk.CTkFrame(self.heatmap_pane, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.heatmap_grid_frame = ctk.CTkFrame(body, fg_color=BG_MAIN, border_color="#1E293B", border_width=1, corner_radius=8)
        self.heatmap_grid_frame.pack(side="left", fill="both", expand=True, pady=5)

        # Info side bar
        info_sidebar = ctk.CTkFrame(body, fg_color="transparent", width=220)
        info_sidebar.pack(side="right", fill="y", padx=(15, 0))
        
        self.heat_details_lbl = ctk.CTkLabel(
            info_sidebar, 
            text="🏠 **Grid Diagnostic**\n\nClick any sector of the floor plan grid to measure local RSSI values and detect dead zones.",
            font=FONT_BODY, text_color=COLOR_TEXT, justify="left", wraplength=200
        )
        self.heat_details_lbl.pack(anchor="w", pady=10)

        # Build grid coordinates (6 rows x 10 cols)
        self.grid_squares = {}
        self.reset_heatmap()

    def reset_heatmap(self):
        # Clear grid frame
        for child in self.heatmap_grid_frame.winfo_children():
            child.destroy()
            
        rows, cols = 6, 8
        # Define router sources to calculate signal attenuation
        routers = [
            {"row": 1, "col": 2, "ssid": "Office_Router", "power": 85},
            {"row": 4, "col": 6, "ssid": "Guest_Extender", "power": 70}
        ]
        
        # Render grid buttons
        for r in range(rows):
            self.heatmap_grid_frame.rowconfigure(r, weight=1)
            for c in range(cols):
                self.heatmap_grid_frame.columnconfigure(c, weight=1)
                
                # Calculate aggregate signal based on distance to routers
                max_signal = -100
                closest_ap = "None"
                for ap in routers:
                    dist = math.sqrt((r - ap["row"])**2 + (c - ap["col"])**2)
                    sig = int(ap["power"] - (dist * 12) + random.randint(-4, 4)) # attenuation
                    sig = min(max(sig, -95), -35)
                    if sig > max_signal:
                        max_signal = sig
                        closest_ap = ap["ssid"]

                # Color square
                if max_signal >= -55:
                    color = "#064E3B" # Safe/Strong green
                    fg = "#34D399"
                elif max_signal >= -75:
                    color = "#78350F" # Medium/Orange
                    fg = "#FBBF24"
                else:
                    color = "#7F1D1D" # Dead zone/Red
                    fg = "#F87171"

                # If AP center, label it
                btn_txt = ""
                for ap in routers:
                    if ap["row"] == r and ap["col"] == c:
                        btn_txt = "📶 AP"
                        
                btn = ctk.CTkButton(
                    self.heatmap_grid_frame,
                    text=btn_txt,
                    font=("Segoe UI", 9, "bold"),
                    fg_color=color,
                    hover_color=COLOR_HOVER,
                    corner_radius=4,
                    border_color="#1E293B",
                    border_width=1,
                    text_color=fg,
                    command=lambda row=r, col=c, s=max_signal, ap=closest_ap: self.click_heatmap_square(row, col, s, ap)
                )
                btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")

    def click_heatmap_square(self, r, c, sig, ap):
        quality = min(max(2 * (sig + 100), 0), 100)
        self.heat_details_lbl.configure(
            text=f"📍 **Sector ({r}, {c})**\n\n"
                 f"• **Primary AP:** {ap}\n"
                 f"• **Signal RSSI:** {sig} dBm\n"
                 f"• **Signal Quality:** {quality}%\n"
                 f"• **Interference:** {'Low' if quality > 75 else 'Moderate' if quality > 50 else 'High (Dead Zone)'}\n\n"
                 f"**Suggestion:** {'Optimal zone' if quality > 75 else 'Relocate AP closer' if quality < 50 else 'Check adjacent channels'}"
        )

    # --- 4. AI SECURITY ADVISOR CHATBOT ---
    def _init_chat_layout(self):
        self.chat_pane = StyledCard(self.panel_container)
        
        # Chat area layout
        chat_box_frame = ctk.CTkFrame(self.chat_pane, fg_color="transparent")
        chat_box_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Message scroll log
        self.chat_log = ctk.CTkTextbox(
            chat_box_frame, 
            fg_color=BG_MAIN, 
            border_color="#1E293B", 
            border_width=1,
            font=FONT_BODY,
            wrap="word"
        )
        self.chat_log.pack(fill="both", expand=True, pady=(0, 10))
        
        self.chat_log.insert("end", "🛡️ **Wi-Fi Security Advisor Bot**\nAsk me defensive questions about encryption standard weaknesses, WPA configurations, Evil Twin detection, or VPN requirements.\n\n")
        self.chat_log.configure(state="disabled")

        # Bottom Input row
        input_row = ctk.CTkFrame(chat_box_frame, fg_color="transparent")
        input_row.pack(fill="x")
        
        self.chat_input = ctk.CTkEntry(
            input_row, 
            placeholder_text="Ask about Wi-Fi security (e.g., 'What is WPA3?', 'How does WEP crack?', 'Explain Evil Twin')...",
            fg_color=BG_MAIN,
            border_color="#1E293B",
            font=FONT_BODY
        )
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.chat_input.bind("<Return>", lambda e: self.send_chat_message())

        btn_send = ctk.CTkButton(
            input_row, text="Send", font=FONT_BODY_BOLD,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_HOVER, width=80,
            command=self.send_chat_message()
        )
        btn_send.pack(side="right")

    def send_chat_message(self):
        msg = self.chat_input.get().strip()
        if not msg:
            return
            
        self.chat_input.delete(0, "end")
        
        self.chat_log.configure(state="normal")
        self.chat_log.insert("end", f"👤 **You:** {msg}\n\n")
        
        # Generate smart defensive response
        response = self.get_bot_response(msg)
        self.chat_log.insert("end", f"🛡️ **Advisor:** {response}\n\n")
        self.chat_log.configure(state="disabled")
        self.chat_log.see("end")

    def get_bot_response(self, text: str) -> str:
        t = text.lower()
        if "wpa3" in t:
            return "WPA3 implements SAE (Simultaneous Authentication of Equals) to replace the pre-shared key exchange in WPA2. This makes it immune to offline dictionary hacking attacks and supports individualized data encryption on open connections."
        elif "wpa2" in t:
            return "WPA2 uses AES/CCMP block ciphers and is highly secure if configured with a long, randomized password (14+ characters). Its main vulnerability is that attackers can sniff the four-way handshake and attempt to crack the key offline."
        elif "wep" in t or "crack" in t:
            return "WEP uses weak static RC4 keys that recycle initialization vectors too frequently. Tools like aircrack-ng gather statistical packets and decrypt WEP passwords in seconds. Avoid WEP completely!"
        elif "twin" in t or "rogue" in t:
            return "An Evil Twin is a rogue AP broadcasting the same SSID name as a real network. Attackers configure it with high signal power or duplicate captive portals to intercept credentials. Always run a VPN to secure yourself."
        elif "vpn" in t:
            return "A Virtual Private Network (VPN) creates an encrypted tunnel between your device and a secure server, protecting HTTP headers, DNS requests, and packet contents from local packet sniffer interception on unencrypted Wi-Fi."
        elif "hello" in t or "hi" in t:
            return "Hello! I am your Wi-Fi Security Advisor. Ask me anything about securing your router, VPNs, or interpreting risk scores."
        else:
            return "I am an offline rule-based knowledge bot. To learn more, check the 'Awareness Hub' page, which details WPA standards, public Wi-Fi safety, and Evil Twin preventions."

    # --- 5. ROUTER AUDIT CHECKER ---
    def _init_router_audit_layout(self):
        self.router_pane = StyledCard(self.panel_container)
        
        body = ctk.CTkFrame(self.router_pane, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=20)
        
        lbl_title = ctk.CTkLabel(body, text="Router Local Credential & DNS Health Auditor", font=FONT_SECTION, text_color=COLOR_TEXT)
        lbl_title.pack(anchor="w", pady=(0, 10))
        
        lbl_desc = ctk.CTkLabel(
            body,
            text="Scan local router gateway paths (e.g. 192.168.1.1) to test for common security vulnerabilities "
                 "such as default administrative password combinations (admin/admin), open ports (80/443, 23/Telnet), and DNS redirection leaks.",
            font=FONT_BODY, text_color=COLOR_TEXT_MUTED, justify="left", wraplength=550
        )
        lbl_desc.pack(anchor="w", pady=(0, 20))

        # Output box
        self.audit_textbox = ctk.CTkTextbox(
            body, fg_color=BG_MAIN, border_color="#1E293B", border_width=1,
            font=FONT_SMALL, height=120
        )
        self.audit_textbox.pack(fill="x", pady=10)
        self.audit_textbox.insert("1.0", "Auditor is idle. Press 'Run Router Scan' to query gateways.")
        self.audit_textbox.configure(state="disabled")

        self.btn_run_audit = ctk.CTkButton(
            body, text="Run Router Audit", font=FONT_BODY_BOLD,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_HOVER,
            command=self.run_router_audit
        )
        self.btn_run_audit.pack(anchor="w")

    def run_router_audit(self):
        self.btn_run_audit.configure(state="disabled")
        self.audit_textbox.configure(state="normal")
        self.audit_textbox.delete("1.0", "end")
        self.audit_textbox.insert("end", "[*] Initializing gateway locator...\n")
        
        # Step-by-step audit simulation
        def step1():
            self.audit_textbox.insert("end", "[+] Gateway identified: 192.168.1.1 (NETGEAR, Inc.)\n")
            self.audit_textbox.see("end")
            self.after(500, step2)

        def step2():
            self.audit_textbox.insert("end", "[*] Scanning open administration ports...\n")
            self.audit_textbox.insert("end", "    - Port 80 (HTTP): OPEN (Web GUI)\n")
            self.audit_textbox.insert("end", "    - Port 443 (HTTPS): CLOSED\n")
            self.audit_textbox.insert("end", "    - Port 23 (Telnet): CLOSED (No plain-text console expose)\n")
            self.audit_textbox.see("end")
            self.after(800, step3)

        def step3():
            self.audit_textbox.insert("end", "[*] Checking default credentials...\n")
            self.audit_textbox.insert("end", "    - admin : admin -> Access Denied (Safe)\n")
            self.audit_textbox.insert("end", "    - admin : password -> Access Denied (Safe)\n")
            self.audit_textbox.insert("end", "[+] Verification passed: Administrative console does not use trivial default passwords.\n")
            self.audit_textbox.see("end")
            self.after(600, step4)

        def step4():
            self.audit_textbox.insert("end", "[*] Querying DNS resolution targets...\n")
            self.audit_textbox.insert("end", "    - Current DNS Server: 1.1.1.1 (Cloudflare Secured DNS)\n")
            self.audit_textbox.insert("end", "    - Redirection Leaks: NONE\n")
            self.audit_textbox.insert("end", "\n[🛡️ RESULT]: Router health is safe. Admin interface is secure, ports are standard, and DNS queries are secure.\n")
            self.audit_textbox.configure(state="disabled")
            self.btn_run_audit.configure(state="normal")
            
        self.after(400, step1)
