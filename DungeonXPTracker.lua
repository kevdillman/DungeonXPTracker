-- Tool to track xp earned during a LFD dungeon
-- v0.1 by Puggyberra and Squealz
-- created 10 Feb 2024

-- setup the dungeonFrame
local dungeonFrame = CreateFrame("Frame")
    dungeonFrame:RegisterEvent("ADDON_LOADED")
    dungeonFrame:RegisterEvent("PLAYER_ENTERING_WORLD")
    dungeonFrame:RegisterEvent("GROUP_LEFT")
    dungeonFrame:RegisterEvent("PLAYER_REGEN_DISABLED")
    dungeonFrame:RegisterEvent("SCENARIO_UPDATE")

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
local inDelve = false
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
    instanceType = "a",
    charName = "a",
    charRace = "a",
    charRole = "a",
    charClass = "a",
    charRealm = "a",
    charGuild = "a",
    guildRealm = "a",
}

-- upon load checks state to determine dungeon tracking
dungeonFrame:SetScript("OnEvent",
    function(self, event, ...)

        -- check for entry to a delve
        if (event == "SCENARIO_UPDATE" and IsInInstance() and (C_Scenario.GetInfo() == "Delves") and not inDelve) then
            print("In a Delve!")
            instanceName = GetInstanceInfo()
            difficulty = C_UIWidgetManager.GetScenarioHeaderDelvesWidgetVisualizationInfo(6183).tierText
            print("In", instanceName, "at tier", difficulty)
            --printCurrentStats()
            --print("IsInInstance info: ", IsInInstance())
            --print("\nC_Scenario.GetInfo(): ", C_Scenario.GetInfo())
            --print("\nGetInstanceInfo(): ", GetInstanceInfo())
            --print("\ndelve tier: ", C_UIWidgetManager.GetScenarioHeaderDelvesWidgetVisualizationInfo(6183).tierText)

        end

        -- check for initial entry to dungeon
        if (event == "PLAYER_ENTERING_WORLD" and IsInInstance() and not inDungeon) then
            print("In a dungeon group! :-D")
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
                _, dungeonRun.instanceType = IsInInstance()
                dungeonRun.charRole = UnitGroupRolesAssigned("player")
            end
            --printZone()
            print("You're currently in: ", dungeonRun.dungeon)
            print("The instance type is: ", dungeonRun.instanceType)
            print("Role: ", dungeonRun.charRole)
            areaCheck = true
        end

        -- allows /xpt commands
        SLASH_DUNGEONXPTRACKER1 = "/xpt";

        function SlashCmdList.DUNGEONXPTRACKER(msg)
            -- output for default /xpt command and /xpt last
            -- prints the contents of dungeonRun

            -- default choice, prints available commands
            if (string.lower(msg) == "" or string.lower(msg) == "help") then
                print("Commands List:")
                print("close - Closes all open XPT windows")
                print("current - Prints the current character information")
                print("data - Prints a pretty string of the recorded data")
                print("demo - Displays the dungeon info window and the raw data windows")
                print("guild - Prints the current character information to guild chat")
                print("info - Prints values from the GetInstanceInfo()")
                print("last - Prints values from the last instance run")
                print("window - Display window with information about dungeon runs")
            end

            -- command /xpt close
            -- closes all open windows
            if (string.lower(msg) == "close") then
                -- close the info window
                if dungeonInfoWindow then
                    dungeonInfoWindow:Hide()
                end

                -- close the raw data window
                if dungeonInfoWindowRaw then
                    dungeonInfoWindowRaw:Hide()
                end

                -- close the test window
                if testWindow then
                    testWindow:Hide()
                end
            end

            -- command /xpt current
            -- prints the current character values
            if (string.lower(msg) == "current") then
                printCurrentStats()

                --print("class is: ", playerClass)
            end

            -- command /xpt data
            -- prints a pretty string of the recorded data
            if (string.lower(msg) == "data") then
               print(dungeonOutput(dungeonTracker.dungeons[#dungeonTracker.dungeons - 1]))
            end

            -- command /xpt demo
            -- displays the dungeon info window and the raw data windows
            if (string.lower(msg) == "demo") then
                print("xpt window demo")
                -- create pretty string windo
                if dungeonInfoWindow == nil then
                    local windowName = "dungeonInfoWindow"
                    createTextWindow(windowName)
                end
                local windowText = "Last Dungeon run:\n" .. dungeonOutput(dungeonTracker.dungeons[#dungeonTracker.dungeons - 1])
                width, height = dungeonInfoWindow:SetText(windowText)
                dungeonInfoWindow:Show()

                -- create raw data window
                if dungeonInfoWindowRaw == nil then
                    local windowName = "dungeonInfoWindowRaw"
                    createTextWindow(windowName, (width*1.1))
                end

                windowText = "Last Dungeon run:\n" .. dungeonOutputRaw(dungeonTracker.dungeons[#dungeonTracker.dungeons - 1])
                dungeonInfoWindowRaw:SetText(windowText)
                dungeonInfoWindowRaw:Show()
            end

            -- command /xpt guild
            -- prints the current character values to guild chat
            if (string.lower(msg) == "guild") then
                -- SendChatMessage("guild test",'GUILD')
                printCurrentStatsGuild()
            end

            -- command /xpt info
            -- prints the current dungeon info
            if (string.lower(msg) == "info") then
                -- msg = dungeonOutputRaw(GetInstanceInfo())
                local name, type, diffNum, diffTxt, maxPlayers, dynamicDifficulty, isDynamic, instanceMapID, lfgID = GetInstanceInfo()

                print("contents: ")
                print("name:", name)
                print("type:", type)
                print("diffNum:", diffNum)
                print("diffTxt:", diffTxt)
                print("maxPlayers:", maxPlayers)
                print("dynamicDifficulty:", dynamicDifficulty)
                print("isDynamic:", isDynamic)
                print("instanceMapID:", instanceMapID)
                print("lfgID:", lfgID)

            end

            -- command /xpt last
            -- shows values from last run
            if (string.lower(msg) == "last") then
                printXPValues()
            end

            -- command /xpt test
            -- tests stuff in text window
            if (string.lower(msg) == "test") then
                if testWindow == nil then
                    createTextWindow("testWindow")
                end

                text = dump(C_UIWidgetManager.GetScenarioHeaderDelvesWidgetVisualizationInfo(6183))
                --text = "[this is a silly test string,"
                testWindow:SetText(text)
                testWindow:Show()
            end

            -- command /xpt window
            -- display window with information about dungeon runs
            if (string.lower(msg) == "window") then
                print("xpt window creates a window")
                if dungeonInfoWindow == nil then
                    local windowName = "dungeonInfoWindow"
                    createTextWindow("dungeonInfoWindow")
                end
                local windowText = "Last Dungeon run:\n" .. dungeonOutput(dungeonTracker.dungeons[#dungeonTracker.dungeons - 1])
                dungeonInfoWindow:SetText(windowText)
                dungeonInfoWindow:Show()
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

-- create text window
function createTextWindow(windowName, horizontalOffset, verticalOffset)
    horizontalOffset = horizontalOffset or 0
    verticalOffset = verticalOffset or 0
    local textWindow = CreateFrame("Frame", windowName, UIParent, "BackdropTemplate")
    -- BackdropTemplate has a internal border line of 4 pixels
    -- UIPanelButtonTemplate has a internal border of 2 pixels
    textWindow:SetResizable(true)
    -- location and size
    textWindow:SetPoint("CENTER", UIParent, "CENTER", horizontalOffset, verticalOffset)
    textWindow:SetSize(230, 325)

    -- background
    textWindow:SetBackdrop(backdropInfo)
    textWindow:SetAlpha(.8)

    -- make window movable
    textWindow:SetMovable(true)
    textWindow:EnableMouse(true)
    textWindow:RegisterForDrag("LeftButton")
    textWindow:SetScript("OnDragStart", textWindow.StartMoving)
    textWindow:SetScript("OnDragStop", textWindow.StopMovingOrSizing)

    -- title:
    local textWindowTitle = textWindow:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    textWindowTitle:SetPoint("TOP", 0, -10)
    textWindowTitle:SetText("Test Window")
    -- make the title easy to access:
    textWindow.Title = textWindowTitle

    -- create close button
    local closeButton = CreateFrame("Button", "$parentCloseButton", textWindow, "UIPanelButtonTemplate")
        closeButton:SetSize(21,21)
        closeButton:SetText("X")
        closeButton:SetPoint("TOPRIGHT", -4, -4)
        closeButton:SetAlpha(.8)
        closeButton:SetScript("OnClick",
            function(self)
                self:GetParent():Hide()
            end
        )
        textWindow.closeButton = closeButton

    -- create button to view more information about specific dungeon
    local infoButton = CreateFrame("Button", "$parentCloseButton", textWindow, "UIPanelButtonTemplate")
        infoButton:SetSize(120,25)
        infoButton:SetText("Clear Text")
        infoButton:SetPoint("BOTTOM", 0, 6)
        infoButton:SetAlpha(.9)
        infoButton:SetScript("OnClick",
            function(self)
                textWindow.Text:Hide()
            end
        )
        textWindow.infoButton = infoButton

    -- Add a font string in the middle:
    textWindow.Text = setWindowTextFormat(textWindow)

    -- Frames don't normally have a SetText method, but we'll add one that sets the
    -- text of the frame's font string, and adjusts the size of the frame to match.
    function textWindow:SetText(text)
        -- Set the text of the font string:
        self.Text:SetText(text)

        -- Find the width and height of the text including padding
        local textWidth = self.Text:GetStringWidth()  + 19
        local textHeight = self.Text:GetStringHeight() + 8

        -- Find the width and height of the title and close boxes including padding
        local titleWidth = self.Title:GetWidth() + self.closeButton:GetWidth()
        local titleHeight = math.max(self.Title:GetHeight() + 6,  self.closeButton:GetHeight() + 4)

        -- Find the width and height of the info button including padding
        local infoButtonWidth = self.infoButton:GetWidth()
        local infoButtonHeight = self.infoButton:GetHeight() + 8

        -- Find the widest window element
        local width = math.max(textWidth,  titleWidth, infoButtonWidth)

        -- Add the heights of all window elements
        local height = textHeight + titleHeight + infoButtonHeight

        -- Adjust the width and height of the frame
        self:SetWidth(width)
        self:SetHeight(height)
        return width, height
    end

    -- add information of the last dungeon run
    --setWindowText(textWindow)

end

-- sets the text format for a window
function setWindowTextFormat(window)
    local windowText = window:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    --windowText:SetPoint("LEFT", 15, 0)
    --windowText:SetPoint("RIGHT", -5, 0)
    windowText:SetPoint("LEFT", 11, 0)
    --windowText:SetPoint("RIGHT", -4, 0)
    windowText:SetPoint("TOP", window.closeButton, "BOTTOM", 0, -2)
    --windowText:SetPoint("BOTTOM", window.closeButton, "TOP", 0, 4)
    windowText:SetJustifyH("Left")
    windowText:SetJustifyV("TOP")

    return windowText
end

-- sets the text string of a window
function setDynamicWindowText(window, text)
    displayText = ""
    displayText = text
    window:SetText(displayText)
end

-- sets the text string of a window
function setWindowText(window, text)
    displayText = ""
    displayText = displayText .. "Last Dungeon run:\n" .. dungeonOutput(dungeonTracker.dungeons[#dungeonTracker.dungeons - 1])
    window:SetText(displayText)
end

-- sets the text string of a window
function setWindowTextRaw(window, text)
    displayText = ""
    displayText = displayText .. "Last Dungeon run:\n" .. dungeonOutputRaw(dungeonTracker.dungeons[#dungeonTracker.dungeons - 1])
    window:SetText(displayText)
end

-- prints the current zone
function printZone()
    print ("You're currently in: ", getZone())
end

-- prints the current XP, time, and zone information
function printCurrentStats()
    local name, _ = UnitName("player")
    local race, _, _ = UnitRace("player")
    local playerClass, _, _ = UnitClass("player")
    local realm = GetRealmName()
    local guildName, _, _, guildRealm = GetGuildInfo("player")

    print("Your playing: ", name)
    print("Your current race: ", race)
    print("Your class is: ", playerClass)
    print("Your realm is: ", realm)
    print("Your guild is: ", guildName)
    print("Your guild's realm is: ", guildRealm)
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
          s = s .. '['..k..'] = ' .. dump(v) .. ',\n'
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
        "Class: " .. dungeonTable.charClass .. "\n" ..
        "Realm: " .. dungeonTable.charRealm .. "\n" ..
        "Guild: " .. dungeonTable.charGuild .. "\n" ..
        "Guild's Realm: " .. dungeonTable.guildRealm .. "\n" ..
        "Dungeon: " .. dungeonTable.dungeon .. "\n" ..
        "Instance Type: " .. dungeonTable.instanceType .. "\n" ..
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
    local name, temp1 = UnitName("player")
    local race, temp1, temp2 = UnitRace("player")
    local playerClass, temp1, temp2 = UnitClass("player")
    local realm = GetRealmName()
    local guildName, _, _, guildRealm = GetGuildInfo("player")

    dungeonRun.charName     = name
    dungeonRun.charRace     = race
    dungeonRun.charClass    = playerClass
    dungeonRun.charRealm    = realm
    dungeonRun.charGuild    = guildName
    dungeonRun.guildRealm   = guildRealm
    dungeonRun.startTime    = date("%d/%m/%y %H:%M:%S")
    dungeonRun.startXP      = UnitXP("player")
    dungeonRun.startRest    = getRestXP()
    dungeonRun.startLVL     = UnitLevel("player")
    dungeonRun.startMoney   = math.floor((GetMoney()/10000))
    dungeonRun.dungeon      = ""
    dungeonRun.instanceType = ""
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
        instanceType= dungeonRun.instanceType,
        charName    = dungeonRun.charName,
        charRace    = dungeonRun.charRace,
        charRole    = dungeonRun.charRole,
        charClass   = dungeonRun.charClass,
        charRealm   = dungeonRun.charRealm,
        charGuild   = dungeonRun.charGuild,
        guildRealm  = dungeonRun.guildRealm,
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
        instanceType = "a",
        charName = "a",
        charRace = "a",
        charRole = "a",
        charClass = "a",
        charRealm = "a",
        charGuild = "a",
        guildRealm = "a",
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
