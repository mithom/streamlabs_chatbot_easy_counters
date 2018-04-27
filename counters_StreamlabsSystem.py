# ---------------------------------------
#   Import Libraries
# ---------------------------------------
import os
import codecs
import json

# ---------------------------------------
#   [Required]  Script Information
# ---------------------------------------
ScriptName = "MoreCounters"
Website = "https://www.Streamlabs.Chatbot.com"
Description = "add counters at will with commands"
Creator = "mi_thom"
Version = "1.2.0"

# ---------------------------------------
#   Set Global Variables
# ---------------------------------------
ScriptSettings = None
m_ModeratorPermission = "Moderator"
m_allowed_permissions = ["Everyone", "Regular", "Subscriber", "GameWisp_Subscriber", "User_Specific", "Min_Rank",
                         "Min_Points", "Min_Hours", "Moderator", "Editor", "Caster"]
m_CounterHash = {}
m_PermissionsHash = {}
m_CountersFile = os.path.join(os.path.dirname(__file__), "Counters.json")
m_PermissionsFile = os.path.join(os.path.dirname(__file__), "permissions.json")
m_SettingsFile = os.path.join(os.path.dirname(__file__), "counterSettings.json")
m_MessagesHash = {}
m_MessagesFile = os.path.join(os.path.dirname(__file__), "messages.json")


def default_permission():
    return m_PermissionsHash.get("Global", [m_ModeratorPermission, ""])


