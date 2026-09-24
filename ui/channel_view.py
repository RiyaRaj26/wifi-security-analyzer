import customtkinter as ctk
import numpy as np
from ui.theme import *

# Try to import matplotlib and its tkinter backend
MATPLOTLIB_AVAILABLE = False
try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    pass

class ChannelView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.networks = []
        self.canvas_widget = None
        self.fig = None
        self._setup_ui()

    def _setup_ui(self):
        # Header
        self.header_lbl = ctk.CTkLabel(self, text="Channel Analyzer", font=FONT_TITLE, text_color=COLOR_TEXT)
        self.header_lbl.pack(anchor="w", pady=(0, 15))

        # Main Split Layout (Left: Matplotlib Chart, Right: Recommendations)
        self.main_split = ctk.CTkFrame(self, fg_color="transparent")
        self.main_split.pack(fill="both", expand=True)

        # Left Card (Graph)
        self.chart_card = StyledCard(self.main_split)
        self.chart_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.chart_title = ctk.CTkLabel(self.chart_card, text="Signal Overlap & Channel Congestion (2.4 GHz)", font=FONT_SECTION, text_color=COLOR_TEXT)
        self.chart_title.pack(pady=(12, 5), padx=15, anchor="w")

        self.chart_container = ctk.CTkFrame(self.chart_card, fg_color="transparent")
        self.chart_container.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        # Right Card (Recommendations)
        self.rec_card = StyledCard(self.main_split, width=340)
        self.rec_card.pack(side="right", fill="both", padx=(10, 0))

        self.rec_title = ctk.CTkLabel(self.rec_card, text="Channel Recommendations", font=FONT_SECTION, text_color=COLOR_TEXT)
        self.rec_title.pack(pady=(12, 10), padx=15, anchor="w")

        # 2.4 GHz Recommendations
        self.rec_2g_frame = ctk.CTkFrame(self.rec_card, fg_color=BG_MAIN, corner_radius=8, border_color="#1E293B", border_width=1)
        self.rec_2g_frame.pack(fill="x", padx=15, pady=8, ipady=5)
        
        self.rec_2g_title = ctk.CTkLabel(self.rec_2g_frame, text="2.4 GHz Optimal Channel", font=FONT_BODY_BOLD, text_color=COLOR_TEXT_MUTED)
        self.rec_2g_title.pack(anchor="w", padx=15, pady=(5, 2))
        
        self.rec_2g_val = ctk.CTkLabel(self.rec_2g_frame, text="Channel 6", font=("Segoe UI", 20, "bold"), text_color=COLOR_SAFE)
        self.rec_2g_val.pack(anchor="w", padx=15)
        
        self.rec_2g_desc = ctk.CTkLabel(
            self.rec_2g_frame, 
            text="Channel 6 is currently showing the lowest overlap and RF interference in your area.", 
            font=FONT_SMALL, 
            text_color=COLOR_TEXT,
            wraplength=290,
            justify="left"
        )
        self.rec_2g_desc.pack(anchor="w", padx=15, pady=(2, 10))

        # 5 GHz Recommendations
        self.rec_5g_frame = ctk.CTkFrame(self.rec_card, fg_color=BG_MAIN, corner_radius=8, border_color="#1E293B", border_width=1)
        self.rec_5g_frame.pack(fill="x", padx=15, pady=8, ipady=5)
        
        self.rec_5g_title = ctk.CTkLabel(self.rec_5g_frame, text="5 GHz Optimal Channel", font=FONT_BODY_BOLD, text_color=COLOR_TEXT_MUTED)
        self.rec_5g_title.pack(anchor="w", padx=15, pady=(5, 2))
        
        self.rec_5g_val = ctk.CTkLabel(self.rec_5g_frame, text="Channel 36", font=("Segoe UI", 20, "bold"), text_color=COLOR_SAFE)
        self.rec_5g_val.pack(anchor="w", padx=15)
        
        self.rec_5g_desc = ctk.CTkLabel(
            self.rec_5g_frame, 
            text="Channel 36 has no overlapping signals detected, offering clean high-speed throughput.", 
            font=FONT_SMALL, 
            text_color=COLOR_TEXT,
            wraplength=290,
            justify="left"
        )
        self.rec_5g_desc.pack(anchor="w", padx=15, pady=(2, 10))

        # Educational Tip
        self.tip_frame = ctk.CTkFrame(self.rec_card, fg_color="transparent")
        self.tip_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.tip_lbl = ctk.CTkLabel(
            self.tip_frame,
            text="💡 **How to change channels:**\n1. Login to your router's web portal (usually http://192.168.1.1)\n2. Navigate to 'Wireless Settings'\n3. Set 'Channel' from 'Auto' to your recommended manual channel.",
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED,
            justify="left",
            wraplength=290
        )
        self.tip_lbl.pack(side="bottom", anchor="w", pady=10)

        self.update_placeholder()

    def update_placeholder(self):
        # Displays placeholder if no networks
        for child in self.chart_container.winfo_children():
            child.destroy()
            
        lbl = ctk.CTkLabel(
            self.chart_container, 
            text="📊 No scan data available. Perform a Network Scan first.", 
            font=FONT_BODY,
            text_color=COLOR_TEXT_MUTED
        )
        lbl.pack(pady=100)

    def draw_chart(self):
        if not MATPLOTLIB_AVAILABLE:
            for child in self.chart_container.winfo_children():
                child.destroy()
            lbl = ctk.CTkLabel(
                self.chart_container, 
                text="Matplotlib library is currently loading or unavailable.\nEnsure installation is complete.", 
                font=FONT_BODY,
                text_color=COLOR_WARN
            )
            lbl.pack(pady=100)
            return

        # Clear existing container children
        for child in self.chart_container.winfo_children():
            child.destroy()

        # Create new figure
        # Set dark theme styling for the chart
        plt.rcParams['text.color'] = COLOR_TEXT
        plt.rcParams['axes.labelcolor'] = COLOR_TEXT_MUTED
        plt.rcParams['xtick.color'] = COLOR_TEXT_MUTED
        plt.rcParams['ytick.color'] = COLOR_TEXT_MUTED
        
        self.fig, ax = plt.subplots(figsize=(6, 4.5), facecolor=BG_CARD)
        ax.set_facecolor(BG_MAIN)
        
        # Grid settings
        ax.grid(True, color="#1E293B", linestyle="--", linewidth=0.5, alpha=0.5)
        ax.set_axisbelow(True)

        # Plot settings
        ax.set_xlim(0, 14)
        ax.set_ylim(-100, -25)
        ax.set_xlabel("Wi-Fi Channel")
        ax.set_ylabel("Signal Strength (dBm)")
        ax.set_xticks(range(1, 14))

        # Filter networks to 2.4 GHz band (channels 1-14)
        nets_2g = [n for n in self.networks if n["channel"] <= 14]
        
        if not nets_2g:
            # Draw standard/empty channels
            ax.text(7, -60, "No 2.4 GHz networks detected\nin range to analyze channel overlap.", 
                    horizontalalignment='center', verticalalignment='center', color=COLOR_TEXT_MUTED)
        else:
            # Draw a smooth dome (parabola) for each network
            # Formula: y = RSSI - C * (x - channel)^2, where C controls the dome width
            # Dome spans from channel - 2.5 to channel + 2.5
            for net in nets_2g:
                ch = net["channel"]
                rssi = net["rssi"]
                ssid = net["ssid"]
                
                # Check security type to assign dome line colors
                sec = net["security_type"].upper()
                if "WPA3" in sec:
                    color = COLOR_SAFE
                elif "OPEN" in sec or "WEP" in sec:
                    color = COLOR_DANGER
                else:
                    color = COLOR_PRIMARY
                
                # Create x data centered at channel
                x = np.linspace(max(0, ch - 2.5), min(14, ch + 2.5), 100)
                
                # Dome shape: reaches rssi at the center and falls to -100 at the edges (width of 5 channels)
                # y(ch) = rssi
                # y(ch ± 2.5) = -100
                # y = (rssi - (-100)) * (1 - ((x - ch)/2.5)^2) - 100
                height = rssi - (-100)
                y = height * (1 - ((x - ch) / 2.5)**2) - 100
                
                # Plot dome
                ax.plot(x, y, color=color, linewidth=2, alpha=0.7)
                
                # Fill under curve
                ax.fill_between(x, -100, y, color=color, alpha=0.15)
                
                # Annotate SSID at peak of dome
                # Limit label length
                label_text = ssid if len(ssid) <= 15 else f"{ssid[:12]}..."
                ax.text(ch, rssi + 1, label_text, fontsize=8, color=COLOR_TEXT, 
                        horizontalalignment='center', clip_on=True)

        # Make layout tight
        self.fig.tight_layout()

        # Render figure on Tkinter canvas
        self.canvas_widget = FigureCanvasTkAgg(self.fig, self.chart_container)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True)

    def set_networks_data(self, networks: list[dict], advice: dict):
        self.networks = networks
        
        # Update recommendations widgets
        recs = advice.get("channel_recommendations", {"2g": 1, "5g": 36})
        self.rec_2g_val.configure(text=f"Channel {recs['2g']}")
        self.rec_5g_val.configure(text=f"Channel {recs['5g']}")
        
        # Customize description detail
        self.rec_2g_desc.configure(
            text=f"Channel {recs['2g']} is currently recommended in the 2.4 GHz band because it has the least overlapping signal power."
        )
        self.rec_5g_desc.configure(
            text=f"Channel {recs['5g']} is the cleanest available 5 GHz channel with minimal local activity."
        )

        if self.networks:
            self.draw_chart()
        else:
            self.update_placeholder()

    def on_tab_active(self):
        """Redraws the chart when the tab is switched to, ensuring size fits perfectly."""
        if self.networks:
            self.draw_chart()
        else:
            self.update_placeholder()
