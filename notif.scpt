on replace_chars(this_text, search_string, replacement_string)
	set AppleScript's text item delimiters to the search_string
	set the item_list to every text item of this_text
	set AppleScript's text item delimiters to the replacement_string
	set this_text to the item_list as string
	set AppleScript's text item delimiters to ""
	return this_text
end replace_chars

tell application "System Events"
	keystroke "n" using {control down, option down, command down}
	delay 1
	set stacked_notifications to {}

    set notifList to {}

	set _groups to groups of UI element 1 of scroll area 1 of group 1 of window "Notification Center" of application process "NotificationCenter"
	repeat with _group in _groups
		try
			if subrole of _group is equal to "AXNotificationCenterBannerStack" then
				set end of stacked_notifications to _group
			end if
		end try
	end repeat
	
	repeat with stacked_notification in stacked_notifications
		click stacked_notification
	end repeat
	
	delay 1
	try
		set _groups to groups of UI element 1 of scroll area 1 of group 1 of window "Notification Center" of application process "NotificationCenter"
		repeat with _group in _groups
            set textOne to value of static text 1 of _group
			set _textTwo to value of static text 2 of _group
			set textTwo to my replace_chars(_textTwo, ",", "")
			set textThree to value of static text 3 of _group
			set end of notifList to (textTwo & "|" & textOne & "|" & textThree) as string
		end repeat
	end try

    keystroke "n" using {control down, option down, command down}
end tell

return notifList