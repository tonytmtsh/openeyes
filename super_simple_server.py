#!/usr/bin/env python3
"""
Super Simple Network Server
Same concept as Bluetooth but using WiFi/network
"""

import socket

# Create a network socket (much simpler than Bluetooth)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8888))
server_socket.listen(1)

print("🌐 Network server listening on localhost:8888")
print("Waiting for connection...")

# Accept connection
client_socket, client_address = server_socket.accept()
print(f"✅ Connected to {client_address}")

# Message loop
try:
    while True:
        # Receive message
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break
            
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
