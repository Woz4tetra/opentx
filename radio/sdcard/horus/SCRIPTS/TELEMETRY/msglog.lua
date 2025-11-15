-- Message Log Telemetry Script
-- Displays scrolling messages received via USB serial
-- Protocol: Each line is a message ending with \n or \r\n
-- Commands:
--   CLEAR\n - Clear all messages
--   MSG:text\n - Add message "text" 
--   Just "text\n" - Add message "text" (implicit MSG command)

local maxLines = 15  -- Maximum lines to display on 480x272 LCD
local messages = {}
local lastUpdate = 0
local updateInterval = 20  -- Update every 200ms (20 * 10ms)
local serialBuffer = ""  -- Buffer for incomplete serial data

-- Colors for Horus
local BLACK = lcd.RGB(0, 0, 0)
local WHITE = lcd.RGB(255, 255, 255) 
local GRAY = lcd.RGB(128, 128, 128)
local BLUE = lcd.RGB(0, 100, 200)
local GREEN = lcd.RGB(0, 200, 0)

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
  lcd.clear(WHITE)
  
  -- Header background
  lcd.drawFilledRectangle(0, 0, LCD_W, 25, BLUE)
  
  -- Header text
  lcd.drawText(10, 5, "Message Log", DBLSIZE + WHITE)
  lcd.drawText(LCD_W - 80, 5, getTime(), WHITE)
  
  -- Messages
  local startY = 35
  for i = 1, #messages do
    local msg = messages[i]
    local y = startY + (i - 1) * 14
    if y < LCD_H - 14 then  -- Make sure we don't draw off screen
      -- Alternate row colors for better readability
      if i % 2 == 0 then
        lcd.drawFilledRectangle(5, y - 2, LCD_W - 10, 12, lcd.RGB(240, 240, 240))
      end
      
      -- Truncate message if too long
      local displayMsg = msg
      if #displayMsg > 60 then  -- Approximate character limit for 480 pixel width
        displayMsg = string.sub(displayMsg, 1, 57) .. "..."
      end
      lcd.drawText(10, y, displayMsg, BLACK)
    end
  end
  
  -- Instructions if no messages
  if #messages == 0 then
    lcd.drawText(50, 80, "Send messages via USB serial:", DBLSIZE + GRAY)
    lcd.drawText(50, 110, "MSG:Hello World", SMLSIZE + BLACK)
    lcd.drawText(50, 130, "or just:", SMLSIZE + BLACK)
    lcd.drawText(50, 150, "Hello World", SMLSIZE + BLACK)
    
    -- Example box
    lcd.drawRectangle(40, 70, LCD_W - 80, 100, GRAY, 2)
  end
  
  -- Footer
  lcd.drawText(10, LCD_H - 20, "Long EXIT to return to main view", SMLSIZE + GRAY)
  
  return 0
end

-- Return the interface
return { init=init, background=background, run=run }