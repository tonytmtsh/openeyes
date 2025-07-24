# OpenEyes Bluetooth Scripts

Two simple Python scripts for Bluetooth communication to send alarm commands
between devices.

## Scripts

### `simple_server.py`

- Bluetooth server that accepts connections
- Receives "SOUND ALARM" and "QUIET ALARM" commands
- Interactive mode for sending commands to client
- Tracks alarm state (SOUND/QUIET)

### `simple_client.py`

- Bluetooth client that connects to server
- Discovers nearby Bluetooth devices
- Sends alarm commands to server
- Interactive mode for real-time communication

### `setup_bluetooth.py`

- Automated setup script for Bluetooth dependencies
- Installs platform-specific requirements
- Tests Bluetooth functionality

## Installation

### 1. Run the setup script (recommended):

```bash
/Users/tonythornton/source/python/openeyes/.venv/bin/python setup_bluetooth.py
```

### 2. Manual installation:

**macOS:**

```bash
brew install pkg-config
pip install pybluez
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get update
sudo apt-get install bluetooth libbluetooth-dev
pip install pybluez
```

**Windows:**

```bash
pip install pybluez
```

## Usage

### 1. Start the server (on first device):

```bash
/Users/tonythornton/source/python/openeyes/.venv/bin/python simple_server.py
```

### 2. Start the client (on second device):

```bash
/Users/tonythornton/source/python/openeyes/.venv/bin/python simple_client.py
```

### 3. Interactive Commands:

- `sound` - Send "SOUND ALARM" command
- `quiet` - Send "QUIET ALARM" command
- `status` - Check current alarm status
- `quit` - Disconnect and exit
- `help` - Show available commands

## Message Protocol

The scripts use a simple text-based protocol:

**Commands:**

- `SOUND ALARM` - Activate alarm
- `QUIET ALARM` - Deactivate alarm
- `STATUS` - Request current status
- `QUIT` - Disconnect

**Responses:**

- `ALARM SOUNDING` - Alarm is active
- `ALARM QUIET` - Alarm is inactive
- `ALARM ACKNOWLEDGED` - Command received
- `QUIET ACKNOWLEDGED` - Quiet command received

## Integration with OpenEyes

These Bluetooth scripts can be integrated with the main `simple_openeyes.py`
script:

1. **Server mode**: Run on the device with the camera
2. **Client mode**: Run on a remote device to trigger alarms
3. **Eye state trigger**: Modify `simple_openeyes.py` to send Bluetooth commands
   when eyes close

Example integration in `simple_openeyes.py`:

```python
# In the eye state analysis function
if eye_state == "CLOSED":
    # Send Bluetooth alarm command
    bluetooth_client.send_message("SOUND ALARM")
elif eye_state == "OPEN":
    # Send Bluetooth quiet command
    bluetooth_client.send_message("QUIET ALARM")
```

## Troubleshooting

### Common Issues:

1. **Import Error**: `ImportError: No module named 'bluetooth'`
   - Run the setup script or install pybluez manually

2. **Permission Denied** (Linux):
   - Add user to bluetooth group: `sudo usermod -a -G bluetooth $USER`
   - Restart session

3. **No Devices Found**:
   - Enable Bluetooth on both devices
   - Make devices discoverable
   - Check Bluetooth is enabled in system settings

4. **Connection Failed**:
   - Ensure devices are paired (optional but recommended)
   - Check firewall settings
   - Verify Bluetooth service is running

### macOS Specific:

- May need to allow Python Bluetooth access in System Preferences > Security &
  Privacy
- Some macOS versions have restrictions on Bluetooth discovery

### Windows Specific:

- Bluetooth support may be limited depending on hardware
- May need additional drivers or software

## Features

- **Auto-discovery**: Client automatically finds available Bluetooth devices
- **Interactive mode**: Real-time command sending
- **Error handling**: Robust connection management
- **Cross-platform**: Works on macOS, Linux, and Windows
- **Simple protocol**: Easy to extend and modify
- **Thread-safe**: Concurrent message handling
