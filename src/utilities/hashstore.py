import os
import hashlib
from datetime import datetime


class HashStore:
    """
    Should be using HashMaps for this
    https://stackoverflow.com/questions/51209510/serializing-hashmap-and-writing-into-a-file
    Interesting:
    https://codereview.stackexchange.com/questions/130063/implementing-cleartable-grow-and-shrink-on-a-hash-table
    Store file path, hash, size and oldest date-time in csv format
    """
    def __init__(self, hashstore_filename, hashstore_duplicates_filename, is_find_duplicates=False):
        print("Entered 'init' method...")
        self.hst_value = ''
        self.hst_filename = hashstore_filename
        self.hst_dup_filename = hashstore_duplicates_filename
        self.media_oldest_date = ''
        self.fd = None
        self.dup_fd = None
        self.isFindDuplicates = is_find_duplicates
        if not is_find_duplicates:
            print("Creating HashStore files...")
            try:
                if os.path.exists(self.hst_filename):
                    print("Renaming old hst file...")
                    dt_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    os.rename(self.hst_filename, self.hst_filename + '_' + dt_string + '.bak')
                if os.path.exists(self.hst_dup_filename):
                    print("Renaming old hst duplicates file...")
                    dt_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    os.rename(self.hst_dup_filename, self.hst_dup_filename + '_' + dt_string + '.bak')
            except IOError as ex:
                print(f"ERROR: An error occurred while generating new HashStore files: {ex}")

    def __enter__(self):
        print("Entered 'enter' method...")
        try:
            # Opening files in 'w+' will truncate the files (delete its contents)
            # Note if that is not what you want, open files in 'r+' mode
            if self.isFindDuplicates:
                # read-only mode to allow rewriting a new updated file
                mode = 'r'
            else:
                mode = 'w+'
            self.fd = open(self.hst_filename, mode)
            self.dup_fd = open(self.hst_dup_filename, mode)
            self.write_hst_headers()
            self.write_hst_headers(is_dup=True)
        except IOError as ex:
            print(f"ERROR: An error occurred while opening HashStore files: {ex}")
        return self.fd

    def __exit__(self, *args):
        print("Entered 'exit' method...")
        self.fd.flush()
        self.fd.close()
        self.dup_fd.flush()
        self.dup_fd.close()

    def write_hst_headers(self, is_dup=False):
        if not is_dup:
            self.fd.write("# HashStore\n")
            self.fd.write(f"# Generated on {datetime.now()}\n")
            self.fd.write("#\n")
            self.fd.write("# ################################################################################\n")
            self.fd.write("# # WARNING: DO NOT REMOVE OR EDIT THIS FILE UNLESS YOU KNOW WHAT YOU ARE DOING! #\n")
            self.fd.write("# ################################################################################\n")
            self.fd.write("#\n")
        else:
            self.dup_fd.write("# HashStore - Duplicate Files List\n")
            self.dup_fd.write(f"# Generated on {datetime.now()}\n")
            self.dup_fd.write("#\n")
            self.dup_fd.write("# ################################################################################\n")
            self.dup_fd.write("# # WARNING: DO NOT REMOVE OR EDIT THIS FILE UNLESS YOU KNOW WHAT YOU ARE DOING! #\n")
            self.dup_fd.write("# ################################################################################\n")
            self.dup_fd.write("#\n")

    # def write_to_file(self, is_hst_duplicate=False):
    #     if not self.hst_value:
    #         print("DEV ERROR: Unable to write to HashStore file. hst_value has not been set.")
    #         return
    #     if not is_hst_duplicate:
    #         try:
    #             line = "{},{},{}".format(self.full_media_filename, self.hst_value, self.media_oldest_date)
    #             self.fd.write(line)
    #             self.fd.write("\n")
    #         except OSError as er:
    #             print("Unable to write HashStore file.")
    #     else:
    #         try:
    #             line = "{},{},{}".format(self.full_media_filename, self.hst_value, self.media_oldest_date)
    #             self.dup_fd.write(line)
    #             self.dup_fd.write("\n")
    #         except OSError as er:
    #             print("Unable to write HashStore duplicates file.")

    # def set_hst_value(self, full_media_filename):
    #     self.full_media_filename = full_media_filename
    #     file_stats = os.stat(self.full_media_filename)
    #     size = file_stats.st_size
    #     # Open,close, read file and calculate MD5 on its contents
    #     with open(self.full_media_filename, 'rb') as f:
    #         # read contents of the file
    #         data = f.read()
    #         # pipe contents of the file through
    #         md5 = hashlib.md5(data).hexdigest()
    #     hst_val = "{},{}".format(md5, size)
    #     hst_val = self.__getHstValue()

    # def is_duplicate_media(self):
    #     # [ToDo] this can be optimised by checking filesize by using a multi step approach.
    #     #       If filesize is same, then we can eventually calculate MD5
    #     result = False
    #     self.fd.flush()
    #     os.fsync(self.fd)
    #     self.fd.seek(0)
    #
    #     while True:
    #         # Get next line from file
    #         line = self.fd.readline()
    #         # if line is empty or end of file is reached
    #         if not line:
    #             break
    #
    #         if self.hst_value in line:
    #             print("This is a DUPLICATE file: not moving/copying file.")
    #             print("HashStore value: %s " % self.hst_value)
    #             result = True
    #             break
    #
    #     self.fd.seek(0, os.SEEK_END)
    #     return result
