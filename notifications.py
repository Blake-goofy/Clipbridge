"""
Windows notification system
"""

import subprocess
import os


def show_notification(message):
    """Show Windows toast notification with icon if available"""
    try:
        # Truncate message for notification if it's too long
        display_text = message if len(message) <= 50 else message[:47] + "..."
        print(f"DEBUG: Showing notification with message: '{display_text}'")
        
        # Log current working directory for debugging
        print(f"DEBUG: Current working directory: {os.getcwd()}")
        # Use absolute path for icon
        icon_path = os.path.abspath("clipbridge_icon.png")
        has_icon = os.path.exists(icon_path)
        print(f"DEBUG: Checking for icon at: {icon_path}")
        print(f"DEBUG: Icon exists: {has_icon}")
        
        if has_icon:
            # Toast notification with custom icon
            icon_full_path = icon_path.replace("\\", "/")
            print(f"DEBUG: Using icon path: file:///{icon_full_path}")
            
            powershell_script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

            Write-Host "DEBUG: PowerShell - Creating toast with icon"
            Write-Host "DEBUG: PowerShell - Icon path: file:///{icon_full_path}"

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

            Write-Host "DEBUG: PowerShell - XML template created"
            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            Write-Host "DEBUG: PowerShell - XML loaded"
            $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
            Write-Host "DEBUG: PowerShell - Toast notification created"
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Clipbridge").Show($toast)
            Write-Host "DEBUG: PowerShell - Toast notification shown"
            '''
            
            print("DEBUG: Running PowerShell script with icon...")
        else:
            print("DEBUG: No icon found, using simple notification")
            # Simple toast notification without icon
            powershell_script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

            Write-Host "DEBUG: PowerShell - Creating simple toast without icon"

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

            Write-Host "DEBUG: PowerShell - XML template created"
            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            Write-Host "DEBUG: PowerShell - XML loaded"
            $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
            Write-Host "DEBUG: PowerShell - Toast notification created"
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Clipbridge").Show($toast)
            Write-Host "DEBUG: PowerShell - Toast notification shown"
            '''
        
        # Run PowerShell with output capture
        result = subprocess.run([
            "powershell", "-WindowStyle", "Hidden", "-Command", powershell_script
        ], check=False, capture_output=True, text=True)
        
        print(f"DEBUG: PowerShell return code: {result.returncode}")
        if result.stdout:
            print(f"DEBUG: PowerShell stdout: {result.stdout}")
        if result.stderr:
            print(f"DEBUG: PowerShell stderr: {result.stderr}")
            
    except Exception as e:
        # If notification fails, just print to console
        print(f"ERROR: Notification failed: {e}")
        print(f"Fallback notification: {message}")
        
if __name__ == "__main__":
    show_notification("Test notification from notifications.py!")