"""
Icon creation and management utilities
"""

import os
import glob
from PIL import Image, ImageDraw


def create_app_icon():
    """Look for any .ico file in the folder, create permanent fallback if needed"""
    try:
        # Look for any .ico file in the current directory
        ico_files = glob.glob("*.ico")
        
        if ico_files:
            icon_path = ico_files[0]  # Use the first .ico file found
            print(f"Using icon file: {icon_path}")
            return Image.open(icon_path)
        else:
            print("No .ico file found, creating permanent fallback icon")
            return _create_and_save_fallback_icon()
    except Exception as e:
        print(f"Warning: Could not load icon file ({e}), creating fallback icon")
        return _create_and_save_fallback_icon()


def _create_and_save_fallback_icon():
    """Create and save a permanent fallback icon file"""
    try:
        fallback_path = "clipbridge_fallback.ico"
        
        # Check if fallback already exists
        if os.path.exists(fallback_path):
            print(f"Using existing fallback icon: {fallback_path}")
            return Image.open(fallback_path)
        
        print(f"Creating permanent fallback icon: {fallback_path}")
        
        # Create a simple icon - colored circle with "C"
        image = Image.new('RGB', (64, 64), color='white')
        draw = ImageDraw.Draw(image)
        
        # Draw a simple circle with the blue color
        circle_color = '#0682f7'
        draw.ellipse([16, 16, 48, 48], fill=circle_color, outline='white', width=2)
        
        # Add a simple "C" for Clipbridge
        draw.text((24, 20), "C", fill='white', anchor="mm")
        
        # Save as ICO file for permanent use
        image.save(fallback_path, format='ICO', sizes=[(64, 64)])
        print(f"Fallback icon saved as {fallback_path}")
        
        return image
        
    except Exception as e:
        print(f"Warning: Could not save fallback icon ({e}), using temporary icon")
        # If saving fails, return the image without saving
        image = Image.new('RGB', (64, 64), color='white')
        draw = ImageDraw.Draw(image)
        circle_color = '#0682f7'
        draw.ellipse([16, 16, 48, 48], fill=circle_color, outline='white', width=2)
        draw.text((24, 20), "C", fill='white', anchor="mm")
        return image
