#!/usr/bin/env python3
"""
Debug script to show expected packet format for OpenTX channel streaming
"""

def create_test_packet():
    """Create test packets showing the expected format"""
    sync_sequence = bytes([0xA3, 0xA4, 0xA5])
    max_channels = 32
    channels_per_packet = 16
    
    # Create test channel data (sawtooth pattern)
    all_channels = []
    for i in range(max_channels):
        # Create a sawtooth pattern for easy identification
        value = int(((i / (max_channels - 1)) * 2048) - 1024)  # -1024 to +1024
        all_channels.append(value)
    
    packets = []
    
    # Create two phase packets
    for phase in range(2):
        start_ch = phase * channels_per_packet
        end_ch = start_ch + channels_per_packet
        phase_channels = all_channels[start_ch:end_ch]
        
        # Build packet: sync + phase + length + data + checksum
        packet = bytearray()
        packet.extend(sync_sequence)
        packet.append(phase)
        
        # Length = channels * 2 + checksum
        data_length = (channels_per_packet * 2) + 1
        packet.append(data_length)
        
        # Calculate checksum starting with phase and length
        checksum = phase ^ data_length
        
        # Channel data as 16-bit little-endian
        for value in phase_channels:
            # Convert to 16-bit signed, little-endian
            if value < 0:
                value = value & 0xFFFF  # Two's complement
            low_byte = value & 0xFF
            high_byte = (value >> 8) & 0xFF
            
            packet.append(low_byte)
            packet.append(high_byte)
            
            checksum ^= low_byte
            checksum ^= high_byte
        
        packet.append(checksum)
        packets.append(packet)
    
    return packets, all_channels

def main():
    packets, channels = create_test_packet()
    
    print("OpenTX Channel Data Packet Format Debug (Phase-Based)")
    print("="*60)
    
    print("Channel values used in test packets:")
    for i in range(0, len(channels), 8):
        line = ""
        for j in range(8):
            if i + j < len(channels):
                ch_num = i + j
                value = channels[ch_num]
                percentage = (value / 1024.0) * 100
                line += f"CH{ch_num+1:2d}:{value:5d}({percentage:+4.0f}%) "
        print(line)
    
    for phase, packet in enumerate(packets):
        print(f"\n--- Phase {phase} Packet ---")
        print(f"Sync sequence: 0x{packet[0]:02X} 0x{packet[1]:02X} 0x{packet[2]:02X}")
        print(f"Phase: {packet[3]}")
        print(f"Length: {packet[4]} (0x{packet[4]:02X})")
        print(f"Total packet size: {len(packet)} bytes")
        print(f"Checksum: 0x{packet[-1]:02X}")
        
        print(f"\nComplete packet (hex):")
        hex_str = ""
        for i, byte in enumerate(packet):
            if i % 16 == 0:
                if hex_str:
                    print(hex_str)
                hex_str = f"{i:04X}: "
            hex_str += f"{byte:02X} "
        if hex_str:
            print(hex_str)
        
        print(f"\nPacket breakdown:")
        print(f"  Sync:     bytes[0:3]   = 0xA3 0xA4 0xA5")
        print(f"  Phase:    byte[3]      = {packet[3]}")
        print(f"  Length:   byte[4]      = {packet[4]} (0x{packet[4]:02X})")
        print(f"  Data:     bytes[5:-1]  = {len(packet[5:-1])} bytes (16 channels × 2 bytes)")
        print(f"  Checksum: byte[-1]     = 0x{packet[-1]:02X}")
        
        # Verify checksum calculation
        calc_checksum = packet[3] ^ packet[4]  # phase XOR length
        for i in range(5, len(packet) - 1):  # All data bytes
            calc_checksum ^= packet[i]
        
        print("\nChecksum verification:")
        print(f"  Calculated: 0x{calc_checksum:02X}")
        print(f"  In packet:  0x{packet[-1]:02X}")
        print(f"  Valid: {calc_checksum == packet[-1]}")

if __name__ == "__main__":
    main()