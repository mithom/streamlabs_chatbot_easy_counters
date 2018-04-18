# streamlabs_chatbot_easy_counters

### this scripts adds easy managable counters with lots of options.
the available commands are:
* !addcounter !a_new_counter
* !removeCounter !an_old_counter
* !addCounterPermission !an_existing_counter Permission (extra_info)
* !removeCounterPermission !an_existing_counter
* !counterPermission !an_existing_counter
* !counterPermissions
* !toggleCounterPermissions

By default each command is linked to a global toggle between moderator and a configurable option. Counters can get their own fixed permission by using the !addCounterPermission command. The toggle will not affect the specified counter anymore. To get it back on the global toggle, just remove the permission again using !removePermission. The Global permission can be checked using !counterPermissions.

All config commands are Moderator only without cooldown (this is why you can disable the toggle in settings), All show functions are for everyone with the configured cooldown.

example counter:

    !addCounter !burp
    !burp 10 
    !burp + 
    !burp - 
    !burp 
    !addCounterPermission !burp Min_hours 10

## On top of these commands, it has some configurable settings
* Use Cooldowns?
* Individual/global cooldown
* length of cooldown
* a shorter cooldown to prevent multiple people counting the same event
* global permission in non-moderator toggle stance
* disable the global permission toggle
* custom command names

### Files to read for showing on stream
They will be kept in sync in real-time
* Counters.json
* permissions.json

### To be expected:
* custom text messages
* other platforms then twitch
* your feature request here? mail me @ mi_thom@hotmail.com

## see it in action?
streamers that are using this script:
* [Billie_bob](http://www.twitch.tv/billie_bob)

### changelog:
v 1.0.1: added custom command names & file sync

v 1.0.0: made public
