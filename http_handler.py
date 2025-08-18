"""
HTTP request handler for clipboard operations
"""

import json
import email
from http.server import BaseHTTPRequestHandler
from clipboard_operations import copy_text_to_clipboard, copy_image_to_clipboard


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
        """Handle JSON data (text only)"""
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            if 'text' in data:
                self.handle_text_data(data['text'])
            else:
                self.send_error(400, "Missing 'text' field")
                
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            self.send_error(500, f"JSON processing error: {str(e)}")
    
    def handle_text_data(self, text):
        """Handle text clipboard data"""
        try:
            copy_text_to_clipboard(text)
            self.send_success_response("Text copied to clipboard")
            
        except Exception as e:
            print(f"ERROR: Text handling failed: {e}")
            self.send_error(500, f"Text processing error: {str(e)}")
    
    def handle_multipart_data(self, post_data, content_type):
        """Handle multipart/form-data file uploads"""
        try:
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
                            copy_image_to_clipboard(image_data)
                            self.send_success_response("Image copied to clipboard")
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
            copy_image_to_clipboard(post_data)
            self.send_success_response("Image copied to clipboard")
        except Exception as e:
            print(f"ERROR: Direct image handling failed: {e}")
            self.send_error(500, f"Direct image processing error: {str(e)}")
    
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
