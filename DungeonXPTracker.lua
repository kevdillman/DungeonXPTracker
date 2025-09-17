-- Tool to track xp earned during a LFD dungeon
-- v0.1 by Puggyberra and Squealz
-- created 10 Feb 2024

-- setup the dungeonFrame
local dungeonFrame = CreateFrame("Frame")
    dungeonFrame:RegisterEvent("ADDON_LOADED")
    dungeonFrame:RegisterEvent("PLAYER_ENTERING_WORLD")
    dungeonFrame:RegisterEvent("GROUP_LEFT")
    dungeonFrame:RegisterEvent("PLAYER_REGEN_DISABLED")

-- setup the window style
local backdropInfo = {
    bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background-Dark",
    edgeFile = "Interface\\AddOns\\Details\\images\\border_3",
    tile=true,
    tileEdge = true,
    tileSize = 8,
    edgeSize = 16,
    insets = {left = 3, right = 3, top = 4, bottom = 4}
}

local inDungeon = false
local areaCheck = false
local dungeonRun = {
    startTime = 0,
    endingTime = 0,
    startLVL = 0,
    startXP = 0,
    startRest = 0,
    startMoney = 0,
    endingLVL = 0,
    endingXP = 0,
    endingRest = 0,
    endingMoney = 0,
    dungeon = "a",
    charName = "a",
    charRace = "a",
    charRole = "a",
    charClass = "a"
}

-- upon load checks state to determine dungeon tracking
dungeonFrame:SetScript("OnEvent",
    function(self, event, ...)

        -- initial entry to dungeon
        if (event == "PLAYER_ENTERING_WORLD" and IsInInstance() and not inDungeon) then
            print("In an instance group! :-D")
            flushTable()
            printCurrentStats()
            inDungeon = true
            setStartXP()
        end

        -- left LFD dungeon from within dungeon
        if (event == "GROUP_LEFT" and IsInInstance() and inDungeon) then
            print("Left the group in an instance")
            inDungeon = false
            setEndXP()
            printXPValues()
        end

        -- left LFD dungeon outside dungeon
        if (event == "GROUP_LEFT" and not IsInInstance() and inDungeon) then
            print("Left the group outside instance")
            inDungeon = false
            setEndXP()
            printXPValues()
        end

        -- on first time in combat records values that may not be loaded earlier
        if (event == "PLAYER_REGEN_DISABLED" and not areaCheck and inDungeon) then
            if getZone() ~= dungeonRun.dungeon then
                dungeonRun.dungeon  = getZone()
                dungeonRun.charRole = UnitGroupRolesAssigned("player")
            end
            printZone()
            print("Role: ", dungeonRun.charRole)
            areaCheck = true
        end

        -- allows /xpt commands
        SLASH_DUNGEONXPTRACKER1 = "/xpt";

        function SlashCmdList.DUNGEONXPTRACKER(msg)
            -- output for default /xpt command and /xpt last
            -- prints the contents of dungeonRun
            if (msg == "" or msg == "last") then
                printXPValues()
            end

            -- command /xpt current
            -- prints the current character values
            if (msg == "current") then
                printCurrentStats()

                --print("class is: ", playerClass)
            end

            -- command /xpt guild
            -- prints the current character values to guild chat
            if (msg == "guild") then
                -- SendChatMessage("guild test",'GUILD')
                printCurrentStatsGuild()
            end

            -- command /xpt window
            -- display window with information about dungeon runs
            if (msg == "window") then
                print("xpt window creates a window")
                if dungeonInfoWindow == nil then
                    createDungeonWindow()
                end
                dungeonInfoWindow:Show()
            end

            -- command /xpt demo
            -- displays the dungeon info window and the raw data windows
            if (msg == "demo") then
                print("xpt window demo")
                if dungeonInfoWindow == nil then
                    createDungeonWindow()
                end
                dungeonInfoWindow:Show()
                if dungeonInfoWindowRaw == nil then
                    createRawDungeonWindow()
                end
                dungeonInfoWindowRaw:Show()
            end

            -- command /xpt close
            -- closes all open windows
            if (msg == "close") then
                -- close the info window
                if dungeonInfoWindow then
                    dungeonInfoWindow:Hide()
                end

                -- close the raw data window
                if dungeonInfoWindowRaw then
                    dungeonInfoWindowRaw:Hide()
                end
            end
        end

        -- on addon load checks saved variable
        if (event == "ADDON_LOADED") then
            local addon = ...
            if addon == "DungeonXPTracker" then

                printCurrentStats()

                -- if no saved variable exists create one
                if dungeonTracker == nil then
                    dungeonTracker = {
                        dungeons = {},
                        parsed = false
                    }
                end

                -- if saved variable file has been parsed clean it
                if dungeonTracker.parsed == true then
                    dungeonTracker = {
                        dungeons = {},
                        parsed = false
                     }
                end
                self:UnregisterEvent(event)
            end
        end
    end
)

