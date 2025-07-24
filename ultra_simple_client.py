#!/usr/bin/env python3
"""
Ultra-Simple Bluetooth Client
Just connects and sends messages
"""

import bluetooth

# Server address (you'll need to change this to your server's address)
# You can find it by running: hcitool scan
server_address = "AA:BB:CC:DD:EE:FF"  # Replace with actual address
port = 1

print("🔍 Connecting to Bluetooth server...")

# Create socket and connect
client_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
client_socket.connect((server_address, port))

print("✅ Connected!")

# Simple command loop
try:
    while True:
        # Get user input
        command = input("Enter command (sound/quiet/quit): ").lower()
        
        if command == "quit":
            break
        elif command == "sound":
            message = "SOUND ALARM"
        elif command == "quiet":
            message = "QUIET ALARM"
        else:
            message = command.upper()
        
        # Send message
        client_socket.send(message.encode('utf-8'))
        print(f"📤 Sent: {message}")
        
        # Get response
        response = client_socket.recv(1024).decode('utf-8')
        print(f"📨 Response: {response}")

except KeyboardInterrupt:
    print("\n👋 Client shutting down")

# Cleanup
client_socket.close()
