#!/usr/bin/env python3
"""
Clipboard Bridge - Send text and images from iPhone to Windows PC clipboard
Main entry point
"""

import sys
import logging
from app import ClipboardBridge

# Global reference to the ClipboardBridge instance
bridge_instance = None


def main():
    """Main entry point"""
    global bridge_instance
    
    # Check for headless mode (service mode)
    headless = "--headless" in sys.argv or "--service" in sys.argv
    
    # Suppress HTTP server logs
    logging.getLogger().setLevel(logging.WARNING)
    
    print("Starting Clipbridge...")
    if headless:
        print("Running in service mode (headless)")
    else:
        print("The app will run in the system tray.")
        print("Right-click the tray icon to quit.")
    print("Send POST requests to http://localhost:5019/clip")
    print("- For text: JSON with 'text' field")
    print("- For images: direct image data or multipart file upload")
    
    bridge_instance = ClipboardBridge(headless=headless)
    bridge_instance.run()


if __name__ == "__main__":
    main()