-- create the dungeonInfoWindow
function createRawDungeonWindow()
    local dungeonInfoWindowRaw = CreateFrame("Frame", "dungeonInfoWindowRaw", UIParent, "BackdropTemplate")
    -- location and size
    dungeonInfoWindowRaw:SetPoint("CENTER", UIParent, "CENTER", 250, 0)
    dungeonInfoWindowRaw:SetSize(230, 270)

    -- background
    dungeonInfoWindowRaw:SetBackdrop(backdropInfo)
    dungeonInfoWindowRaw:SetAlpha(.8)

    -- make window movable
    dungeonInfoWindowRaw:SetMovable(true)
    dungeonInfoWindowRaw:EnableMouse(true)
    dungeonInfoWindowRaw:RegisterForDrag("LeftButton")
    dungeonInfoWindowRaw:SetScript("OnDragStart", dungeonInfoWindowRaw.StartMoving)
    dungeonInfoWindowRaw:SetScript("OnDragStop", dungeonInfoWindowRaw.StopMovingOrSizing)

    -- title:
    local dungeonInfoWindowTitle = dungeonInfoWindowRaw:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    dungeonInfoWindowTitle:SetPoint("TOP", 0, -4)
    dungeonInfoWindowTitle:SetText("Dungeon XP Raw Data")
    -- make the title easy to access:
    dungeonInfoWindowRaw.Title = dungeonInfoWindowTitle

    -- create close button
    local closeButton = CreateFrame("Button", "$parentCloseButton", dungeonInfoWindowRaw, "UIPanelButtonTemplate")
        closeButton:SetSize(21,21)
        closeButton:SetText("X")
        closeButton:SetPoint("TOPRIGHT", -2, -2)
        closeButton:SetAlpha(.8)
        closeButton:SetScript("OnClick",
            function(self)
                self:GetParent():Hide()
            end
        )
        dungeonInfoWindowRaw.closeButton = closeButton

    -- create button to view more information about specific dungeon
    local infoButton = CreateFrame("Button", "$parentCloseButton", dungeonInfoWindowRaw, "UIPanelButtonTemplate")
        infoButton:SetSize(120,25)
        infoButton:SetText("Clear Text")
        infoButton:SetPoint("BOTTOM", 0, 10)
        infoButton:SetAlpha(.9)
        infoButton:SetScript("OnClick",
            function(self)
                dungeonInfoWindowRaw.Text:Hide()
            end
        )
        dungeonInfoWindowRaw.infoButton = infoButton

    -- Frames don't normally have a SetText method, but we'll add one that sets the
    -- text of the frame's font string, and adjusts the size of the frame to match.
    function dungeonInfoWindowRaw:SetText(text)
        -- Set the text of the font string:
        self.Text:SetText(text)
        -- Find out how long the text is:
        local width = self.Text:GetStringWidth()
        -- Make sure it's at least as wide as the title and button:
        local titleWidth = self.Title:GetWidth()
        local buttonWidth = self.closeButton:GetWidth()
        width = math.max(width, titleWidth, buttonWidth)
        -- And adjust the width of the frame, accounting for the inner padding:
        self:SetWidth(width + 32)
    end

    -- Add a font string in the middle:
    dungeonInfoWindowRaw.Text = setWindowTextFormat(dungeonInfoWindowRaw)


    -- add information of the last dungeon run
    setWindowTextRaw(dungeonInfoWindowRaw)

