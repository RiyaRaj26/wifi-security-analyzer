import customtkinter as ctk

# Cybersecurity Palette (Dark Mode First)
BG_MAIN = "#0B0F19"         # Very dark slate blue (background)
BG_SIDEBAR = "#070A13"      # Almost black (sidebar background)
BG_CARD = "#151C2C"         # Mid-tone dark slate (dashboard cards, network items)
COLOR_PRIMARY = "#0EA5E9"   # Cyber Neon Blue (primary buttons, active tabs, accents)
COLOR_HOVER = "#0284C7"     # Darker Neon Blue (hover state)
COLOR_TEXT = "#F8FAFC"      # Off-white (primary text)
COLOR_TEXT_MUTED = "#94A3B8"# Muted slate-gray (labels, descriptions)

# Status/Risk Color Code Badges
COLOR_SAFE = "#10B981"      # Cyber Green (WPA3 / Safe)
COLOR_WARN = "#F59E0B"      # Orange (WPA2-TKIP / Moderate Risk)
COLOR_DANGER = "#EF4444"    # Red (Open / WEP / Critical Risk)
COLOR_MUTED = "#64748B"     # Slate Gray (Low Risk / Weak Signal)

# Fonts
FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_SECTION = ("Segoe UI", 16, "bold")
FONT_BODY_BOLD = ("Segoe UI", 12, "bold")
FONT_BODY = ("Segoe UI", 12, "normal")
FONT_SMALL = ("Segoe UI", 10, "normal")
FONT_CODE = ("Consolas", 10, "normal")

def apply_app_theme():
    """Initializes appearance mode and default color styling."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue") # use blue as default, customize specifically with colors above

class StyledCard(ctk.CTkFrame):
    """A pre-styled card with shadow border or clean background to match dark aesthetic."""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=BG_CARD,
            border_color="#1E293B",
            border_width=1,
            corner_radius=10,
            **kwargs
        )
