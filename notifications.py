"""
Windows notification system
"""

import subprocess
import os
import sys


def _get_app_dir():
    """Get the directory where the app executable or script is located."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def show_notification(message):
    """Show Windows toast notification with icon if available"""
    try:
        # Truncate message for notification if it's too long
        display_text = message if len(message) <= 50 else message[:47] + "..."

        # Resolve icon path relative to the app directory, not CWD
        icon_path = os.path.join(_get_app_dir(), "clipbridge_icon.png")
        has_icon = os.path.exists(icon_path)
        print(f"Checking for notification icon at: {icon_path} (exists: {has_icon})")
        
        if has_icon:
            # Toast notification with custom icon
            icon_full_path = icon_path.replace("\\", "/")

            powershell_script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

            $template = @"
            <toast>
                <visual>
                    <binding template="ToastImageAndText02">
                        <image id="1" src="file:///{icon_full_path}" alt="Clipbridge"/>
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
        else:
            # Simple toast notification without icon
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
        
        # Run PowerShell
        result = subprocess.run([
            "powershell", "-WindowStyle", "Hidden", "-Command", powershell_script
        ], check=False, capture_output=True, text=True,
           creationflags=subprocess.CREATE_NO_WINDOW)

        if result.returncode != 0 and result.stderr:
            print(f"Notification error: {result.stderr}")
            
    except Exception as e:
        # If notification fails, just print to console
        print(f"ERROR: Notification failed: {e}")
        print(f"Fallback notification: {message}")
        
if __name__ == "__main__":
    show_notification("Test notification from notifications.py!")