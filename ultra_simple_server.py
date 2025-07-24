#!/usr/bin/env python3
"""
Ultra-Simple Bluetooth Server
Just receives messages and prints them
"""

import bluetooth

# Create a Bluetooth socket
server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

# Bind to any port
server_socket.bind(("", bluetooth.PORT_ANY))
port = server_socket.getsockname()[1]

# Listen for connections
server_socket.listen(1)

print(f"🔵 Bluetooth server listening on port {port}")
print("Waiting for connection...")

# Accept a connection
client_socket, client_info = server_socket.accept()
print(f"✅ Connected to {client_info}")

# Simple message loop
try:
    while True:
        # Receive message
        message = client_socket.recv(1024).decode('utf-8')
        print(f"📨 Received: {message}")
        
        # Send response
        if message == "SOUND ALARM":
            response = "🚨 ALARM ON!"
        elif message == "QUIET ALARM":
            response = "🔇 ALARM OFF"
        else:
            response = "👍 Got it"
            
        client_socket.send(response.encode('utf-8'))
        print(f"📤 Sent: {response}")

except KeyboardInterrupt:
    print("\n👋 Server shutting down")

# Cleanup
client_socket.close()
server_socket.close()
