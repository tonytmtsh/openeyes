#!/usr/bin/env python3
"""
Super Simple Network Client
Same concept as Bluetooth but using WiFi/network
"""

import socket

# Connect to server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 8888))

print("✅ Connected to server!")

# Command loop
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
