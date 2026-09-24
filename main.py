import logging
import sys
import customtkinter as ctk

# Configure logging to console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("WiFiSecurityAnalyzer")

from ui.theme import apply_app_theme
from ui.main_window import MainWindow
from ui.dashboard_view import DashboardView
from ui.analyzer_view import AnalyzerView
from ui.channel_view import ChannelView
from ui.education_view import EducationView
from ui.history_view import HistoryView
from ui.future_view import FutureView
from controller.main_controller import MainController

def main():
    logger.info("Starting Wi-Fi Security Analyzer application...")
    
    # 1. Initialize core themes & color palettes
    apply_app_theme()
    
    # 2. Instantiate MVC controller
    controller = MainController()
    
    # 3. Create Main Window View
    app = MainWindow(controller)
    
    # 4. Register all views/tabs (lazy loaded)
    app.register_tab("dashboard", DashboardView)
    app.register_tab("analyzer", AnalyzerView)
    app.register_tab("channel", ChannelView)
    app.register_tab("education", EducationView)
    app.register_tab("history", HistoryView)
    app.register_tab("future", FutureView)
    
    # 5. Inject view back to controller
    controller.set_view(app)
    
    # 6. Switch to dashboard by default
    app.switch_tab("dashboard")
    
    # 7. Start Tkinter Main Event Loop
    try:
        app.mainloop()
    except KeyboardInterrupt:
        logger.info("Application closed by keyboard interrupt.")
    except Exception as e:
        logger.critical(f"Unhandled app exception: {e}", exc_info=True)

if __name__ == "__main__":
    main()
