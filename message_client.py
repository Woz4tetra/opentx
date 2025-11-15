#!/usr/bin/env python3
"""
Message Log Client - Send text messages to OpenTX Message Log display
Sends messages via USB serial to the OpenTX message log telemetry script

Installation:
    pip install pyserial

Usage:
    python3 message_client.py [options]
    
Options:
    --port PORT     Serial port (default: /dev/ttyACM0)
    --message MSG   Send a single message and exit
    --interactive   Interactive mode - type messages
    --test          Send test messages
    --clear         Clear all messages and exit

Protocol:
    MSG:text\n      - Add message "text"
    text\n          - Add message "text" (implicit MSG command)  
    CLEAR\n         - Clear all messages
"""

import serial
import time
import sys
import argparse
from datetime import datetime

class MessageClient:
    def __init__(self, port='/dev/ttyACM0', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        
    def connect(self):
        """Connect to the OpenTX radio via USB serial"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"Connected to {self.port} at {self.baudrate} baud")
            time.sleep(2)  # Give time for connection to establish
            return True
        except Exception as e:
            print(f"Failed to connect to {self.port}: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from the radio"""
        if self.ser:
            self.ser.close()
            print("Disconnected")
            
    def send_message(self, message):
        """Send a message to the radio"""
        if not self.ser:
            print("Not connected")
            return False
            
        try:
            # Add timestamp to message
            timestamp = datetime.now().strftime("%H:%M:%S")
            full_message = f"[{timestamp}] {message}"
            
            # Send the message
            data = full_message + '\n'
            self.ser.write(data.encode('utf-8'))
            print(f"Sent: {full_message}")
            return True
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False
            
    def clear_messages(self):
        """Clear all messages on the radio"""
        if not self.ser:
            print("Not connected")
            return False
            
        try:
            self.ser.write(b'CLEAR\n')
            print("Cleared all messages")
            return True
        except Exception as e:
            print(f"Failed to clear messages: {e}")
            return False
            
    def send_test_messages(self):
        """Send a series of test messages"""
        test_messages = [
            "System initialized",
            "GPS: 12 satellites",
            "Battery: 12.4V",
            "Flight mode: ARMED",
            "Takeoff complete",
            "Altitude: 100m",
            "Warning: Low battery",
            "Landing initiated",
            "System disarmed"
        ]
        
        for i, msg in enumerate(test_messages):
            if self.send_message(f"{i+1:02d}: {msg}"):
                time.sleep(0.5)  # Small delay between messages
            else:
                break
                
    def interactive_mode(self):
        """Interactive mode - user can type messages"""
        print("\n=== Interactive Message Mode ===")
        print("Type messages and press Enter to send")
        print("Commands:")
        print("  /clear  - Clear all messages")
        print("  /test   - Send test messages") 
        print("  /exit   - Exit")
        print("=====================================")
        
        try:
            while True:
                message = input("> ")
                
                if message.lower() == "/exit":
                    break
                elif message.lower() == "/clear":
                    self.clear_messages()
                elif message.lower() == "/test":
                    self.send_test_messages()
                elif message.strip():
                    self.send_message(message)
                    
        except KeyboardInterrupt:
            print("\nExiting...")

def main():
    parser = argparse.ArgumentParser(description="Send messages to OpenTX Message Log")
    parser.add_argument('--port', default='/dev/ttyACM0', help='Serial port')
    parser.add_argument('--baudrate', type=int, default=115200, help='Baud rate')
    parser.add_argument('--message', help='Send a single message and exit')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--test', action='store_true', help='Send test messages')
    parser.add_argument('--clear', action='store_true', help='Clear messages and exit')
    
    args = parser.parse_args()
    
    # Create client
    client = MessageClient(args.port, args.baudrate)
    
    # Connect
    if not client.connect():
        sys.exit(1)
        
    try:
        if args.clear:
            client.clear_messages()
        elif args.message:
            client.send_message(args.message)
        elif args.test:
            client.send_test_messages()
        elif args.interactive:
            client.interactive_mode()
        else:
            # Default to interactive mode
            client.interactive_mode()
            
    finally:
        client.disconnect()

if __name__ == '__main__':
    main()