end

-- create raw data window
function createDungeonWindow()
    local dungeonInfoWindow = CreateFrame("Frame", "dungeonInfoWindow", UIParent, "BackdropTemplate")
    -- location and size
    dungeonInfoWindow:SetPoint("CENTER", UIParent, "CENTER", 0, 0)
    dungeonInfoWindow:SetSize(230, 270)

    -- background
    dungeonInfoWindow:SetBackdrop(backdropInfo)
    dungeonInfoWindow:SetAlpha(.8)

    -- make window movable
    dungeonInfoWindow:SetMovable(true)
    dungeonInfoWindow:EnableMouse(true)
    dungeonInfoWindow:RegisterForDrag("LeftButton")
    dungeonInfoWindow:SetScript("OnDragStart", dungeonInfoWindow.StartMoving)
    dungeonInfoWindow:SetScript("OnDragStop", dungeonInfoWindow.StopMovingOrSizing)

    -- title:
    local dungeonInfoWindowTitle = dungeonInfoWindow:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    dungeonInfoWindowTitle:SetPoint("TOP", 0, -4)
    dungeonInfoWindowTitle:SetText("Dungeon XP Tracker")
    -- make the title easy to access:
    dungeonInfoWindow.Title = dungeonInfoWindowTitle

    -- create close button
    local closeButton = CreateFrame("Button", "$parentCloseButton", dungeonInfoWindow, "UIPanelButtonTemplate")
        closeButton:SetSize(21,21)
        closeButton:SetText("X")
        closeButton:SetPoint("TOPRIGHT", -2, -2)
        closeButton:SetAlpha(.8)
        closeButton:SetScript("OnClick",
            function(self)
                self:GetParent():Hide()
            end
        )
        dungeonInfoWindow.closeButton = closeButton

    -- create button to view more information about specific dungeon
    local infoButton = CreateFrame("Button", "$parentCloseButton", dungeonInfoWindow, "UIPanelButtonTemplate")
        infoButton:SetSize(120,25)
        infoButton:SetText("Clear Text")
        infoButton:SetPoint("BOTTOM", 0, 10)
        infoButton:SetAlpha(.9)
        infoButton:SetScript("OnClick",
            function(self)
                dungeonInfoWindow.Text:Hide()
            end
        )
        dungeonInfoWindow.infoButton = infoButton

    -- Add a font string in the middle:
    dungeonInfoWindow.Text = setWindowTextFormat(dungeonInfoWindow)

    -- Frames don't normally have a SetText method, but we'll add one that sets the
    -- text of the frame's font string, and adjusts the size of the frame to match.
    function dungeonInfoWindow:SetText(text)
        -- Set the text of the font string:
        self.Text:SetText(text)
        -- Find out how long the text is:
        local width = self.Text:GetStringWidth()
        -- Make sure it's at least as wide as the title and button:
        local titleWidth = self.Title:GetWidth()
        local buttonWidth = self.closeButton:GetWidth()
        width = math.max(width, titleWidth, buttonWidth)
        -- And adjust the width of the frame, accounting for the inner padding:
        self:SetWidth(width + 32)
    end

    -- add information of the last dungeon run
    setWindowText(dungeonInfoWindow)

end


-- sets the text format for a window
function setWindowTextFormat(window)
    local windowText = window:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    windowText:SetPoint("LEFT", 15, 0)
    windowText:SetPoint("RIGHT", -5, 0)
    windowText:SetPoint("TOP", window.Title, "BOTTOM", 0, -16)
    windowText:SetPoint("BOTTOM", 0, 16)
    windowText:SetJustifyH("Left")
    windowText:SetJustifyV("TOP")

    return windowText
end

