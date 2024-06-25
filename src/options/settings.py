import os

# #################### CONSTANTS ########################
HOME_DIR = os.path.expanduser("~")
# WORK_DIR = os.path.join(os.getcwd(), "..")
WORK_DIR = os.getcwd()
print("WORK_DIR:", WORK_DIR)

# ################### ExifTool_Config ###################
EXIFTOOL_CONFIG_FILENAME = "../.ExifTool_config"
HELPER_FILES_DIR = "../helper_files"
# EXIFTOOL_CONFIG_FILE = os.path.join(HOME_DIR, EXIFTOOL_CONFIG_FILENAME)
EXIFTOOL_CONFIG_FILE = os.path.join(WORK_DIR, EXIFTOOL_CONFIG_FILENAME)
# print("EXIFTOOL_CONFIG_FILE: %s" % EXIFTOOL_CONFIG_FILE)
HELPER_EXIF_CONFIG_FILE = os.path.join(WORK_DIR, HELPER_FILES_DIR, EXIFTOOL_CONFIG_FILENAME)

# #################### Version ###########################
VERSION = "0.7.5"
