#!/usr/bin/env python3
"""
Setup Bluetooth Dependencies - Install required packages for Bluetooth scripts
"""

import subprocess
import sys
import platform

def run_command(cmd, description):
    """Run a system command and return success status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def install_bluetooth_dependencies():
    """Install Bluetooth dependencies based on the operating system"""
    system = platform.system().lower()
    
    print(f"🖥️  Detected OS: {system}")
    
    if system == "darwin":  # macOS
        print("\n📦 Installing macOS Bluetooth dependencies...")
        
        # Check if Homebrew is installed
        if subprocess.run("which brew", shell=True, capture_output=True).returncode != 0:
            print("❌ Homebrew not found. Please install Homebrew first:")
            print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            return False
        
        # Install pkg-config (required for pybluez on macOS)
        if not run_command("brew install pkg-config", "Installing pkg-config"):
            return False
        
        # Install pybluez
        if not run_command("pip install pybluez", "Installing pybluez"):
            return False
            
    elif system == "linux":
        print("\n📦 Installing Linux Bluetooth dependencies...")
        
        # Install bluez development libraries
        if not run_command("sudo apt-get update", "Updating package list"):
            return False
            
        if not run_command("sudo apt-get install -y bluetooth libbluetooth-dev", "Installing Bluetooth libraries"):
            return False
        
        # Install pybluez
        if not run_command("pip install pybluez", "Installing pybluez"):
            return False
            
    elif system == "windows":
        print("\n📦 Installing Windows Bluetooth dependencies...")
        print("⚠️  Note: Bluetooth support on Windows may be limited")
        
        # Install pybluez (Windows version)
        if not run_command("pip install pybluez", "Installing pybluez"):
            return False
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False
    
    return True

def test_bluetooth_import():
    """Test if bluetooth module can be imported"""
    print("\n🧪 Testing Bluetooth import...")
    try:
        import bluetooth
        print("✅ Bluetooth module imported successfully")
        
        # Try to get local Bluetooth adapter
        try:
            adapter = bluetooth.read_local_bdaddr()
            print(f"📡 Local Bluetooth adapter: {adapter[0]}")
        except:
            print("⚠️  Could not read local Bluetooth adapter (may be disabled)")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import bluetooth module: {e}")
        return False

def main():
    """Main setup function"""
    print("🔵 OpenEyes Bluetooth Setup")
    print("=" * 40)
    
    # Install dependencies
    if not install_bluetooth_dependencies():
        print("\n❌ Failed to install Bluetooth dependencies")
        sys.exit(1)
    
    # Test import
    if not test_bluetooth_import():
        print("\n❌ Bluetooth setup incomplete")
        print("You may need to:")
        print("  1. Enable Bluetooth on your system")
        print("  2. Restart your terminal/IDE")
        print("  3. Check system permissions")
        sys.exit(1)
    
    print("\n✅ Bluetooth setup completed successfully!")
    print("\nYou can now run:")
    print(f"  {sys.executable} simple_server.py")
    print(f"  {sys.executable} simple_client.py")

if __name__ == "__main__":
    main()
