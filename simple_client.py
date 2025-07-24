#!/usr/bin/env python3
"""
Simple Bluetooth Client - Connects to server and sends alarm messages
"""

import bluetooth
import threading
import time
import sys

class BluetoothClient:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.running = False
        
    def discover_devices(self):
        """Discover nearby Bluetooth devices"""
        print("🔍 Discovering Bluetooth devices...")
        try:
            devices = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True)
            
            if not devices:
                print("❌ No Bluetooth devices found")
                return []
            
            print(f"📱 Found {len(devices)} device(s):")
            for i, (address, name) in enumerate(devices):
                print(f"  {i+1}. {name} ({address})")
            
            return devices
        
        except bluetooth.BluetoothError as e:
            print(f"❌ Error discovering devices: {e}")
            return []
    
    def connect_to_server(self, server_address=None):
        """Connect to Bluetooth server"""
        try:
            if not server_address:
                # Discover devices and let user choose
                devices = self.discover_devices()
                if not devices:
                    return False
                
                # Let user select device
                while True:
                    try:
                        choice = input("\nSelect device number (or 'q' to quit): ").strip()
                        if choice.lower() == 'q':
                            return False
                        
                        device_index = int(choice) - 1
                        if 0 <= device_index < len(devices):
                            server_address = devices[device_index][0]
                            break
                        else:
                            print("❌ Invalid selection")
                    except ValueError:
                        print("❌ Please enter a valid number")
            
            print(f"🔗 Connecting to {server_address}...")
            
            # Create socket and connect
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            
            # Try to find the service
            services = bluetooth.find_service(address=server_address)
            if not services:
                print("❌ No services found on target device")
                return False
            
            # Connect to first available service (usually port 1)
            port = services[0]["port"] if services else 1
            self.socket.connect((server_address, port))
            
            self.connected = True
            self.running = True
            print(f"✅ Connected to server on port {port}")
            
            return True
            
        except bluetooth.BluetoothError as e:
            print(f"❌ Bluetooth connection error: {e}")
            return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def send_message(self, message):
        """Send message to server"""
        if not self.connected or not self.socket:
            print("❌ Not connected to server")
            return False
            
        try:
            self.socket.send(message.encode('utf-8'))
            print(f"📤 Sent: {message}")
            
            # Wait for response
            response = self.socket.recv(1024).decode('utf-8').strip()
            print(f"📨 Response: {response}")
            
            return True
            
        except bluetooth.BluetoothError as e:
            print(f"❌ Error sending message: {e}")
            self.connected = False
            return False
    
    def listen_for_messages(self):
        """Listen for incoming messages from server"""
        try:
            while self.running and self.connected:
                try:
                    data = self.socket.recv(1024).decode('utf-8').strip()
                    if not data:
                        break
                        
                    print(f"📨 Server says: {data}")
                    
                    # Auto-respond to server commands
                    if data == "SOUND ALARM":
                        print("🚨 ALARM COMMAND RECEIVED!")
                        response = "ALARM ACKNOWLEDGED"
                    elif data == "QUIET ALARM":
                        print("🔇 QUIET COMMAND RECEIVED!")
                        response = "QUIET ACKNOWLEDGED"
                    else:
                        response = "MESSAGE RECEIVED"
                    
                    # Send acknowledgment
                    self.socket.send(response.encode('utf-8'))
                    
                except bluetooth.BluetoothError:
                    print("📱 Server disconnected")
                    break
                    
        except Exception as e:
            print(f"❌ Error in message listener: {e}")
        finally:
            self.connected = False
    
    def interactive_mode(self):
        """Interactive command mode"""
        print("\n🎮 Interactive Mode:")
        print("Commands: 'sound', 'quiet', 'status', 'quit'")
        
        # Start listener thread
        listener_thread = threading.Thread(target=self.listen_for_messages)
        listener_thread.daemon = True
        listener_thread.start()
        
        while self.connected:
            try:
                cmd = input("Client> ").strip().lower()
                
                if cmd == 'sound':
                    self.send_message("SOUND ALARM")
                elif cmd == 'quiet':
                    self.send_message("QUIET ALARM")
                elif cmd == 'status':
                    self.send_message("STATUS")
                elif cmd == 'quit':
                    self.send_message("QUIT")
                    break
                elif cmd == 'help':
                    print("Commands: sound, quiet, status, quit, help")
                elif cmd == '':
                    continue
                else:
                    # Send custom message
                    self.send_message(cmd.upper())
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        
        self.running = False
    
    def cleanup(self):
        """Clean up connection"""
        if self.socket:
            self.socket.close()
        self.connected = False
        print("🧹 Client cleaned up")

def main():
    """Main client function"""
    print("📱 OpenEyes Bluetooth Client")
    print("=" * 40)
    
    client = BluetoothClient()
    
    try:
        # Connect to server
        if not client.connect_to_server():
            print("❌ Failed to connect to server")
            return
        
        # Start interactive mode
        client.interactive_mode()
        
    except KeyboardInterrupt:
        print("\n⏹️  Client shutting down...")
    
    except Exception as e:
        print(f"❌ Client error: {e}")
    
    finally:
        client.cleanup()

if __name__ == "__main__":
    # Check if bluetooth module is available
    try:
        import bluetooth
    except ImportError:
        print("❌ Error: pybluez module not installed")
        print("Install with: pip install pybluez")
        print("\nOn macOS, you may also need:")
        print("  brew install pkg-config")
        print("  pip install pybluez")
        sys.exit(1)
    
    main()
