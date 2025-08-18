"""
System tray management
"""

import signal
import sys
import time
import threading
import pystray
from http.server import HTTPServer
from http_handler import ClipboardHandler
from icon_utils import create_app_icon


class ClipboardBridge:
    """Main application class"""
    
    def __init__(self, headless=False):
        self.server = None
        self.server_thread = None
        self.tray = None
        self.running = False
        self.headless = headless
    
    def start_server(self):
        """Start the HTTP server in a background thread"""
        self.server = HTTPServer(('0.0.0.0', 5019), ClipboardHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        print("Clipbridge server started on http://0.0.0.0:5019")
    
    def stop_server(self):
        """Stop the HTTP server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.server_thread:
            self.server_thread.join(timeout=1)
    
    def quit_app(self, icon, item):
        """Quit the application"""
        print("Shutting down Clipbridge...")
        self.running = False
        self.stop_server()
        if self.tray:
            self.tray.stop()
    
    def run(self):
        """Run the application"""
        self.running = True
        
        # Start HTTP server
        self.start_server()
        
        if self.headless:
            # Run in headless mode (for service)
            print("Running in headless mode (service mode)")
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Shutting down...")
        else:
            # Run with system tray
            icon_image = create_app_icon()
            menu = pystray.Menu(pystray.MenuItem("Quit", self.quit_app))
            self.tray = pystray.Icon("clipbridge", icon_image, "Clipbridge", menu)
            
            # Set up signal handlers for graceful shutdown
            def signal_handler(sig, frame):
                print("\nReceived interrupt signal. Shutting down...")
                self.quit_app(None, None)
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            try:
                # Run the tray (this blocks until quit)
                self.tray.run()
            except KeyboardInterrupt:
                self.quit_app(None, None)
        
        self.stop_server()
