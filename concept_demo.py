#!/usr/bin/env python3
"""
Minimal Communication Demo - Shows the basic concept in one file
Run this, then look at the code to understand how it works
"""

def demo_communication():
    """Shows how two programs would talk to each other"""
    
    print("🤖 Simulating two programs talking:")
    print("=" * 40)
    
    # Simulate messages between programs
    messages = [
        ("Client", "SOUND ALARM"),
        ("Server", "🚨 ALARM ON!"),
        ("Client", "QUIET ALARM"), 
        ("Server", "🔇 ALARM OFF"),
        ("Client", "Hello"),
        ("Server", "👍 Got it")
    ]
    
    for sender, message in messages:
        print(f"{sender:6s} → {message}")
    
    print("\n📝 That's the basic concept!")
    print("   One program sends messages")
    print("   Another program responds")
    print("\n🔧 In real code:")
    print("   1. Server: listens for messages")
    print("   2. Client: sends messages")
    print("   3. Both: encode/decode text")

def show_code_example():
    """Shows the core code concept"""
    print("\n💻 Core concept in 10 lines:")
    print("-" * 30)
    
    code = '''
# Server side (simplified):
message = receive_message()
if message == "SOUND ALARM":
    send_response("🚨 ALARM ON!")

# Client side (simplified):  
send_message("SOUND ALARM")
response = receive_response()
print(response)  # Shows: 🚨 ALARM ON!
'''
    print(code)

if __name__ == "__main__":
    print("🎯 Understanding Program Communication")
    print("=" * 50)
    
    demo_communication()
    show_code_example()
    
    print("\n🚀 Ready to try the real scripts:")
    print("   python super_simple_server.py")
    print("   python super_simple_client.py")
