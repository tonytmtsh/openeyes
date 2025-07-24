#!/usr/bin/env python3
"""
Simple Bluetooth Server - Receives and sends alarm messages
"""

import bluetooth
import threading
import time
import sys

class BluetoothServer:
    def __init__(self):
        self.server_socket = None
        self.client_socket = None
        self.running = False
        self.alarm_state = False  # False = QUIET, True = SOUND
        
    def start_server(self):
        """Start the Bluetooth server"""
        try:
            # Create Bluetooth socket
            self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            
            # Bind to any available port
            port = bluetooth.PORT_ANY
            self.server_socket.bind(("", port))
            
            # Get the port that was assigned
            port = self.server_socket.getsockname()[1]
            
            # Listen for connections
            self.server_socket.listen(1)
            
            print(f"🔵 Bluetooth Server started on port {port}")
            print("📱 Waiting for client connection...")
            
            # Make server discoverable
            bluetooth.advertise_service(
                self.server_socket,
                "OpenEyes Alarm Server",
                service_id="00001101-0000-1000-8000-00805F9B34FB",  # Standard RFCOMM UUID
                service_classes=[bluetooth.SERIAL_PORT_CLASS],
                profiles=[bluetooth.SERIAL_PORT_PROFILE]
            )
            
            self.running = True
            
            # Accept client connection
            self.client_socket, client_info = self.server_socket.accept()
            print(f"✅ Client connected: {client_info}")
            
            # Start message handling
            self.handle_messages()
            
        except bluetooth.BluetoothError as e:
            print(f"❌ Bluetooth error: {e}")
        except Exception as e:
            print(f"❌ Error starting server: {e}")
        finally:
            self.cleanup()
    
    def handle_messages(self):
        """Handle incoming messages from client"""
        try:
            while self.running:
                # Receive message
                try:
                    data = self.client_socket.recv(1024).decode('utf-8').strip()
                    if not data:
                        break
                        
                    print(f"📨 Received: {data}")
                    
                    # Process commands
                    if data == "SOUND ALARM":
                        self.alarm_state = True
                        print("🚨 ALARM ACTIVATED!")
                        response = "ALARM SOUNDING"
                    elif data == "QUIET ALARM":
                        self.alarm_state = False
                        print("🔇 ALARM QUIETED")
                        response = "ALARM QUIET"
                    elif data == "STATUS":
                        response = "ALARM SOUNDING" if self.alarm_state else "ALARM QUIET"
                    elif data == "QUIT":
                        print("👋 Client requested disconnect")
                        break
                    else:
                        response = f"UNKNOWN COMMAND: {data}"
                    
                    # Send response
                    self.client_socket.send(response.encode('utf-8'))
                    print(f"📤 Sent: {response}")
                    
                except bluetooth.BluetoothError:
                    print("📱 Client disconnected")
                    break
                    
        except KeyboardInterrupt:
            print("\n⏹️  Server interrupted by user")
        finally:
            self.running = False
    
    def send_command(self, command):
        """Send command to client (for interactive mode)"""
        if self.client_socket:
            try:
                self.client_socket.send(command.encode('utf-8'))
                print(f"📤 Sent: {command}")
                
                # Wait for response
                response = self.client_socket.recv(1024).decode('utf-8').strip()
                print(f"📨 Response: {response}")
                
            except bluetooth.BluetoothError as e:
                print(f"❌ Error sending command: {e}")
    
    def interactive_mode(self):
        """Interactive command mode"""
        print("\n🎮 Interactive Mode:")
        print("Commands: 'sound', 'quiet', 'status', 'quit'")
        
        while self.running and self.client_socket:
            try:
                cmd = input("Server> ").strip().lower()
                
                if cmd == 'sound':
                    self.send_command("SOUND ALARM")
                elif cmd == 'quiet':
                    self.send_command("QUIET ALARM")
                elif cmd == 'status':
                    self.send_command("STATUS")
                elif cmd == 'quit':
                    self.send_command("QUIT")
                    break
                elif cmd == 'help':
                    print("Commands: sound, quiet, status, quit, help")
                else:
                    print("Unknown command. Type 'help' for commands.")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
    
    def cleanup(self):
        """Clean up connections"""
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        print("🧹 Server cleaned up")

def main():
    """Main server function"""
    print("🔵 OpenEyes Bluetooth Server")
    print("=" * 40)
    
    server = BluetoothServer()
    
    try:
        # Start server in a separate thread
        server_thread = threading.Thread(target=server.start_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait for connection
        while not server.client_socket and server_thread.is_alive():
            time.sleep(0.1)
        
        if server.client_socket:
            # Start interactive mode
            server.interactive_mode()
        
        # Wait for server thread to finish
        server.running = False
        server_thread.join(timeout=2)
        
    except KeyboardInterrupt:
        print("\n⏹️  Server shutting down...")
        server.running = False
    
    except Exception as e:
        print(f"❌ Server error: {e}")
    
    finally:
        server.cleanup()

if __name__ == "__main__":
    # Check if bluetooth module is available
    try:
        import bluetooth
    except ImportError:
        print("❌ Error: pybluez module not installed")
        print("Install with: pip install pybluez")
        sys.exit(1)
    
    main()
