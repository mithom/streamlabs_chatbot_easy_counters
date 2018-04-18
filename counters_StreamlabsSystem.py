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
Version = "1.0.1"

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
        except:
            self.use_cd = True
            self.show_cd = 15
            self.individual_cd = False
            self.set_cd = 5
            self.allow_user_change_toggle = True
            self.toggle_to = "Regular"
            self.toggle_to_info = ""
            self.addCommand = "!addCounter"
            self.removeCommand = "!removeCounter"
            self.addPermission = "!addCounterPermission"
            self.removePermission = "!removeCounterPermission"
            self.getPermission = "!counterPermission"
            self.GetUserChangePermissionGlobal = "!counterPermissions"
            self.toggleUserChangeGlobal = "!toggleCounterPermissions"

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
        Parent.Log(ScriptName, "current counters are: %s" % (str(m_CounterHash)))
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
        Parent.Log(ScriptName, "current permissions are: %s" % (str(m_PermissionsHash)))
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
        Parent.Log(ScriptName, "global was on: %s" % m_PermissionsHash.get("Global", default_permission())[0])
        m_PermissionsHash.update(Global=[ScriptSettings.toggle_to, ScriptSettings.toggle_to_info])
        Parent.SendTwitchMessage(
            "/me the global permission to change counters has been set to %s" % str(m_PermissionsHash["Global"]))


# ---------------------------------------
#   [Required] Intialize Data (Only called on Load)
# ---------------------------------------
def Init():
    global ScriptSettings

    ScriptSettings = Settings(m_SettingsFile)
    load_counters()
    load_permissions()
    fix_global_permission_on_load()


# ---------------------------------------
#   [Optional] Reload settings (Only called on save button press)
# ---------------------------------------
def ReloadSettings(jsondata):
    # load in json after pressing save settings button
    global ScriptSettings
    Parent.Log(ScriptName, jsondata)
    ScriptSettings.reload(jsondata)
    fix_global_permission_on_load()
    Parent.Log(ScriptName, str(ScriptSettings.show_cd))
    return


# ---------------------------------------
#   [Optional] Save data (Only called on exit chatbot)
# ---------------------------------------
def Unload():
    # Triggers when the bot closes / script is reloaded
    save_counters()
    save_permissions()


def ScriptToggle(state):
    # Tells you if the script is enabled or not, state is a boolean
    return


# ---------------------------------------
#   Processing functions
# ---------------------------------------
def has_command_format(first_word):
    return first_word[0] == "!"


def add_command(new_counter, user):
    if Parent.HasPermission(user, m_ModeratorPermission, ""):
        if has_command_format(new_counter):
            if new_counter not in m_CounterHash:
                m_CounterHash[new_counter] = 0
                Parent.SendTwitchMessage("/me counter %s has been successfully created" % new_counter)
            else:
                Parent.SendTwitchMessage("/me counter %s did already exist" % new_counter)
        else:
            Parent.SendTwitchMessage("/m %s is not in the correct format" % new_counter)


def remove_command(old_counter, user):
    if Parent.HasPermission(user, m_ModeratorPermission, ""):
        if old_counter in m_CounterHash:
            del m_CounterHash[old_counter]
            Parent.SendTwitchMessage("/me counter %s has been succesfully removed" % old_counter)
        else:
            Parent.SendTwitchMessage("/me counter %s did not exist" % old_counter)


def has_counter_permission(counter, user):
    return Parent.HasPermission(user, *m_PermissionsHash.get(counter, default_permission()))


def handle_counter(counter, user, *args):
    if has_counter_permission(counter, user):
        if not Parent.IsOnCooldown(ScriptName, "set %s" % counter):
            if args[0] == "+":
                Parent.AddCooldown(ScriptName, "set %s" % counter, ScriptSettings.set_cd)
                m_CounterHash[counter] += 1
                Parent.SendTwitchMessage(
                    "/me [increased] current %s count is %s" % (counter[1:], m_CounterHash[counter]))
                save_counters()
            elif args[0] == "-":
                Parent.AddCooldown(ScriptName, "set %s" % counter, ScriptSettings.set_cd)
                m_CounterHash[counter] -= 1
                Parent.SendTwitchMessage(
                    "/me [decreased] current %s count is %s" % (counter[1:], m_CounterHash[counter]))
                save_counters()
            elif args[0].isdigit():
                Parent.AddCooldown(ScriptName, "set %s" % counter, ScriptSettings.set_cd)
                m_CounterHash[counter] = int(args[0])
                Parent.SendTwitchMessage(
                    "/me [set nb] current %s count is %s" % (counter[1:], m_CounterHash[counter]))
                save_counters()


def show_counter(counter, user):
    if counter in m_CounterHash:
        message = "/me current %s count is %s" % (counter[1:], m_CounterHash[counter])
        send_if_not_on_cd("show %s" % counter, message, user)


def show_user_change_permission_global(user):
    message = "/me current global permission to change counters is %s" % str(
        m_PermissionsHash.get("Global", default_permission()))
    send_if_not_on_cd("show global permission", message, user)


def toggle_user_change_permission_global(user):
    if Parent.HasPermission(user, m_ModeratorPermission, "") and ScriptSettings.allow_user_change_toggle:
        if m_PermissionsHash.get("Global", default_permission())[0] == m_ModeratorPermission:
            m_PermissionsHash.update(Global=[ScriptSettings.toggle_to, ScriptSettings.toggle_to_info])
        else:
            m_PermissionsHash.update(Global=[m_ModeratorPermission, ""])
        Parent.SendTwitchMessage(
            "/me the global permission to change counters has been set to %s" % str(
                m_PermissionsHash["Global"]))
        save_permissions()


def remove_permission(counter, user):
    if Parent.HasPermission(user, m_ModeratorPermission, ""):
        if counter in m_PermissionsHash:
            del m_PermissionsHash[counter]
            Parent.SendTwitchMessage("/me the counter %s is back on the global permission" % counter)
            save_permissions()


def show_permission(counter, user):
    if counter in m_PermissionsHash:
        message = "/me the permission for %s is %s" % (counter, m_PermissionsHash[counter])
    else:
        message = "the counter %s is on the global permission" % counter
    Parent.Log(ScriptName, message)
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
                Parent.SendTwitchMessage(
                    "/me counter %s permission is set to %s" % (counter, str(m_PermissionsHash[counter])))
                save_permissions()
        else:
            Parent.SendTwitchMessage("/me counter %s does not exist" % counter)


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
        args = data.Message.split()[2:]
        if param1 == ScriptSettings.addPermission:
            add_permission(param2, data.User, *args)


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
