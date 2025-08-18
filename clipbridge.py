#!/usr/bin/env python3
"""
Clipboard Bridge - Send text and images from iPhone to Windows PC clipboard
"""

import base64
import json
import logging
import os
import signal
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import pyperclip
import pystray
from PIL import Image, ImageDraw

# Global reference to the ClipboardBridge instance
bridge_instance = None


class ClipboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for clipboard operations"""
    
    def do_POST(self):
        """Handle POST requests to /clip endpoint"""
        if self.path != '/clip':
            self.send_error(404, "Not Found")
            return
        
        try:
            # Get content length and read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error(400, "Empty request body")
                return
            
            post_data = self.rfile.read(content_length)
            content_type = self.headers.get('Content-Type', '').lower()
            
            # Handle different content types
            if 'application/json' in content_type:
                self.handle_json_data(post_data)
            elif 'multipart/form-data' in content_type:
                self.handle_multipart_data(post_data, content_type)
            elif any(img_type in content_type for img_type in ['image/']):
                self.handle_direct_image_data(post_data, content_type)
            else:
                self.send_error(400, f"Unsupported content type: {content_type}")
                
        except Exception as e:
            print(f"ERROR: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def handle_json_data(self, post_data):
        """Handle JSON data (text or base64 image)"""
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            if 'text' in data:
                self.handle_text_data(data['text'])
            elif 'image' in data:
                self.handle_base64_image_data(data['image'])
            else:
                self.send_error(400, "Missing 'text' or 'image' field")
                
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            self.send_error(500, f"JSON processing error: {str(e)}")
    
    def handle_text_data(self, text):
        """Handle text clipboard data"""
        try:
            if not isinstance(text, str):
                self.send_error(400, "'text' must be a string")
                return
            
            # Copy to clipboard
            pyperclip.copy(text)
            print(f"Text copied: {text[:50]}{'...' if len(text) > 50 else ''}")
            
            self.show_notification(f"Text copied: {text}")
            self.send_success_response("Text copied to clipboard")
            
        except Exception as e:
            print(f"ERROR: Text handling failed: {e}")
            self.send_error(500, f"Text processing error: {str(e)}")
    
    def handle_base64_image_data(self, image_data):
        """Handle base64 encoded image data"""
        try:
            # Decode base64 image
            if image_data.startswith('data:image'):
                # Handle data URL format: data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
                header, base64_data = image_data.split(',', 1)
                image_bytes = base64.b64decode(base64_data)
            else:
                # Direct base64 string
                image_bytes = base64.b64decode(image_data)
            
            self.copy_image_to_clipboard(image_bytes)
            
        except Exception as e:
            print(f"ERROR: Base64 image handling failed: {e}")
            self.send_error(500, f"Base64 image processing error: {str(e)}")
    
    def handle_multipart_data(self, post_data, content_type):
        """Handle multipart/form-data file uploads"""
        try:
            import email
            
            # Parse the boundary from content-type header
            boundary = None
            if 'boundary=' in content_type:
                boundary = content_type.split('boundary=')[1].split(';')[0].strip()
            
            if not boundary:
                self.send_error(400, "Invalid multipart data - no boundary")
                return
            
            # Create a proper email message for parsing
            message_text = f"Content-Type: {content_type}\r\n\r\n" + post_data.decode('latin-1')
            
            # Parse multipart data
            msg = email.message_from_string(message_text)
            
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_disposition() == 'form-data':
                        content_type_part = part.get_content_type()
                        filename = part.get_filename()
                        
                        if content_type_part.startswith('image/') or (filename and any(ext in filename.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.heic'])):
                            # This is an image file
                            image_data = part.get_payload(decode=True)
                            print(f"Image received: {len(image_data)} bytes")
                            self.copy_image_to_clipboard(image_data)
                            return
                        elif content_type_part.startswith('text/') or part.get_param('name') == 'text':
                            # This is text data
                            text_data = part.get_payload(decode=True).decode('utf-8')
                            self.handle_text_data(text_data)
                            return
            
            self.send_error(400, "No valid file or text found in upload")
            
        except Exception as e:
            print(f"ERROR: Multipart handling failed: {e}")
            self.send_error(500, f"Multipart processing error: {str(e)}")
    
    def handle_direct_image_data(self, post_data, content_type):
        """Handle direct image data"""
        try:
            self.copy_image_to_clipboard(post_data)
        except Exception as e:
            print(f"ERROR: Direct image handling failed: {e}")
            self.send_error(500, f"Direct image processing error: {str(e)}")
    
    def copy_image_to_clipboard(self, image_bytes):
        """Copy image bytes to Windows clipboard"""
        try:
            # Save image to temporary file
            temp_image_path = os.path.abspath("temp_clipboard_image.png")
            
            # Convert image with Pillow
            try:
                from PIL import Image as PILImage
                from io import BytesIO
                
                # Register HEIF opener with Pillow
                try:
                    from pillow_heif import register_heif_opener
                    register_heif_opener()
                except ImportError:
                    pass
                
                # Load and convert image
                image_stream = BytesIO(image_bytes)
                pil_image = PILImage.open(image_stream)
                
                # Convert to RGB if necessary
                if pil_image.mode not in ('RGB', 'L'):
                    pil_image = pil_image.convert('RGB')
                
                # Save as PNG
                pil_image.save(temp_image_path, 'PNG')
                print(f"Image converted: {pil_image.size}")
                
            except Exception as conversion_error:
                print(f"Image conversion failed: {conversion_error}")
                self.send_error(400, "Could not process image")
                return
            
            # Verify file exists and has reasonable size
            if not os.path.exists(temp_image_path) or os.path.getsize(temp_image_path) < 100:
                self.send_error(500, "Image conversion failed")
                return
            
            # Copy to clipboard using PowerShell
            powershell_script = f'''
            Add-Type -AssemblyName System.Windows.Forms, System.Drawing
            $image = [System.Drawing.Image]::FromFile("{temp_image_path.replace("\\", "\\\\")}")
            [System.Windows.Forms.Clipboard]::SetImage($image)
            $image.Dispose()
            '''
            
            result = subprocess.run([
                "powershell", "-WindowStyle", "Hidden", "-Command", powershell_script
            ], check=False, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Image copied to clipboard")
                self.show_notification("Image copied to clipboard")
                self.send_success_response("Image copied to clipboard")
            else:
                self.send_error(500, "Failed to copy image to clipboard")
            
            # Clean up temporary file
            try:
                time.sleep(0.5)
                os.remove(temp_image_path)
            except Exception:
                pass
                
        except Exception as e:
            print(f"ERROR: Image clipboard operation failed: {e}")
            self.send_error(500, f"Image clipboard error: {str(e)}")
    
    def show_notification(self, message):
        """Show Windows toast notification"""
        try:
            # Truncate message for notification if it's too long
            display_text = message if len(message) <= 50 else message[:47] + "..."
            
            # Simple toast notification without custom icon (for service compatibility)
            powershell_script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

            $template = @"
            <toast>
                <visual>
                    <binding template="ToastText02">
                        <text id="1">Clipbridge</text>
                        <text id="2">{display_text}</text>
                    </binding>
                </visual>
            </toast>
"@

            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Clipbridge").Show($toast)
            '''
            
            subprocess.run([
                "powershell", "-WindowStyle", "Hidden", "-Command", powershell_script
            ], check=False, capture_output=True)
                
        except Exception as e:
            # If notification fails, just print to console
            print(f"Notification: {message}")
    
    def send_success_response(self, message):
        """Send a success response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = {"status": "success", "message": message}
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress default request logs"""
        pass


class ClipboardBridge:
    """Main application class"""
    
    def __init__(self, headless=False):
        self.server = None
        self.server_thread = None
        self.tray = None
        self.running = False
        self.headless = headless
    
    def create_icon(self):
        """Load icon from ic_fluent_clipboard_20_color.ico file, fallback to simple icon"""
        try:
            # Try to load the ic_fluent_clipboard_20_color.ico file
            icon_path = "ic_fluent_clipboard_20_color.ico"
            if os.path.exists(icon_path):
                print(f"Using icon file: {icon_path}")
                return Image.open(icon_path)
            else:
                print(f"Warning: {icon_path} not found, using simple fallback icon")
        except Exception as e:
            print(f"Warning: Could not load {icon_path} ({e}), using simple fallback icon")
        
        # Simple fallback icon - just a colored circle
        image = Image.new('RGB', (64, 64), color='white')
        draw = ImageDraw.Draw(image)
        
        # Draw a simple circle with the blue color
        circle_color = '#0682f7'
        draw.ellipse([16, 16, 48, 48], fill=circle_color, outline='white', width=2)
        
        # Add a simple "C" for Clipbridge
        draw.text((24, 20), "C", fill='white', anchor="mm")
        
        return image
    
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
            icon_image = self.create_icon()
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
    print("- For images: JSON with 'image' field (base64) or direct image data")
    
    bridge_instance = ClipboardBridge(headless=headless)
    bridge_instance.run()


if __name__ == "__main__":
    main()
