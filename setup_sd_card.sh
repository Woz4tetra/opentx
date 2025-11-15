#!/bin/bash

# OpenTX Message Log SD Card Setup Script
# This script copies the msglog.lua script to your SD card

echo "OpenTX Message Log SD Card Setup"
echo "================================="

# Function to detect radio type
detect_radio_type() {
    echo "Please select your radio type:"
    echo "1) Taranis X9 (X9D, X9D+, X9E)"
    echo "2) Taranis X7 (X7, X7S)" 
    echo "3) Jumper T16/T18 (Horus)"
    echo "4) Tango 2"
    echo "5) Manual path entry"
    
    read -p "Enter choice [1-5]: " choice
    
    case $choice in
        1) echo "taranis-x9" ;;
        2) echo "taranis-x7" ;;
        3) echo "horus" ;;
        4) echo "tango" ;;
        5) echo "manual" ;;
        *) echo "invalid" ;;
    esac
}

# Function to find SD card
find_sd_card() {
    echo
    echo "Looking for SD card..."
    
    # Common SD card mount points
    possible_paths=(
        "/media/$USER"
        "/media"
        "/mnt"
        "/Volumes"  # macOS
    )
    
    for base_path in "${possible_paths[@]}"; do
        if [ -d "$base_path" ]; then
            echo "Checking $base_path..."
            for mount_point in "$base_path"/*; do
                if [ -d "$mount_point" ]; then
                    # Check if it looks like an SD card (has some typical characteristics)
                    if [ -w "$mount_point" ] && [ "$(stat -f -c %T "$mount_point" 2>/dev/null)" = "msdos" ] 2>/dev/null; then
                        echo "Found potential SD card at: $mount_point"
                    fi
                fi
            done
        fi
    done
    
    echo
    echo "Please enter the full path to your SD card:"
    echo "Example: /media/username/SD_CARD_NAME"
    echo "         /Volumes/SD_CARD_NAME (macOS)"
    echo "         D: (Windows - use Git Bash or WSL)"
    
    read -p "SD card path: " sd_path
    echo "$sd_path"
}

# Function to copy files
copy_files() {
    local radio_type="$1"
    local sd_path="$2"
    
    if [ "$radio_type" = "manual" ]; then
        echo
        echo "Manual setup instructions:"
        echo "1. Create folder: SCRIPTS/TELEMETRY/ on your SD card"
        echo "2. Copy the appropriate msglog.lua file from:"
        echo "   /home/ben/opentx/radio/sdcard/[your-radio]/SCRIPTS/TELEMETRY/msglog.lua"
        echo "3. Put the file in: [SD-CARD]/SCRIPTS/TELEMETRY/msglog.lua"
        return
    fi
    
    local source_file="/home/ben/opentx/radio/sdcard/$radio_type/SCRIPTS/TELEMETRY/msglog.lua"
    local dest_dir="$sd_path/SCRIPTS/TELEMETRY"
    local dest_file="$dest_dir/msglog.lua"
    
    echo
    echo "Setting up SD card for $radio_type..."
    echo "Source: $source_file"
    echo "Destination: $dest_file"
    
    # Check if source file exists
    if [ ! -f "$source_file" ]; then
        echo "❌ Error: Source file not found: $source_file"
        return 1
    fi
    
    # Check if SD card path exists and is writable
    if [ ! -d "$sd_path" ] || [ ! -w "$sd_path" ]; then
        echo "❌ Error: SD card path not accessible: $sd_path"
        echo "Make sure the SD card is mounted and writable"
        return 1
    fi
    
    # Create directory structure
    echo "Creating directory structure..."
    mkdir -p "$dest_dir"
    
    if [ $? -ne 0 ]; then
        echo "❌ Error: Could not create directory: $dest_dir"
        return 1
    fi
    
    # Copy the file
    echo "Copying msglog.lua..."
    cp "$source_file" "$dest_file"
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully copied msglog.lua to SD card!"
        echo
        echo "Next steps:"
        echo "1. Safely eject the SD card from your computer"
        echo "2. Insert SD card into your radio"
        echo "3. Go to DISPLAY menu and select 'msglog' telemetry screen"
        echo "4. Or bind to a switch via Special Functions"
        echo
        echo "Testing:"
        if [ -f "/home/ben/opentx/message_client.py" ]; then
            echo "5. Connect radio via USB"
            echo "6. Run: python3 /home/ben/opentx/message_client.py"
            echo "   Or: echo 'MSG:Test message' > /dev/ttyACM0"
        fi
        
        # If it's a CLI build, add CLI instructions
        echo
        echo "For CLI-enabled builds:"
        echo "7. Connect via USB terminal and run: luaserial on"
        
    else
        echo "❌ Error: Failed to copy file"
        return 1
    fi
}

# Main execution
main() {
    # Detect radio type
    radio_type=$(detect_radio_type)
    
    if [ "$radio_type" = "invalid" ]; then
        echo "❌ Invalid selection. Exiting."
        exit 1
    fi
    
    if [ "$radio_type" != "manual" ]; then
        # Find SD card
        sd_path=$(find_sd_card)
        
        # Copy files
        copy_files "$radio_type" "$sd_path"
    else
        copy_files "manual" ""
    fi
}

# Run main function
main