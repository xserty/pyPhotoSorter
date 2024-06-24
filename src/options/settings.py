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

# Exiftool executable
#exiftool_path = os.path.abspath("./exiftool.exe")
# EXIFTOOL_PATH = os.path.abspath("/usr/bin/exiftool")

# #################### Pickle ###########################
# DICTIONARY_PICKLE_FILE = os.path.join(options.sorted_media_dir, 'psMediaDictionary.dat')
# DELETED_ITEMS_PICKLE_FILE = os.path.join(options.sorted_media_dir, 'deleted_items.dat')
# Options settings
# OPTIONS_PICKLE_FILE = os.path.join(HOME_DIR, '.pyPhotoSorter_options.dat')
# OPTIONS_PICKLE_FILE = 'options.dat'

# ################## Parameters #########################
DEEP_MODE_HASH = True
REGENERATE_MEDIA_DICTIONARY = False
# Cleanup dictionary pickle file (remove items that do not correspond to an existing file in the sorted directory)
# CLEAN_UP_DICTIONARY = True
CLEAN_UP_DICTIONARY = False
# when looking for the oldest date, ignore any date in the file path
# Note: this is used when regenerating the MediaDictionary pickle file that reads files from the
#       sorted directory
IGNORE_DATE_IN_PATH = False

# #################### Version ###########################
VERSION = "0.7.5"
