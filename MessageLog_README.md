# OpenTX Message Log Display

A Lua telemetry script that displays scrolling text messages received via USB serial. This allows external applications to send status messages, logs, or notifications to be displayed on the OpenTX radio screen.

## Features

- **Scrolling message display**: Shows up to 7 messages (18 on Horus) with automatic scrolling
- **USB Serial communication**: Receives messages via USB serial connection
- **Simple text protocol**: Easy to integrate with any application
- **Multiple radio support**: Works on Taranis X9, X7, Tango, and Horus radios
- **Real-time updates**: Messages appear immediately on the display

## Installation

### Quick Setup

**🚀 Automated Setup (Recommended):**
```bash
cd /home/ben/opentx
./setup_sd_card.sh
```

**📋 Manual Setup:**
1. **Mount your SD card** on computer
2. **Create folder**: `SCRIPTS/TELEMETRY/` on SD card
3. **Copy script**: Copy the appropriate `msglog.lua` from:
   - `radio/sdcard/taranis-x9/` for X9D, X9D+, X9E  
   - `radio/sdcard/taranis-x7/` for X7, X7S
   - `radio/sdcard/horus/` for Jumper T16/T18
   - `radio/sdcard/tango/` for Tango 2
4. **Insert SD card** into radio and power on

See `SD_CARD_SETUP.md` for detailed setup instructions.

### 1. Copy the Lua Script

The msglog.lua scripts are located in the OpenTX repository at:

- **Taranis X9**: `radio/sdcard/taranis-x9/SCRIPTS/TELEMETRY/msglog.lua`
- **Taranis X7**: `radio/sdcard/taranis-x7/SCRIPTS/TELEMETRY/msglog.lua` 
- **Tango**: `radio/sdcard/tango/SCRIPTS/TELEMETRY/msglog.lua`
- **Horus**: `radio/sdcard/horus/SCRIPTS/TELEMETRY/msglog.lua`

Copy to your SD card's `/SCRIPTS/TELEMETRY/msglog.lua` location.

### 2. Activate the Script

#### Method 1: Via Display Menu (Recommended)
1. Go to **MODEL** menu → **DISPLAY**
2. Select a telemetry screen (Screen 1, 2, or 3)
3. Change **Type** to **Script**
4. Select **msglog** from the script list
5. Navigate to the telemetry view and press **DISP** to cycle to your message screen

#### Method 2: Via Special Function (Button Activation)
1. Go to **MODEL** menu → **SPECIAL FUNCTIONS**
2. Find an empty function slot
3. Set **Switch** to desired button/switch (e.g., SA↑)
4. Set **Function** to **Play Script**
5. Set **Script** to **msglog**

### 3. Configure USB Mode

Make sure your radio is in the correct USB mode:
- **Debug builds**: USB Serial Mode
- **Release builds**: USB Telemetry Mirror Mode

## Protocol

The message log uses a simple text-based protocol over USB serial:

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `text\n` | Add message "text" | `Hello World\n` |
| `MSG:text\n` | Add message "text" (explicit) | `MSG:Status OK\n` |
| `CLEAR\n` | Clear all messages | `CLEAR\n` |

### Message Format
- Each message must end with newline (`\n`) or carriage return + newline (`\r\n`)
- Messages longer than display width are automatically truncated with "..."
- Only the most recent messages are kept (older messages scroll off)

## Usage Examples

### Python Client

A Python client is provided (`message_client.py`):

```bash
# Install requirements
pip install pyserial

# Send a single message
python3 message_client.py --message "Hello from Python"

# Interactive mode
python3 message_client.py --interactive

# Send test messages
python3 message_client.py --test

# Clear all messages
python3 message_client.py --clear
```

### Command Line (Linux/Mac)

```bash
# Send a message
echo "Hello World" > /dev/ttyACM0

# Send multiple messages
echo -e "Line 1\nLine 2\nLine 3" > /dev/ttyACM0

# Clear messages
echo "CLEAR" > /dev/ttyACM0
```

### Arduino/Embedded

