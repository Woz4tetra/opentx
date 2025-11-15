# Quick SD Card Setup for OpenTX Message Log

## Option 1: Automated Setup (Recommended)

```bash
cd /home/ben/opentx
./setup_sd_card.sh
```

The script will:
1. Ask for your radio type
2. Find your SD card 
3. Copy the correct msglog.lua file
4. Create the proper directory structure

## Option 2: Manual Setup

### Step 1: Identify Your Radio Type
- **Taranis X9** (X9D, X9D+, X9E) → use `taranis-x9` folder
- **Taranis X7** (X7, X7S) → use `taranis-x7` folder  
- **Horus** (Jumper T16/T18) → use `horus` folder
- **Tango 2** → use `tango` folder

### Step 2: Copy Files to SD Card

1. **Mount your SD card** on your computer
2. **Create directories** on SD card: `SCRIPTS/TELEMETRY/`
3. **Copy the script**:
   ```bash
   # Example for Taranis X9:
   cp /home/ben/opentx/radio/sdcard/taranis-x9/SCRIPTS/TELEMETRY/msglog.lua /path/to/sd/SCRIPTS/TELEMETRY/msglog.lua
   ```

### Step 3: Verify Structure
Your SD card should have:
```
SD_CARD/
├── SCRIPTS/
│   └── TELEMETRY/
│       └── msglog.lua
└── (other files...)
```

## Step 4: Radio Setup

1. **Insert SD card** into radio
2. **Power on** radio
3. **Access telemetry**: Press `DISP` button or go to DISPLAY menu
4. **Select msglog**: Choose "msglog" from telemetry screens

## Step 5: Test

### For Standard Builds:
```bash
# Connect radio via USB, then:
echo "MSG:Test message" > /dev/ttyACM0
```

### For CLI Builds:
```bash
# 1. Connect via USB terminal:
screen /dev/ttyACM0 115200
# or: minicom -D /dev/ttyACM0 -b 115200

# 2. Enable Lua serial:
luaserial on

# 3. In another terminal, send message:
echo "MSG:CLI test message" > /dev/ttyACM0
```

## Troubleshooting

### "No scripts on SD card"
- Check directory structure: `SCRIPTS/TELEMETRY/msglog.lua`
- Verify file permissions (should be readable)
- Try reformating SD card (FAT32)
- Check SD card is properly seated in radio

### Script appears but doesn't work
- Check USB connection mode (USB Serial or USB Telemetry Mirror)
- For CLI builds: Make sure `luaserial on` is executed
- Verify messages end with newline (`\n`)

### Can't find SD card mount point
```bash
# List all mounted filesystems:
df -h

# List USB/SD devices:
lsblk

# Manual mount example:
sudo mkdir /mnt/sdcard
sudo mount /dev/sdb1 /mnt/sdcard
```