-- sets the text string of a window
function setWindowText(window, text)
    displayText = ""
    displayText = displayText .. "Last Dungeon run:\n" .. dungeonOutput(dungeonTracker.dungeons[#dungeonTracker.dungeons - 1])
    window.Text:SetText(displayText)
end

-- sets the text string of a window
function setWindowTextRaw(window, text)
    displayText = ""
    displayText = displayText .. "Last Dungeon run:\n" .. dungeonOutputRaw(dungeonTracker.dungeons[#dungeonTracker.dungeons - 1])
    window.Text:SetText(displayText)
end

-- prints the current zone
function printZone()
    print ("You're currently in: ", getZone())
end

-- prints the current XP, time, and zone information
function printCurrentStats()
    local name, temp = UnitName("player")
    local race, temp1, temp2 = UnitRace("player")
    local playerClass, temp1, temp2 = UnitClass("player")
    print("Your playing: ", name)
    print("Your current race: ", race)
    print("Your class is: ", playerClass)
    print("The current time is: ", date("%d/%m/%y %H:%M:%S"))
    print("Current XP is:", UnitXP("player"))
    print("Current rest XP is:", GetXPExhaustion())
    print("Current max lvl XP is:", UnitXPMax("player"))
    print("Current gold: ", math.floor((GetMoney()/10000)))
    printZone()
end

-- prints current stats in guild chat
function printCurrentStatsGuild()
    local name, temp = UnitName("player")
    local race, temp1, temp2 = UnitRace("player")

    SendChatMessage("You're playing: " .. name,'GUILD')
    SendChatMessage("You're current race: " .. race,'GUILD')
    SendChatMessage("The current time is: " .. date("%d/%m/%y %H:%M:%S"), 'GUILD')
    SendChatMessage("Current XP is: " .. UnitXP("player"), 'GUILD')
    SendChatMessage("Current rest XP is: " .. getRestXP(), 'GUILD')
    SendChatMessage("Current max lvl XP is: " .. UnitXPMax("player"), 'GUILD')
    SendChatMessage("Current gold: " .. math.floor((GetMoney()/10000)), 'GUILD')
    SendChatMessage("Current zone: " .. getZone(), 'GUILD')
end

-- returns the current zone
function getZone()
    local Map_unit = false
    local zoneText = "a"
    local gotMapInfo = false

    if C_Map.GetBestMapForUnit ~= nil then
        Map_unit = C_Map.GetBestMapForUnit
        gotMapInfo = true
    else
        print("C_Map.GetBestMapForUnit == nil")
    end

    if gotMapInfo then
        gotMapInfo = false
        if Map_unit("player") ~= nil then
            zoneText, temp, temp1 = C_Map.GetMapInfo(Map_unit("player"))
            gotMapInfo = true
        else
            print("Map_unit(\"player\")) == nil")
        end
    end

    if gotMapInfo then
        return zoneText.name
    end

    return zoneText
end

-- prints the contents of a table
function dump(o)
    if type(o) == 'table' then
       local s = '{ '
       for k,v in pairs(o) do
          if type(k) ~= 'number' then k = '"'..k..'"' end
          s = s .. '['..k..'] = ' .. dump(v) .. ','
       end
       return s .. '} '
    else
       return tostring(o)
    end
 end

-- raw dungeon variable outputs
function dungeonOutputRaw(dungeonTable)
    local rawString = ""
    for key,value in pairs(dungeonTable) do
        key = key
        rawString = rawString .. key ..': ' .. tostring(value) .. '\n'
    end

    return rawString
end

-- return a pretty string of the information in the dungeon table
function dungeonOutput(dungeonTable)
    local prettyString = ""
    for key,value in pairs(dungeonTable) do
        key = key
        prettyString = prettyString .. key ..'   =   ' .. tostring(value) .. '\n'
    end
    prettyString =
        "Name: " .. dungeonTable.charName .. "\n" ..
        "Race: " .. dungeonTable.charRace .. "\n" ..
        -- need to add class gather "Class: " .. dungeonTable.charClass
        "Dungeon: " .. dungeonTable.dungeon .. "\n" ..
        "Role: " .. dungeonTable.charRole .. "\n" ..
        "Start level: " .. dungeonTable.startLVL .. "\n" ..
        "Start XP: " .. dungeonTable.startXP .. "\n" ..
        "End level: " .. dungeonTable.endingLVL .. "\n" ..
        "End XP: " .. dungeonTable.endingXP .. "\n" ..
        "Start rest: " .. dungeonTable.startRest .. "\n" ..
        "End rest: " .. dungeonTable.endingRest .. "\n" ..
        "Start gold: " .. dungeonTable.startMoney .. "\n" ..
        "End gold: " .. dungeonTable.endingMoney .. "\n" ..
        "Gold gained: " .. dungeonTable.endingMoney - dungeonTable.startMoney .. "\n" ..
        "Start time: " .. dungeonTable.startTime .. "\n" ..
        "End time: " .. dungeonTable.endingTime

    return prettyString
 end

-- gets amount of rest XP or returns 0 if none
function getRestXP()
    local endingRest = 0

    if GetXPExhaustion() ~= nil then
        endingRest = GetXPExhaustion()
    end

    return endingRest
end

-- sets the starting XP, rest, and lvl of a dungeon
function setStartXP()
    local name, temp = UnitName("player")
    local race, temp1, temp2 = UnitRace("player")
    local playerClass, temp1, temp2 = UnitClass("player")

    dungeonRun.charName     = name
    dungeonRun.charRace     = race
    dungeonRun.charClass    = playerClass
    dungeonRun.startTime    = date("%d/%m/%y %H:%M:%S")
    dungeonRun.startXP      = UnitXP("player")
    dungeonRun.startRest    = getRestXP()
    dungeonRun.startLVL     = UnitLevel("player")
    dungeonRun.startMoney   = math.floor((GetMoney()/10000))
    dungeonRun.dungeon      = ""
    dungeonRun.charRole     = "" --UnitGroupRolesAssigned("player")
    areaCheck               = false
end

-- sets the ending XP, rest, and lvl of a dungeon
function setEndXP()

    dungeonRun.endingRest    = getRestXP()
    dungeonRun.endingTime    = date("%d/%m/%y %H:%M:%S")
    dungeonRun.endingXP      = UnitXP("player")
    dungeonRun.endingLVL     = UnitLevel("player")
    dungeonRun.endingMoney   = math.floor((GetMoney()/10000))

    local dungeonInstance = {
        startTime   = dungeonRun.startTime,
        endingTime  = dungeonRun.endingTime,
        startLVL    = dungeonRun.startLVL,
        startXP     = dungeonRun.startXP,
        startRest   = dungeonRun.startRest,
        startMoney  = dungeonRun.startMoney,
        endingLVL   = dungeonRun.endingLVL,
        endingXP    = dungeonRun.endingXP,
        endingRest  = dungeonRun.endingRest,
        endingMoney = dungeonRun.endingMoney,
        dungeon     = dungeonRun.dungeon,
        charName    = dungeonRun.charName,
        charRace    = dungeonRun.charRace,
        charRole    = dungeonRun.charRole,
        charClass   = dungeonRun.charClass
    }

    table.insert(dungeonTracker.dungeons, dungeonInstance)
end

-- sets dungeonRun to default values
function flushTable()
    dungeonRun = {
        startTime = 0,
        endingTime = 0,
        startLVL = 0,
        startXP = 0,
        startRest = 0,
        startMoney = 0,
        endingLVL = 0,
        endingXP = 0,
        endingRest = 0,
        endingMoney = 0,
        dungeon = "a",
        charName = "a",
        charRace = "a",
        charRole = "a",
        charClass = "a",
    }
end

-- prints the beggining and ending XP values and dungeon
function printXPValues()
    print("Start time: ",    dungeonRun.startTime,  "  End time: ",  dungeonRun.endingTime)
    print("Start XP: ",      dungeonRun.startXP,    "  End XP: ",    dungeonRun.endingXP)
    print("Start Rest: ",    dungeonRun.startRest,  "  End Rest: ",  dungeonRun.endingRest)
    print("Start LvL: ",     dungeonRun.startLVL,   "  End LvL: ",   dungeonRun.endingLVL)
    print("Start gold: ",    dungeonRun.startMoney, "  End gold: ",  dungeonRun.endingMoney)
    print("Dungeon: ",       dungeonRun.dungeon)
    print("Role: ",          dungeonRun.charRole)
end
