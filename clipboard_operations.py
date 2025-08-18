"""
Clipboard operations for text and images
"""

import os
import subprocess
import time
import pyperclip
from PIL import Image as PILImage
from io import BytesIO
from notifications import show_notification


def copy_text_to_clipboard(text):
    """Copy text to clipboard"""
    try:
        if not isinstance(text, str):
            raise ValueError("'text' must be a string")
        
        # Copy to clipboard
        pyperclip.copy(text)
        print(f"Text copied: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        show_notification(f"Text copied: {text}")
        return True
        
    except Exception as e:
        print(f"ERROR: Text handling failed: {e}")
        raise


def copy_image_to_clipboard(image_bytes):
    """Copy image bytes to Windows clipboard"""
    try:
        # Save image to temporary file
        temp_image_path = os.path.abspath("temp_clipboard_image.png")
        
        # Convert image with Pillow
        try:
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
            raise ValueError("Could not process image")
        
        # Verify file exists and has reasonable size
        if not os.path.exists(temp_image_path) or os.path.getsize(temp_image_path) < 100:
            raise RuntimeError("Image conversion failed")
        
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
            show_notification("Image copied to clipboard")
        else:
            raise RuntimeError("Failed to copy image to clipboard")
        
        # Clean up temporary file
        try:
            time.sleep(0.5)
            os.remove(temp_image_path)
        except Exception:
            pass
            
        return True
            
    except Exception as e:
        print(f"ERROR: Image clipboard operation failed: {e}")
        raise