# ---------------------------------------
# Classes
# ---------------------------------------
class Settings(object):
    """ Load in saved settings file if available else set default values. """

    def __init__(self, settingsfile=None):
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8")
            if "GetUserChangePermissionGlobal" in self.__dict__:
                self.__dict__["getUserChangePermissionGlobal"] = self.__dict__["GetUserChangePermissionGlobal"]
                del self.__dict__["GetUserChangePermissionGlobal"]
        except:
            self.use_cd = True
            self.show_cd = 15
            self.individual_cd = False
            self.set_cd = 5
            self.allow_user_change_toggle = True
            self.toggle_to = "Regular"
            self.toggle_to_info = ""

            # messages
            self.default_counter_message = "current {0} count is {1}"
            self.global_permission_toggle_message = "the global permission to change counters has been set to {1}, {2}"
            self.on_global_permission_message = "the counter {0} is on the global permission"
            self.specific_permission_message = "{0} counter's permission is {1}, {2}"
            self.counter_not_exist = "{0} counter does not exist"

            # command names
            self.addCommand = "!addCounter"
            self.removeCommand = "!removeCounter"
            self.addPermission = "!addCounterPermission"
            self.removePermission = "!removeCounterPermission"
            self.getPermission = "!counterPermission"
            self.getUserChangePermissionGlobal = "!counterPermissions"
            self.toggleUserChangeGlobal = "!toggleCounterPermissions"
            self.editCommand = "!editCounter"

    def reload(self, jsondata):
        """ Reload settings from Chatbot user interface by given json data. """
        self.__dict__ = json.loads(jsondata, encoding="utf-8")
        return

    def save(self, settingsfile):
        """ Save settings contained within to .json and .js settings files. """
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8")
            with codecs.open(settingsfile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8')))
        except:
            Parent.Log(ScriptName, "Failed to save settings to file.")
        return


# ---------------------------------------
#   Init & Cleanup functions
# ---------------------------------------
def load_counters():
    global m_CounterHash

    try:
        with codecs.open(m_CountersFile, mode="r") as f:
            m_CounterHash = json.load(f)
    except:
        Parent.Log(ScriptName, "failed to load counters, counters have been reset")


def save_counters():
    try:
        with codecs.open(m_CountersFile, mode="w+") as f:
            json.dump(m_CounterHash, f)
    except:
        Parent.Log(ScriptName, "Failed to save the counters")
    return


def load_permissions():
    global m_PermissionsHash
    try:
        with codecs.open(m_PermissionsFile, mode="r") as f:
            m_PermissionsHash = json.load(f)
    except:
        Parent.Log(ScriptName, "failed to load permissions, permissions have been reset to mods only")


def save_permissions():
    try:
        with codecs.open(m_PermissionsFile, mode="w+") as f:
            json.dump(m_PermissionsHash, f)
    except:
        Parent.Log(ScriptName, "Failed to save the permissions")
    return


def fix_global_permission_on_load():
    global m_PermissionsHash
    if m_PermissionsHash.get("Global", default_permission())[0] != m_ModeratorPermission:
        m_PermissionsHash.update(Global=[ScriptSettings.toggle_to, ScriptSettings.toggle_to_info])
        message = "/me [set] " + ScriptSettings.global_permission_toggle_message.format("", *m_PermissionsHash["Global"])
        Parent.SendTwitchMessage(message)


def load_messages():
    global m_MessagesHash

    try:
        with codecs.open(m_MessagesFile, mode="r") as f:
            m_MessagesHash = json.load(f)
    except:
        Parent.Log(ScriptName, "failed to load messages, messages have been reset")


def save_messages():
    try:
        with codecs.open(m_MessagesFile, mode="w+") as f:
            json.dump(m_MessagesHash, f)
    except:
        Parent.Log(ScriptName, "Failed to save the messages")
    return
# ---------------------------------------
#   [Required] Intialize Data (Only called on Load)
# ---------------------------------------
def Init():
    global ScriptSettings

    ScriptSettings = Settings(m_SettingsFile)
    load_counters()
    load_permissions()
    fix_global_permission_on_load()
    load_messages()


# ---------------------------------------
#   [Optional] Reload settings (Only called on save button press)
# ---------------------------------------
def ReloadSettings(jsondata):
    # load in json after pressing save settings button
    global ScriptSettings
    ScriptSettings.reload(jsondata)
    fix_global_permission_on_load()
    Parent.Log('saving settings successful')
    return


# ---------------------------------------
#   [Optional] Save data (Only called on exit chatbot)
# ---------------------------------------
def Unload():
    # Triggers when the bot closes / script is reloaded
    save_counters()
    save_permissions()
    save_messages()


def ScriptToggle(state):
    # Tells you if the script is enabled or not, state is a boolean
    return


# ---------------------------------------
#   Processing functions
# ---------------------------------------
def has_command_format(first_word):
    return first_word[0] == "!"


def add_command(new_counter, user, message=None):
    if Parent.HasPermission(user, m_ModeratorPermission, ""):
        if has_command_format(new_counter):
            if new_counter not in m_CounterHash:
                m_CounterHash[new_counter] = 0
                if message is not None:
                    m_MessagesHash[new_counter] = message
                    save_messages()
                Parent.SendTwitchMessage("/me counter %s has been successfully created" % new_counter)
                save_counters()
            else:
                Parent.SendTwitchMessage("/me counter %s did already exist" % new_counter)
        else:
            Parent.SendTwitchMessage("/m %s is not in the correct format" % new_counter)


def remove_command(old_counter, user):
    if Parent.HasPermission(user, m_ModeratorPermission, ""):
        if old_counter in m_CounterHash:
            del m_CounterHash[old_counter]
            if old_counter in m_PermissionsHash:
                del m_PermissionsHash[old_counter]
                save_permissions()
            if old_counter in m_MessagesHash:
                del m_MessagesHash[old_counter]
                save_messages()
            Parent.SendTwitchMessage("/me counter %s has been successfully removed" % old_counter)
            save_counters()
        else:
            message = ScriptSettings.counter_not_exist.format(old_counter)
            Parent.SendTwitchMessage("/me " + message)


def has_counter_permission(counter, user):
    return Parent.HasPermission(user, *m_PermissionsHash.get(counter, default_permission()))


def get_message_for_counter(counter):
    if counter in m_MessagesHash:
        return m_MessagesHash[counter].format(counter[1:], m_CounterHash[counter])
    else:
        return ScriptSettings.default_counter_message.format(counter[1:], m_CounterHash[counter])


def handle_counter(counter, user, *args):
    if has_counter_permission(counter, user):
        if not Parent.IsOnCooldown(ScriptName, "set %s" % counter):
            if args[0] == "+":
                Parent.AddCooldown(ScriptName, "set %s" % counter, ScriptSettings.set_cd)
                m_CounterHash[counter] += 1
                Parent.SendTwitchMessage(
                    "/me [increased] " + get_message_for_counter(counter))
                save_counters()
            elif args[0] == "-":
                Parent.AddCooldown(ScriptName, "set %s" % counter, ScriptSettings.set_cd)
                m_CounterHash[counter] -= 1
                Parent.SendTwitchMessage(
                    "/me [decreased] " + get_message_for_counter(counter))
                save_counters()
            elif args[0].isdigit():
                Parent.AddCooldown(ScriptName, "set %s" % counter, ScriptSettings.set_cd)
                m_CounterHash[counter] = int(args[0])
                Parent.SendTwitchMessage(
                    "/me [set nb] " + get_message_for_counter(counter))
                save_counters()


def show_counter(counter, user):
    if counter in m_CounterHash:
        message = "/me " + get_message_for_counter(counter)
        send_if_not_on_cd("show %s" % counter, message, user)


def show_user_change_permission_global(user):
    message = "/me " + ScriptSettings.global_permission_toggle_message.format("",
        *m_PermissionsHash.get("Global", default_permission()))
    send_if_not_on_cd("show global permission", message, user)


def toggle_user_change_permission_global(user):
    if Parent.HasPermission(user, m_ModeratorPermission, "") and ScriptSettings.allow_user_change_toggle:
        if m_PermissionsHash.get("Global", default_permission())[0] == m_ModeratorPermission:
            m_PermissionsHash.update(Global=[ScriptSettings.toggle_to, ScriptSettings.toggle_to_info])
        else:
            m_PermissionsHash.update(Global=[m_ModeratorPermission, ""])
        message = "/me [set] " + ScriptSettings.global_permission_toggle_message.format("", *m_PermissionsHash["Global"])
        Parent.SendTwitchMessage(message)
        save_permissions()


def remove_permission(counter, user):
    if Parent.HasPermission(user, m_ModeratorPermission, ""):
        if counter in m_CounterHash:
            if counter in m_PermissionsHash:
                del m_PermissionsHash[counter]
                message = "/me [removed] " + ScriptSettings.on_global_permission_message. \
                    format(counter, *m_PermissionsHash.get("Global", default_permission()))
                Parent.SendTwitchMessage(message)
                save_permissions()
        else:
            message = ScriptSettings.counter_not_exist.format(old_counter)
            Parent.SendTwitchMessage("/me " + message)


def show_permission(counter, user):
    if counter in m_CounterHash:
        if counter in m_PermissionsHash:
            message = "/me " + ScriptSettings.specific_permission_message.format(counter, *m_PermissionsHash[counter])
        else:
            message = "/me " + ScriptSettings.on_global_permission_message. \
                format(counter, *m_PermissionsHash.get("Global", default_permission()))
        send_if_not_on_cd("show permission %s" % counter, message, user)


def send_if_not_on_cd(cd_name, to_send, user):
    if ScriptSettings.use_cd:
        if ScriptSettings.individual_cd:
            if not Parent.IsOnUserCooldown(ScriptName, cd_name, user):
                Parent.SendTwitchMessage(to_send)
                Parent.AddUserCooldown(ScriptName, cd_name, user, ScriptSettings.show_cd)
        else:
            if not Parent.IsOnCooldown(ScriptName, cd_name):
                Parent.SendTwitchMessage(to_send)
                Parent.AddCooldown(ScriptName, cd_name, ScriptSettings.show_cd)
    else:
        Parent.SendTwitchMessage(to_send)


def add_permission(counter, user, *args):
    if Parent.HasPermission(user, m_ModeratorPermission, ""):
        if counter in m_CounterHash:
            args = list(args)
            if len(args) == 1:
                args.append("")
            if len(args) == 2 and args[0] in m_allowed_permissions:
                m_PermissionsHash[counter] = args
                message = "/me [set] " + ScriptSettings.specific_permission_message.format(counter,
                                                                                           *m_PermissionsHash[counter])
                Parent.SendTwitchMessage(message)
                save_permissions()
        else:
            message = ScriptSettings.counter_not_exist.format(counter)
            Parent.SendTwitchMessage("/me " + message)


def edit_message(counter, user, message):
    if Parent.HasPermission(user, m_ModeratorPermission, ""):
        if counter in m_CounterHash:
            m_MessagesHash[counter] = message
            Parent.SendTwitchMessage("/me %s counter's messages has been updated"% counter)
            save_messages()
        else:
            message = ScriptSettings.counter_not_exist.format(counter)
            Parent.SendTwitchMessage("/me " + message)


def remove_message(counter, user):
    if Parent.HasPermission(user, m_ModeratorPermission, ""):
        if counter in m_CounterHash:
            if counter in m_MessagesHash:
                del m_MessagesHash[counter]
                Parent.SendTwitchMessage("/me %s counter's message is back on default" % counter)
                save_messages()
        else:
            message = ScriptSettings.counter_not_exist.format(counter)
            Parent.SendTwitchMessage("/me " + message)


def process_command(data):
    """The data has to be a command"""
    word_count = data.GetParamCount()
    param1 = data.GetParam(0)
    if word_count == 2:
        param2 = data.GetParam(1)
        if param1 == ScriptSettings.addCommand:
            add_command(param2, data.User)
        elif param1 == ScriptSettings.removeCommand:
            remove_command(param2, data.User)
        elif param1 == ScriptSettings.getPermission:
            show_permission(param2, data.User)
        elif param1 == ScriptSettings.removePermission:
            remove_permission(param2, data.User)
        elif param1 == ScriptSettings.editCommand:
            remove_message(param2, data.User)
        elif param1 in m_CounterHash:
            handle_counter(param1, data.User, param2)
    elif word_count == 1:
        if param1 == ScriptSettings.getUserChangePermissionGlobal:
            show_user_change_permission_global(data.User)
        elif param1 == ScriptSettings.toggleUserChangeGlobal:
            toggle_user_change_permission_global(data.User)
        else:
            show_counter(param1, data.User)
    elif word_count > 2:
        param2 = data.GetParam(1)
        args = data.Message.split(' ', maxsplit=2)[2]
        if param1 == ScriptSettings.addPermission:
            add_permission(param2, data.User, *args.split())
        elif param1 == ScriptSettings.addCommand:
            add_command(param2, data.User, args)
        elif param1 == ScriptSettings.editCommand:
            edit_message(param2, data.User, args)


# ---------------------------------------
#   [Required] Execute Data / Process Messages
# ---------------------------------------
def Execute(data):
    global m_CounterHash
    if data.IsFromTwitch() and data.IsChatMessage():
        param1 = data.GetParam(0)
        if has_command_format(param1):
            process_command(data)
    return


# ---------------------------------------
#   [Required] Tick Function
# ---------------------------------------
def Tick():
    return
