#!/usr/bin/env python3
"""
Test script to verify CLI luaserial command functionality.

This script tests:
1. CLI command recognition
2. USB serial data routing to both CLI and Lua
3. Message log script functionality with CLI enabled

Usage:
    python3 test_cli_luaserial.py /dev/ttyACM0
"""

import serial
from serial.tools.list_ports import comports
import time
import sys

def find_transmitter() -> serial.Serial:
    for port in comports():
        if port.pid == 22336 and port.vid == 1155:
            return serial.Serial(port.device, 115200)
    raise RuntimeError("Transmitter not found")


def test_cli_luaserial():
    """Test the CLI luaserial functionality"""
    
    print("OpenTX CLI LuaSerial Test")
    print("=" * 40)
    
    try:
        # Connect to radio
        ser = find_transmitter()
        print(f"Connected to {ser.port}")

        # Give some time for connection
        time.sleep(1)
        
        # Test CLI help command first
        print("\n1. Testing CLI connectivity...")
        ser.write(b"help\r\n")
        time.sleep(0.5)
        
        response = b""
        while ser.in_waiting > 0:
            response += ser.read(ser.in_waiting)
            time.sleep(0.1)
        
        if b"luaserial" in response:
            print("✓ CLI luaserial command found in help")
        else:
            print("✗ luaserial command not found in CLI help")
            print(f"Help response: {response.decode('ascii', errors='ignore')}")
        
        # Test luaserial command
        print("\n2. Enabling luaserial mode...")
        ser.write(b"luaserial on\r\n")
        time.sleep(0.5)
        
        response = b""
        while ser.in_waiting > 0:
            response += ser.read(ser.in_waiting)
            time.sleep(0.1)
        
        print(f"luaserial on response: {response.decode('ascii', errors='ignore')}")
        
        # Test sending messages to Lua
        print("\n3. Testing Lua message forwarding...")
        
        for i in range(1, 30):
            print(f"   Sending message {i}: CLI Test Message {i}")
            ser.write(f"MSG:CLI Test Message {i}\n".encode())
            time.sleep(0.1)
        
        print("\n4. Testing disable luaserial...")
        ser.write(b"luaserial off\r\n")
        time.sleep(0.5)
        
        response = b""
        while ser.in_waiting > 0:
            response += ser.read(ser.in_waiting)
            time.sleep(0.1)
        
        print(f"luaserial off response: {response.decode('ascii', errors='ignore')}")
        
        print("\n5. Note: With luaserial off, messages go only to CLI")
        print("   (CLI will show 'Invalid command' for non-CLI messages)")
        # Don't send test messages when luaserial is off to avoid CLI errors
        
        print("\nTest complete!")
        print("\nTo use message logging with CLI:")
        print("1. Activate msglog telemetry screen on radio")
        print("2. Enable Lua forwarding: luaserial on")
        print("3. Send messages: echo 'MSG:Hello World!' > /dev/ttyACM0")
        print("4. Messages will appear on radio AND in CLI")
        print("5. To disable: luaserial off (messages only go to CLI)")
        print("\nIMPORTANT: Only send messages when luaserial is ON")
        print("           Otherwise CLI will try to parse them as commands")
        
    except serial.SerialException as e:
        print(f"Serial connection error: {e}")
        print("Make sure:")
        print("- Radio is connected via USB")
        print("- USB mode is set to 'USB Serial (VCP)' or 'USB Telemetry Mirror'")
        print("- Port permissions are correct (try: sudo chmod 666 /dev/ttyACM0)")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    test_cli_luaserial()