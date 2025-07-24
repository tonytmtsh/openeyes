# Ultra-Simple Communication Scripts

These are the **simplest possible** scripts to show communication between two
programs.

## The Easy Way - Network Scripts (Recommended to start)

### `super_simple_server.py` (25 lines)

- Creates a server that listens for messages
- Responds to "SOUND ALARM" and "QUIET ALARM"
- Uses regular WiFi/network (no Bluetooth setup needed)

### `super_simple_client.py` (23 lines)

- Connects to the server
- Sends messages when you type commands
- Shows responses

### How to run (2 terminals):

**Terminal 1:**

```bash
python super_simple_server.py
```

**Terminal 2:**

```bash
python super_simple_client.py
```

Then type: `sound`, `quiet`, or `quit`

---

## The Bluetooth Way (if you want Bluetooth)

### `ultra_simple_server.py` (35 lines)

- Same idea but uses Bluetooth instead of WiFi
- Requires `pip install pybluez`

### `ultra_simple_client.py` (30 lines)

- Connects via Bluetooth
- You need to change the server address in the code

---

## Key Differences:

### Network Version (Super Simple):

- ✅ Works immediately, no setup
- ✅ Both programs run on same computer
- ✅ Just uses `socket` (built into Python)

### Bluetooth Version (Ultra Simple):

- 📱 Works between different devices
- 🔧 Needs `pybluez` installation
- 📍 Need to find device addresses

---

## The Core Concept:

Both do the **exact same thing**:

1. **Server**: Waits for messages, sends back responses
2. **Client**: Sends messages, shows responses
3. **Messages**: "SOUND ALARM" and "QUIET ALARM"

**That's it!** Just 25 lines of code to understand communication between
programs.

## Integration with OpenEyes:

Add these 3 lines to your `simple_openeyes.py`:

```python
# At the top
import socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 8888))

# In your eye detection loop
if eye_state == "CLOSED":
    client.send("SOUND ALARM".encode('utf-8'))
elif eye_state == "OPEN":  
    client.send("QUIET ALARM".encode('utf-8'))
```

Now your eye detection can trigger alarms on another device!
