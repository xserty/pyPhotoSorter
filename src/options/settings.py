import os

# #################### CONSTANTS ########################
HOME_DIR = os.path.expanduser("~")
_OPTIONS_DIR = os.path.dirname(os.path.abspath(__file__))   # src/options/
_SRC_DIR = os.path.dirname(_OPTIONS_DIR)                     # src/
WORK_DIR = os.path.dirname(_SRC_DIR)                         # project root
print("WORK_DIR:", WORK_DIR)

# ################### ExifTool_Config ###################
EXIFTOOL_CONFIG_FILENAME = ".ExifTool_config"
HELPER_FILES_DIR = "helper_files"
EXIFTOOL_CONFIG_FILE = os.path.join(WORK_DIR, EXIFTOOL_CONFIG_FILENAME)
HELPER_EXIF_CONFIG_FILE = os.path.join(_SRC_DIR, HELPER_FILES_DIR, EXIFTOOL_CONFIG_FILENAME)

# #################### Version ###########################
VERSION = "0.7.6"
