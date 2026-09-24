import customtkinter as ctk
from ui.theme import *

class EducationView(ctk.CTkScrollableFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        # Header
        self.header_lbl = ctk.CTkLabel(self, text="Cybersecurity Awareness Hub", font=FONT_TITLE, text_color=COLOR_TEXT)
        self.header_lbl.pack(anchor="w", pady=(0, 20))

        # Introductions
        self.intro_lbl = ctk.CTkLabel(
            self,
            text="Welcome to the Wi-Fi Security Education Hub. This space contains defensive security material "
                 "and awareness guides to help you secure your own home or business network and protect yourself "
                 "when connecting to public access points.",
            font=FONT_BODY,
            text_color=COLOR_TEXT_MUTED,
            justify="left",
            wraplength=900
        )
        self.intro_lbl.pack(anchor="w", pady=(0, 20))

        # --- SECTION 1: Wi-Fi Protocols ---
        self.sec1_lbl = ctk.CTkLabel(self, text="1. Encryption Standards & Evolution", font=FONT_SECTION, text_color=COLOR_PRIMARY)
        self.sec1_lbl.pack(anchor="w", pady=(10, 10))

        self.cards_frame1 = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame1.pack(fill="x", pady=(0, 20))
        
        # WPA3 vs WPA2 vs WPA
        card_wpa3 = self._create_info_card(
            self.cards_frame1,
            "🛡️ WPA3 (Wi-Fi Protected Access 3)",
            "The current, state-of-the-art security standard introduced in 2018.",
            [
                "Key Benefit: Implements Simultaneous Authentication of Equals (SAE) handshake.",
                "Protection: Immunizes your network against offline dictionary attacks (brute forcing).",
                "Privacy: Uses Forward Secrecy to prevent older data from being decrypted even if the key is compromised.",
                "Recommendation: Always use WPA3 if your router and client devices support it."
            ],
            COLOR_SAFE
        )
        card_wpa3.pack(side="left", fill="both", expand=True, padx=(0, 10))

        card_wpa2 = self._create_info_card(
            self.cards_frame1,
            "🔑 WPA2 (Wi-Fi Protected Access 2)",
            "The most widely adopted security protocol since 2004.",
            [
                "Key Benefit: Uses AES (Advanced Encryption Standard) block ciphers.",
                "Protection: Good, but susceptible to offline WPA handshake capture (WPA handshakes can be sniffed and brute-forced).",
                "Weakness: Vulnerable to KRACK attacks (fixed in firmware patches).",
                "Recommendation: Good fallback. Ensure complex passwords (16+ chars) to prevent brute-forcing."
            ],
            COLOR_PRIMARY
        )
        card_wpa2.pack(side="left", fill="both", expand=True, padx=10)

        # WEP & TKIP
        card_legacy = self._create_info_card(
            self.cards_frame1,
            "⚠️ Legacy Vulnerabilities (WEP / WPA1)",
            "Outdated, broken, and deprecated standards from the early 2000s.",
            [
                "WEP Insecurity: Uses short static keys and weak RC4 encryption. Can be cracked in seconds.",
                "WPA1/TKIP: TKIP has cryptographic flaws that allow key manipulation and packet injection.",
                "Warning: Modern operating systems will warn you or outright refuse to connect to WEP/TKIP.",
                "Action: Upgrade router configurations immediately; replace ancient hardware."
            ],
            COLOR_DANGER
        )
        card_legacy.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # --- SECTION 2: Common Wi-Fi Threats ---
        self.sec2_lbl = ctk.CTkLabel(self, text="2. Local Wireless Threats Explained", font=FONT_SECTION, text_color=COLOR_PRIMARY)
        self.sec2_lbl.pack(anchor="w", pady=(10, 10))

        self.cards_frame2 = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame2.pack(fill="x", pady=(0, 20))

        # Evil Twin
        card_evil = self._create_info_card(
            self.cards_frame2,
            "👥 Evil Twin Attacks",
            "A malicious clone of a legitimate Wi-Fi access point.",
            [
                "How it works: An attacker broadcasts the same SSID name as a public or home network.",
                "The trap: They set it as Open or configure it with a captive portal to harvest credentials.",
                "Detection: Watch for mismatched security settings or double SSIDs with different signals.",
                "Mitigation: Avoid connecting to duplicate network names, and use VPNs for all connections."
            ],
            COLOR_DANGER
        )
        card_evil.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Public WiFi
        card_public = self._create_info_card(
            self.cards_frame2,
            "📶 Public Wi-Fi Risks",
            "Connecting to unencrypted networks in coffee shops, airports, or hotels.",
            [
                "Sniffing: Attackers on the same network can capture DNS queries, unencrypted web pages, and metadata.",
                "Man-in-the-Middle (MitM): Router compromise allows attackers to inject malicious code or redirect you to phishing sites.",
                "Action: Turn off auto-connect to open networks.",
                "Action: Use HTTPS Everywhere and run a trusted virtual private network (VPN) immediately."
            ],
            COLOR_WARN
        )
        card_public.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # --- SECTION 3: Defensive Best Practices ---
        self.sec3_lbl = ctk.CTkLabel(self, text="3. Router Hardening Checklist", font=FONT_SECTION, text_color=COLOR_PRIMARY)
        self.sec3_lbl.pack(anchor="w", pady=(10, 10))

        self.checklist_card = StyledCard(self)
        self.checklist_card.pack(fill="x", pady=(0, 20))

        checklist_items = [
            ("🔐 **Use Strong Passwords:** Avoid default passwords or weak combinations. Make Wi-Fi passwords at least 12-16 characters with letters, numbers, and symbols.", COLOR_TEXT),
            ("🔌 **Disable WPS (Wi-Fi Protected Setup):** WPS allows easy connection but is highly vulnerable to PIN brute-forcing attacks (e.g. Reaver tools).", COLOR_WARN),
            ("📝 **Change Default Admin Credentials:** The router login portal (e.g. admin/admin) should be updated to custom, secure passwords immediately.", COLOR_DANGER),
            ("🔄 **Keep Firmware Updated:** Enable automatic router updates. Manufacturers patch critical remote code execution (RCE) bugs regularly.", COLOR_SAFE),
            ("🕸️ **Set up a Guest Network:** Isolate smart IoT devices (which are frequently vulnerable) and temporary visitors onto a separate Guest Network partition.", COLOR_PRIMARY),
        ]

        for text, dot_color in checklist_items:
            row = ctk.CTkFrame(self.checklist_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=6)
            
            dot = ctk.CTkLabel(row, text="•", font=("Segoe UI", 16, "bold"), text_color=dot_color)
            dot.pack(side="left", padx=(0, 10))
            
            lbl = ctk.CTkLabel(row, text=text, font=FONT_BODY, text_color=COLOR_TEXT, justify="left", anchor="w")
            lbl.pack(side="left", fill="x", expand=True)

    def _create_info_card(self, parent, title, subtitle, bullets, highlight_color):
        card = StyledCard(parent)
        
        # Line indicator at top
        indicator = ctk.CTkFrame(card, height=4, fg_color=highlight_color, corner_radius=0)
        indicator.pack(fill="x", side="top")
        
        # Content frame
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=15)
        
        lbl_title = ctk.CTkLabel(content, text=title, font=FONT_BODY_BOLD, text_color=COLOR_TEXT, anchor="w")
        lbl_title.pack(fill="x", pady=(0, 2))
        
        lbl_sub = ctk.CTkLabel(content, text=subtitle, font=FONT_SMALL, text_color=COLOR_TEXT_MUTED, wraplength=260, justify="left", anchor="w")
        lbl_sub.pack(fill="x", pady=(0, 10))
        
        # Bullets
        for bullet in bullets:
            row = ctk.CTkFrame(content, fg_color="transparent")
            row.pack(fill="x", pady=3)
            
            bullet_dot = ctk.CTkLabel(row, text="▪", font=FONT_SMALL, text_color=highlight_color)
            bullet_dot.pack(side="left", anchor="n", padx=(0, 8), pady=2)
            
            bullet_txt = ctk.CTkLabel(row, text=bullet, font=FONT_SMALL, text_color=COLOR_TEXT, wraplength=240, justify="left", anchor="w")
            bullet_txt.pack(side="left", fill="x", expand=True)
            
        return card
