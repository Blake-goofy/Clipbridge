# Clipboard Bridge

A minimal Python tray application that allows you to send text from your iPhone clipboard to your Windows 11 PC over HTTP.

## Features

- HTTP server running on port 5019
- System tray integration with quit option
- Accepts JSON POST requests to copy text to Windows clipboard
- Simple and lightweight implementation

## Setup

### 1. Create Virtual Environment

```powershell
py -3 -m venv .venv
```

### 2. Activate Virtual Environment

```powershell
.venv\Scripts\activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

## Usage

### Running the Application

```powershell
python app.py
```

The application will:
- Start an HTTP server on `http://0.0.0.0:5019`
- Create a system tray icon
- Wait for clipboard requests

To quit the application, right-click the system tray icon and select "Quit", or press `Ctrl+C` in the terminal.

### Testing with curl

You can test the application using curl:

```powershell
curl -X POST http://127.0.0.1:5019/clip -H "Content-Type: application/json" -d "{\"text\":\"hello\"}"
```

This will copy "hello" to your Windows clipboard.

## iPhone Shortcut Setup

To create an iPhone Shortcut that sends your clipboard to the PC:

### 1. Create New Shortcut

1. Open the **Shortcuts** app on your iPhone
2. Tap the **+** button to create a new shortcut
3. Name it "Send to PC Clipboard" or similar

### 2. Add Actions

Add the following actions in order:

1. **Get Clipboard** (from Apps > Shortcuts)
   - This gets the current clipboard content

2. **Get Text from Input** (from Text)
   - This ensures the clipboard content is treated as text

3. **Get My Shortcuts** (from Apps > Shortcuts) - Skip this step
   
   Instead, add **Text** action:
   - Add a **Text** action
   - Set the text to:
   ```json
   {"text":"CLIPBOARD_CONTENT"}
   ```
   - Tap on "CLIPBOARD_CONTENT" and replace it with the output from "Get Clipboard" (tap the magic variable)

4. **Get Contents of URL** (from Web)
   - **URL**: `http://YOUR_PC_IP_ADDRESS:5019/clip`
   - **Method**: POST
   - **Headers**: 
     - Add header: `Content-Type` = `application/json`
   - **Request Body**: Choose "Text" and select the JSON text from step 3

### 3. Replace IP Address

Replace `YOUR_PC_IP_ADDRESS` with your Windows PC's actual IP address on your local network. You can find this by running `ipconfig` in Command Prompt and looking for your IPv4 address.

### 4. Test the Shortcut

1. Copy some text on your iPhone
2. Run the shortcut
3. Check if the text appears in your PC's clipboard

### 5. Add to Home Screen (Optional)

You can add the shortcut to your iPhone's home screen for quick access:

1. In the Shortcuts app, tap the shortcut
2. Tap the settings icon (three dots)
3. Tap "Add to Home Screen"
4. Customize the icon and name if desired

## API Endpoint

### POST /clip

Copies text to the Windows clipboard.

**Request:**
```json
{
  "text": "Text to copy to clipboard"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Text copied to clipboard"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid JSON or missing 'text' field
- `404 Not Found`: Invalid endpoint
- `500 Internal Server Error`: Server error

## Network Configuration

The server binds to `0.0.0.0:5019`, making it accessible from other devices on your local network. Make sure:

1. Your Windows firewall allows incoming connections on port 5019
2. Your iPhone and PC are on the same network
3. You use your PC's actual IP address in the iPhone shortcut

To find your PC's IP address:
```powershell
ipconfig
```

Look for the IPv4 address under your active network adapter.

## Troubleshooting

### Firewall Issues
If the connection fails, you may need to allow the app through Windows Firewall:
1. Go to Windows Security > Firewall & network protection
2. Click "Allow an app through firewall"
3. Add Python or the specific port 5019

### Network Issues
- Ensure both devices are on the same Wi-Fi network
- Try pinging your PC from another device to verify network connectivity
- Check if other apps can access your PC on the same network

### Clipboard Issues
- The app uses `pyperclip` which should work with most Windows clipboard implementations
- If clipboard operations fail, try running the app as administrator

## Dependencies

- **pystray**: System tray integration
- **pyperclip**: Clipboard operations
- **Pillow**: Image creation for tray icon

## License

This project is provided as-is for personal use.