```cpp
void sendMessage(const char* msg) {
    Serial.print(msg);
    Serial.print('\n');
}

void setup() {
    Serial.begin(115200);
    sendMessage("System initialized");
    sendMessage("GPS: Searching...");
}

void loop() {
    static int counter = 0;
    char buffer[64];
    sprintf(buffer, "Loop count: %d", counter++);
    sendMessage(buffer);
    delay(1000);
}
```

## Display Layout

### Monochrome Radios (X9/X7/Tango)
```
┌──────────────────────┐
│ Message Log    12:34 │ ← Header (inverted)
├──────────────────────┤
│ [12:34:56] Msg 1     │ ← Message with timestamp
│ [12:34:57] Msg 2     │
│ [12:34:58] Msg 3     │
│ ...                  │
│ [12:35:05] Msg 7     │ ← Up to 7 messages
└──────────────────────┘
```

### Color Radios (Horus)
```
┌────────────────────────────────────────┐
│ Message Log                      12:34 │ ← Blue header
├────────────────────────────────────────┤
│ [12:34:56] System initialized          │ ← Alternating row colors
│ [12:34:57] GPS: 12 satellites found    │
│ [12:34:58] Battery voltage: 12.4V      │
│ ...                                    │
│ [12:35:05] Message 18                  │ ← Up to 18 messages
├────────────────────────────────────────┤
│ Long EXIT to return to main view       │ ← Footer
└────────────────────────────────────────┘
```

## Integration Examples

### Flight Controller Status
```python
def send_flight_status():
    send_message(f"Mode: {flight_mode}")
    send_message(f"Alt: {altitude}m")
    send_message(f"Bat: {battery_voltage}V")
    if battery_voltage < 11.0:
        send_message("WARNING: Low battery!")
```

### Build System Notifications
```bash
#!/bin/bash
# Send build status to radio
if make; then
    echo "Build: SUCCESS" > /dev/ttyACM0
else
    echo "Build: FAILED" > /dev/ttyACM0
fi
```

### Server Monitoring
```python
def check_server_status():
    if ping_server():
        send_message("Server: Online ✓")
    else:
        send_message("Server: OFFLINE ✗")
```

## Troubleshooting

### Script Not Loading
- Check that script is in correct `/SCRIPTS/TELEMETRY/` folder
- Verify script name is exactly `msglog.lua`
- Check for syntax errors in script

### No Messages Received
- Verify USB mode is set correctly (USB Serial or USB Telemetry Mirror)
- Check serial port permissions (`sudo chmod 666 /dev/ttyACM0`)
- Try different baud rate (usually 115200)
- Ensure newlines are being sent (`\n`)
- **For CLI-enabled builds**: Enable Lua serial forwarding (see CLI Builds section below)

### Messages Not Displaying
- Make sure telemetry script is selected and active
- Press DISP button to cycle through telemetry screens
- Check that radio is not in a menu (must be on main view)

### Connection Issues
```bash
# Check if radio is detected
ls /dev/ttyACM*

# Check USB mode
dmesg | grep -i usb

# Test basic connection
echo "test" > /dev/ttyACM0
```

### CLI Builds

If you're using a build with CLI (Command Line Interface) enabled, you need to explicitly enable Lua serial forwarding:

1. Connect to radio via USB serial terminal
2. Enable Lua serial mode:
   ```
   luaserial on
   ```
3. To disable (back to CLI-only mode):
   ```
   luaserial off
   ```

**Note**: In CLI builds, USB serial data normally goes only to the CLI interface. The `luaserial` command enables forwarding a copy of the data to Lua scripts while keeping CLI functionality intact.

## Technical Details

- **Update rate**: Messages are checked every 200ms
- **Memory usage**: Minimal, only stores visible messages
- **Character limits**: ~20 chars (mono) / ~60 chars (color) per line
- **Protocol**: Plain text over USB CDC (Serial over USB)
- **Thread safety**: Not required, Lua scripts run single-threaded

## Customization

You can modify the script to:
- Change maximum number of messages (`maxLines`)
- Adjust update interval (`updateInterval`)
- Customize display format and colors
- Add message filtering or priorities
- Implement additional commands

The script is designed to be simple and easily extensible for your specific use case.