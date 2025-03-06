on run argv
    -- Convert the argument list to text
    set recipientListText to item 1 of argv
    set emailSubject to item 2 of argv
    set emailBody to item 3 of argv

    -- Convert the recipient list text to a list
    set AppleScript's text item delimiters to ","
    set recipientList to text items of recipientListText

    tell application "Mail"
        set newMessage to make new outgoing message with properties {subject:emailSubject, visible:true}

        tell newMessage
            -- Add each email address as a BCC recipient
            repeat with recipientAddress in recipientList
                make new bcc recipient at end of bcc recipients with properties {address:recipientAddress}
            end repeat
            set content to emailBody
        end tell
        
        activate
    end tell
end run
