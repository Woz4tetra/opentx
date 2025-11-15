-- Message Log Telemetry Script
-- Displays scrolling messages received via USB serial
-- Protocol: Each line is a message ending with \n or \r\n
-- Commands:
--   CLEAR\n - Clear all messages
--   MSG:text\n - Add message "text" 
--   Just "text\n" - Add message "text" (implicit MSG command)

local maxLines = 7  -- Maximum lines to display on 128x64 LCD
local messages = {}
local lastUpdate = 0
local updateInterval = 20  -- Update every 200ms (20 * 10ms)
local serialBuffer = ""  -- Buffer for incomplete serial data

-- Initialize
local function init()
  return { }
end

-- Background function (not used for telemetry scripts)
local function background()
  -- Not used for telemetry scripts
end

-- Main run function
local function run(event)
  -- Handle exit
  if event == EVT_EXIT_BREAK then
    return 2  -- Exit to main view
  end
  
  -- Read serial data periodically
  local currentTime = getTime()
  if currentTime - lastUpdate >= updateInterval then
    lastUpdate = currentTime
    
    -- Read all available serial data (read multiple times to get all data)
    local hasNewData = false
    for readAttempt = 1, 5 do  -- Try multiple reads to get all buffered data
      local data = serialRead()
      if data and type(data) == "string" and data ~= "" then
        serialBuffer = serialBuffer .. data
        hasNewData = true
      else
        break  -- No more data available
      end
    end
    
    if hasNewData then
      -- Process complete lines
      while true do
        local newlinePos = string.find(serialBuffer, "\n")
        if not newlinePos then
          break
        end
        
        local line = string.sub(serialBuffer, 1, newlinePos - 1)
        serialBuffer = string.sub(serialBuffer, newlinePos + 1)
        
        -- Remove carriage return if present
        if string.sub(line, -1) == "\r" then
          line = string.sub(line, 1, -2)
        end
        
        -- Process the complete line
        if line ~= "" then
          if line == "CLEAR" then
            -- Clear all messages
            messages = {}
          elseif string.sub(line, 1, 4) == "MSG:" then
            -- Extract message after MSG: prefix
            local msg = string.sub(line, 5)
            messages[#messages + 1] = msg
          else
            -- Treat as message without prefix
            messages[#messages + 1] = line
          end
          
          -- Keep only the latest messages that fit on screen
          while #messages > maxLines do
            -- Remove first element by shifting all elements down
            for i = 1, #messages - 1 do
              messages[i] = messages[i + 1]
            end
            messages[#messages] = nil
          end
        end
      end
    end
  end
  
  -- Draw the UI
  lcd.clear()
  
  -- Header
  lcd.drawText(1, 1, "Message Log", INVERS)
  lcd.drawText(LCD_W - 30, 1, getTime(), 0)
  
  -- Messages
  local startY = 10
  for i = 1, #messages do
    local msg = messages[i]
    local y = startY + (i - 1) * 8
    if y < LCD_H - 8 then  -- Make sure we don't draw off screen
      -- Truncate message if too long
      local displayMsg = msg
      if #displayMsg > 30 then  -- Approximate character limit for 128 pixel width
        displayMsg = string.sub(displayMsg, 1, 27) .. "..."
      end
      lcd.drawText(1, y, displayMsg, 0)
    end
  end
  
  -- Instructions at bottom if no messages
  if #messages == 0 then
    lcd.drawText(1, 20, "Send messages via", SMLSIZE)
    lcd.drawText(1, 28, "USB serial:", SMLSIZE)
    lcd.drawText(1, 36, "MSG:Hello World", SMLSIZE)
    lcd.drawText(1, 44, "or just:", SMLSIZE) 
    lcd.drawText(1, 52, "Hello World", SMLSIZE)
  end
  
  return 0
end

-- Return the interface
return { init=init, background=background, run=run }