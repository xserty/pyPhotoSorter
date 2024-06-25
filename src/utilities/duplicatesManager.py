import time

from src.utilities.hashstore import HashStore


class DuplicatesManager:

    def __init__(self, hashstore_filename, hashstore_duplicates_filename):
        self.hst_filename = hashstore_filename
        self.hst_dup_filename = hashstore_duplicates_filename
        self.elapsed_time = 0

    # Decorator to calculate duration taken by any function
    def measure_execution_time(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Function {func.__name__} took {execution_time:.4f} seconds to execute")
            return result
        return wrapper

    @measure_execution_time
    def manage_duplicates(self):
        print('')
        print("Starting to manage Duplicates...")
        # with open(self.hst_filename, 'r+b') as fd, open(self.hst_dup_filename, 'r+b') as dup_fd:
        hst = HashStore(self.hst_filename, self.hst_dup_filename, is_find_duplicates=True)
        with hst:
            while True:
                # Get next duplicate media line from duplicates file
                dup_line = hst.dup_fd.readline()
                # if line is empty or end of file is reached
                if not dup_line:
                    break
                if dup_line.startswith('#'):
                    # ignore 'comments' (lines starting with '#')
                    continue

                dup_csv_line = dup_line.split(',')
                dup_file_name = dup_csv_line[0]
                dup_hash_val = dup_csv_line[1]
                dup_file_size = dup_csv_line[2]
                dup_date = dup_csv_line[3]
                print("Processing duplicate media: ")
                print(dup_file_name, dup_hash_val, dup_file_size, dup_date)
                # create the string to look for in the original HashStore file
                dup_hst_value = "{},{}".format(dup_hash_val, dup_file_size)
                # start reading the file from the beginning
                hst.fd.seek(0)
                while True:
                    # look for that value in the hstStore file
                    # and replace that line with media from duplicates file which has older date-time
                    #
                    # Get next line from HashStore file
                    orig_line = hst.fd.readline()
                    # if line is empty or end of file is reached
                    if not orig_line:
                        break
                    if orig_line.startswith('#'):
                        # ignore 'comments' (lines starting with '#')
                        continue

                    if dup_hst_value in orig_line:
                        print("Found line with hst value: %s " % dup_hst_value)
                        orig_csv_line = orig_line.split(',')
                        orig_file_name = orig_csv_line[0]
                        orig_hash_val = orig_csv_line[1]
                        orig_file_size = orig_csv_line[2]
                        orig_date = orig_csv_line[3]
                        print("Original file found: ", orig_file_name, orig_hash_val, orig_file_size, orig_date)
                        # check sorting dates
                        if dup_date < orig_date:
                            print("SORT OUT: Sorting dates of the two files differ... Need to exchange file location")
                            # now we have to do the following steps:
                            # 1. copy older duplicate media 'dup_file_name' to it's sorted img dir
                            # 2. add new line 'dup_line' to temp HashStore file
                            # 3. remove line from duplicates file (write nothing to new file)
                            # 4. remove newer media 'orig_file_name' from sorted img dir
                            # 5. move temp HashStore file to its final name 'main.HASHSTORE_FILE'
                        else:
                            print("NOTHING TO DO: Sorting dates of the two files are sorted correctly")
                            # write 'orig_line' to temp HashStore file
                        break
                print("----------------")

    # @classmethod
    # def findDuplicateInOriginalFile(cls, hst, dup_hash_val, dup_file_size):
    #     orig_file_name = ''
    #     orig_hash_val = ''
    #     orig_file_size = ''
    #     orig_date = ''
    #     hst_value = "{},{}".format(dup_hash_val, dup_file_size)
    #     hst.fd.flush()
    #     os.fsync(hst.fd)
    #     hst.fd.seek(0)
    #     while True:
    #         # Get next line from file
    #         line = hst.fd.readline().decode('utf-8')
    #         # if line is empty or end of file is reached
    #         if not line:
    #             break
    #
    #         if hst_value in line:
    #             print("Found line with HashStore value: %s " % hst_value)
    #             csv_line = line.split(',')
    #             orig_file_name = csv_line[0]
    #             orig_hash_val = csv_line[1]
    #             orig_file_size = csv_line[2]
    #             orig_date = csv_line[3]
    #             print("Original file found: ", orig_name, orig_val, orig_file_size, orig_date)
    #             # check sorting dates
    #             if dup_date < orig_date:
    #                 print("SORT OUT: Sorting dates of the two files differ... Need to exchange file location")
    #
    #             else:
    #                 print("NOTHING TO DO: Sorting dates of the two files are sorted correctly")
    #
    #             break
    #
    #     # fd.seek(1, os.SEEK_END)
    #     return orig_file_name, orig_hash_val, orig_file_size, orig_date
