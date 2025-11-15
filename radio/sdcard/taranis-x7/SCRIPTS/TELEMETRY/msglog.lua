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
  if event == EVT_KEY_LONG(KEY_EXIT) then
    return 2  -- Exit to main view
  end
  
  -- Read serial data periodically
  local currentTime = getTime()
  if currentTime - lastUpdate >= updateInterval then
    lastUpdate = currentTime
    
    -- Read all available serial data
    local data = serialRead()
    if data and data ~= "" then
      -- Split by lines and process each one
      local lines = {}
      for line in (data .. "\n"):gmatch("([^\r\n]*)\r?\n") do
        if line ~= "" then
          table.insert(lines, line)
        end
      end
      
      for _, line in ipairs(lines) do
        if line == "CLEAR" then
          -- Clear all messages
          messages = {}
        elseif line:sub(1, 4) == "MSG:" then
          -- Extract message after MSG: prefix
          local msg = line:sub(5)
          table.insert(messages, msg)
        else
          -- Treat as message without prefix
          table.insert(messages, line)
        end
        
        -- Keep only the latest messages that fit on screen
        while #messages > maxLines do
          table.remove(messages, 1)
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
  for i, msg in ipairs(messages) do
    local y = startY + (i - 1) * 8
    if y < LCD_H - 8 then  -- Make sure we don't draw off screen
      -- Truncate message if too long
      local displayMsg = msg
      if #displayMsg > 20 then  -- Approximate character limit for 128 pixel width
        displayMsg = displayMsg:sub(1, 17) .. "..."
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