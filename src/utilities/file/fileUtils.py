import errno
import filecmp
import hashlib
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from sys import platform

from src.utilities.reporting import Reporting
# from src.settings import EXIFTOOL_CONFIG_FILE, HELPER_EXIF_CONFIG_FILE
from src.options import options, settings

def copy_file(full_filename, destination):
    """
    Copy a media file to destination
    :param full_filename:
    :param destination:
    :return:
    """
    print("\tCopying %s to %s..." % (full_filename, destination))
    shutil.copy2(full_filename, destination)


def delete_file(full_filename):
    print("\tDeleting file %s..." % full_filename)
    if os.path.exists(full_filename):
        os.remove(full_filename)
    else:
        print("Nothing to delete. The file does not exist: '%s'" % full_filename)


def backup_file(full_filename=''):
    dt_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_filename = full_filename + '_' + dt_string + '.bak'
    if os.path.exists(full_filename):
        copy_file(full_filename, new_filename)
    else:
        print("Nothing to backup. The file does not exist: '%s'" % full_filename)


def generate_file_md5(filename, blocksize=2 ** 20):
    """
    2 ** 20 = 1MB
    2 ** 21 = 2MB
    2 ** 22 = 4MB
    2 ** 23 = 8MB
    2 ** 24 = 16MB
    2 ** 25 = 32MB
    ...
    2 ** 30 = 1GB
    2 ** 31 = 2GB
    2 ** 32 = 4GB
    :param filename:
    :param blocksize:
    :return:
    """
    m = hashlib.md5()
    with open(filename, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()


def copy_media_to_unsorted_dir(src_file, target_dir):
    """
    Copy file to target directory including parents directory
    :param src_file:
    :param target_dir:
    :return:
    """
    if not os.path.exists(options.unsorted_media_dir):
        os.makedirs(options.unsorted_media_dir)
    file_dir = os.path.dirname(src_file)
    dest_dir = os.path.normpath(os.path.join(target_dir, os.path.relpath(file_dir)))
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    print("\tCopying %s to %s..." % (src_file, dest_dir))
    shutil.copy2(src_file, dest_dir)
    Reporting.total_num_of_unsorted_files += 1


def remove_sorted_img_dir():
    if os.path.exists(options.source_media_dir):
        shutil.rmtree(options.source_media_dir)
        print(f"'{options.source_media_dir}' directory removed successfully")


def create_sorted_img_dir():
    if not os.path.exists(options.source_media_dir):
        os.mkdir(options.source_media_dir)
        print(f"'{options.source_media_dir}' directory created successfully")
    else:
        print(f"'{options.source_media_dir}' directory exists already")


def generate_exiftool_config():
    # Todo: Surely this can be improved too!!
    exif_conf_file = Path(settings.EXIFTOOL_CONFIG_FILE)
    if exif_conf_file.is_file():

        # check if files differ
        print("WARNING: doing a shallow compare on EXIFTool_config files")
        if not filecmp.cmp(settings.EXIFTOOL_CONFIG_FILE, settings.HELPER_EXIF_CONFIG_FILE, shallow=True):
            print("In generate_exiftool_config...")
            if os.path.exists(settings.EXIFTOOL_CONFIG_FILE):
                print("Renaming ExifTool_config old file...")
                dt_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                os.rename(settings.EXIFTOOL_CONFIG_FILE, settings.EXIFTOOL_CONFIG_FILE + '_' + dt_string + '.bak')
            # the file ExifTool_config does not exist
            print(f"Creating {settings.EXIFTOOL_CONFIG_FILE}.")
            shutil.copy(settings.HELPER_EXIF_CONFIG_FILE, f"{settings.EXIFTOOL_CONFIG_FILE}")
            print(f"Done creating {settings.EXIFTOOL_CONFIG_FILE}.")
        else:
            print(f"No need to replace {settings.EXIFTOOL_CONFIG_FILE}.")

    else:
        print(f"Creating {settings.EXIFTOOL_CONFIG_FILE}.")
        shutil.copy(settings.HELPER_EXIF_CONFIG_FILE, f"{settings.EXIFTOOL_CONFIG_FILE}")
        print(f"Done creating {settings.EXIFTOOL_CONFIG_FILE}.")


def get_image_format(full_filename):
    # img_format = ''
    # try:
    #     # Read image into imageio for data type
    #     # pic = imageio.imread(full_filename)
    #     # [ToDo] Do we need PIL to get the image format? Do we need to know the image format, or can we just deduce from the file extension?
    #     # Read image into PIL to extract basic metadata
    #     img = Image.open(full_filename)
    #     img_format = img.format
    #     # do we need information from img_format.getexif()?
    #     # exif = img_format.getexif()
    #     # img.show()
    #     # if we are done with the image, close it (PIL uses lazy loading)
    #     img.close()
    # except OSError:
    #     print("ERROR: PIL is unable to read file format for: %s " % full_filename)
    # if not img_format:
    #     print("WARNING: Getting format from file extension.")
    filename, file_extension = os.path.splitext(full_filename)
    img_format = file_extension.split('.')[1]
    print(f"Format: {img_format}")
    return img_format

# Found following here:
# https://stackoverflow.com/questions/55394905/how-to-find-the-location-of-an-executable-in-python
def _is_tool(name):
    try:
        devnull = open(os.devnull)
        subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
    except OSError as e:
        if e.errno == errno.ENOENT:
            return False
    return True

def find_prog(prog):
    if _is_tool(prog):
        cmd = "where" if platform.system() == "Windows" else "which"
        try:
            return subprocess.check_output([cmd, prog])
        except subprocess.CalledProcessError:
            return None
