import os
import ac

section = ''

# This flag tells wether the config has changed and needs to be written to the disk
update = False

# Those are the imports needed to set the defaults.
# Change your imports according to your needs and project
import sam_secondz_xyro

# We'll need to find the user's "documents" folder even it it has been moved away
# from the default C:\users\<user>\Documents\. This is a solution by never_eat_yellow_snow
import winreg

def expand_ac(*args):
    k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
    v = winreg.QueryValueEx(k, "Personal")
    return os.path.join(v[0], *args)

def handleIni(appName):
    global update, section
    section = appName
    iniDirectory = expand_ac("Assetto Corsa/cfg/apps/")

    iniFile = iniDirectory + appName + '.ini'
    if not os.path.exists(iniDirectory):
        update = True
        ac.log('ini directory ' + iniDirectory + ' does not exist, try to create it')
        os.makedirs(iniDirectory)
    try:
        from configparser import ConfigParser
    except ImportError:
        from ConfigParser import ConfigParser  # ver. < 3.0
    config = ConfigParser()
    config.read(iniFile)

    # if there is no ini-file (with an 'appName' section), we will create one
    # with the default values. This way we get configurable stuff
    # which is never overwritten by updates or even Steam Workshop
    if config.has_section(appName) != True:
        config.add_section(appName)
        update = True

    # Then we'll feed all the constants with either the ini
    # values, but they also can be overridden by the defaults
    sam_secondz_xyro.UDP_IP = getOrSetDefaultString(config, 'UDP_IP', "127.0.0.1")
    sam_secondz_xyro.UDP_PORT = getOrSetDefaultInt(config, 'UDP_PORT', 59481)
    sam_secondz_xyro.DEVICE_ID = int(getOrSetDefaultString(config, 'DEVICE_ID', "ac00000000000001"), 16)
    

    # If anything was written to the config, we'll have to write this to the config file
    # in the end
    if update == True:
        ac.log('Updates to ini file detected, will update ' + iniFile)
        with open(iniFile, 'w') as configfile:
            config.write(configfile)

def getOrSetDefaultString(config, key, default):
    global update
    try:
        return config.get(section, key)
    except:
        config.set(section, key, str(default))
        update=True
        return default

def getOrSetDefaultInt(config, key, default):
    global update
    try:
        return config.getint(section, key)
    except:
        config.set(section, key, str(default))
        update=True
        return default

def getOrSetDefaultFloat(config, key, default):
    global update
    try:
        return config.getfloat(section, key)
    except:
        config.set(section, key, str(default))
        update=True
        return default

def getOrSetDefaultFloatArray(config, key, defaultR, defaultG, defaultB):
    global update
    try:
        floatArray = []
        i = 0
        for f in config.get(section, key).split(","):
            floatArray[i] = float(f)
            i = i + 1
        return floatArray
    except:
        config.set(section, key, str("{},{},{}".format(defaultR, defaultG, defaultB)))
        update=True
        return [ defaultR, defaultG, defaultB ]
