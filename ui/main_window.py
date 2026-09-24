import customtkinter as ctk
from ui.theme import *

class MainWindow(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        # Configure window
        self.title("Wi-Fi Security Analyzer")
        self.geometry("1100x700")
        self.minsize(1000, 600)
        self.configure(fg_color=BG_MAIN)
        
        # Track active tab
        self.active_tab_name = None
        self.tabs = {}
        
        # Layout structure
        self._create_sidebar()
        self._create_status_bar()
        self._create_content_area()
        
    def _create_sidebar(self):
        # Sidebar Frame
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=BG_SIDEBAR, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        # App Title / Branding
        self.title_label = ctk.CTkLabel(
            self.sidebar, 
            text="🛡️ Wi-Fi Security\nAnalyzer", 
            font=("Segoe UI", 18, "bold"),
            text_color=COLOR_PRIMARY,
            justify="center"
        )
        self.title_label.pack(pady=(20, 30), padx=10)
        
        # Nav Buttons
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "🛡️  Network Scan"),
            ("analyzer", "🔍  Security Analyzer"),
            ("channel", "📊  Channel Analyzer"),
            ("education", "📚  Awareness Hub"),
            ("history", "⏳  Scan History"),
            ("future", "🔮  Concept Labs"),
        ]
        
        for name, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                font=FONT_BODY_BOLD,
                fg_color="transparent",
                text_color=COLOR_TEXT_MUTED,
                hover_color="#1E293B",
                height=40,
                anchor="w",
                corner_radius=6,
                command=lambda n=name: self.switch_tab(n)
            )
            btn.pack(pady=5, padx=10, fill="x")
            self.nav_buttons[name] = btn
            
        # Theme / Footer info at bottom of sidebar
        self.sidebar_footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_footer.pack(side="bottom", fill="x", pady=20, padx=10)
        
        # Theme Toggle
        self.theme_label = ctk.CTkLabel(self.sidebar_footer, text="Appearance Mode", font=FONT_SMALL, text_color=COLOR_TEXT_MUTED)
        self.theme_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.theme_switch = ctk.CTkOptionMenu(
            self.sidebar_footer,
            values=["Dark", "Light"],
            command=self._change_appearance_mode,
            fg_color=BG_CARD,
            button_color=COLOR_PRIMARY,
            button_hover_color=COLOR_HOVER,
            dropdown_fg_color=BG_CARD,
            dropdown_hover_color=COLOR_HOVER,
            text_color=COLOR_TEXT,
            font=FONT_SMALL
        )
        self.theme_switch.set("Dark")
        self.theme_switch.pack(fill="x", padx=10)
        
        # Uptime or version text
        self.version_label = ctk.CTkLabel(
            self.sidebar_footer, 
            text="v1.0.0 (Education/Defensive)", 
            font=("Segoe UI", 9), 
            text_color=COLOR_MUTED
        )
        self.version_label.pack(pady=(15, 0))

    def _create_status_bar(self):
        self.status_bar = ctk.CTkFrame(self, height=28, fg_color=BG_SIDEBAR, corner_radius=0)
        self.status_bar.pack(side="bottom", fill="x")
        
        self.status_text = ctk.CTkLabel(
            self.status_bar, 
            text="Status: Idle | Ready to audit", 
            font=FONT_SMALL, 
            text_color=COLOR_TEXT_MUTED
        )
        self.status_text.pack(side="left", padx=15, pady=2)
        
        self.mode_text = ctk.CTkLabel(
            self.status_bar, 
            text="Scan Mode: Initializing...", 
            font=FONT_SMALL, 
            text_color=COLOR_PRIMARY
        )
        self.mode_text.pack(side="right", padx=15, pady=2)

    def _create_content_area(self):
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="right", fill="both", expand=True)

    @property
    def dashboard(self):
        return self._get_or_create_tab("dashboard")

    @property
    def analyzer(self):
        return self._get_or_create_tab("analyzer")

    @property
    def channel(self):
        return self._get_or_create_tab("channel")

    @property
    def education(self):
        return self._get_or_create_tab("education")

    @property
    def history(self):
        return self._get_or_create_tab("history")

    @property
    def future(self):
        return self._get_or_create_tab("future")

    def _get_or_create_tab(self, name: str):
        tab_info = self.tabs[name]
        if tab_info["instance"] is None:
            tab_info["instance"] = tab_info["class"](self.content_frame, self.controller)
        return tab_info["instance"]

    def register_tab(self, name: str, frame_class):
        """Registers a tab with the window, delaying instantiation until it is switched to."""
        self.tabs[name] = {
            "class": frame_class,
            "instance": None
        }

    def switch_tab(self, name: str):
        if name not in self.tabs:
            return
            
        # Highlight button
        for tab_name, btn in self.nav_buttons.items():
            if tab_name == name:
                btn.configure(fg_color=COLOR_PRIMARY, text_color=COLOR_TEXT)
            else:
                btn.configure(fg_color="transparent", text_color=COLOR_TEXT_MUTED)
                
        # Hide current active tab instance
        if self.active_tab_name and self.tabs[self.active_tab_name]["instance"]:
            self.tabs[self.active_tab_name]["instance"].pack_forget()
            
        # Load tab instance
        tab_instance = self._get_or_create_tab(name)
            
        # Show new active tab
        tab_instance.pack(fill="both", expand=True, padx=25, pady=25)
        self.active_tab_name = name
        
        # Trigger update of specific views when user navigates to them
        if hasattr(tab_instance, "on_tab_active"):
            tab_instance.on_tab_active()

    def update_status(self, status: str):
        self.status_text.configure(text=f"Status: {status}")

    def update_scan_mode(self, is_simulated: bool):
        if is_simulated:
            self.mode_text.configure(
                text="Scan Mode: Simulated Fallback", 
                text_color=COLOR_WARN
            )
        else:
            self.mode_text.configure(
                text="Scan Mode: Live Wi-Fi Card", 
                text_color=COLOR_SAFE
            )

    def _change_appearance_mode(self, new_mode: str):
        ctk.set_appearance_mode(new_mode)
        
        # Update colors on specific CustomTkinter frames that may not automatically update
        # Standard widgets will automatically respond to set_appearance_mode
        pass
