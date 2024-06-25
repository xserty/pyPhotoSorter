import logging
import os.path
from datetime import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, ALL_COMPLETED
import re

from src.options import options
from src.utilities.exifDateUtils import get_all_possible_dates
from src.utilities.file.fileUtils import generate_exiftool_config, create_sorted_img_dir
from src.utilities.reporting import Reporting
from src.utilities.psMediaDictionary import MediaDictionary
from src.utilities.file import fileUtils


log = logging.getLogger('pyPhotoSorter.imageSort')

# futures list
futures = []

class ImageSort:

    # def __new__(cls):
    #     if img_dir and not os.path.exists(img_dir):
    #         print(f"Image directory '{img_dir}' not found.")
    #         raise FileNotFoundError(1, "Image directory not found.", img_dir)
    #     instance = super(ImageSort, cls).__new__(cls)
    #     instance.img_dir = img_dir
    #     instance.sorted_dir = sorted_dir
    #     instance.unsorted_dir = unsorted_dir
    #     return instance

    # def __new__(cls, img_dir=None, sorted_dir=None, unsorted_dir=None, deep_mode_hash=True):
    #     if img_dir and not os.path.exists(img_dir):
    #         print(f"Image directory '{img_dir}' not found.")
    #         raise FileNotFoundError(1, "Image directory not found.", img_dir)
    #     instance = super(ImageSort, cls).__new__(cls)
    #     instance.img_dir = img_dir
    #     instance.sorted_dir = sorted_dir
    #     instance.unsorted_dir = unsorted_dir
    #
    #     return instance

    def __init__(self, args_dict):
        self.elapsed_time = 0
        self.img_dir = args_dict['img_dir']
        self.sorted_dir = args_dict['sorted_dir']
        self.unsorted_dir = args_dict['unsorted_dir']
        self.deep_mode_hash = args_dict['deep_mode_hash']
        self.ignore_date_in_path = args_dict['ignore_date_in_path']
        self.regen_media_dict = args_dict['regen_media_dict']
        self.cleanup_dictionary = args_dict['cleanup_dictionary']
        self.max_threads_num = args_dict['max_threads_num']
        self.psMediaDictionary = MediaDictionary()
        self.psMediaDictionary.deepModeHash = self.deep_mode_hash
        self.psMediaDictionary.sorted_media_dir = self.sorted_dir
        self.psMediaDictionary.unsorted_media_dir = self.unsorted_dir

    # Decorator to calculate duration taken by any function
    def _calculate_time_decorator(func):
        # added arguments inside the inner1
        def decorator(img_sort_instance, *args, **kwargs):
            # storing time before function execution
            begin = dt.now()
            # x = func(*args, **kwargs)
            func(img_sort_instance, *args, **kwargs)
            # func(calling_instance, *args, **kwargs)
            # storing time after function execution
            end = dt.now()
            img_sort_instance.elapsed_time = end - begin
            Reporting.dt_elapsed_time = img_sort_instance.elapsed_time
            # print(f"Total time taken in :  {func.__name__}  {self.total_time}")
        return decorator

    def _sort_media(self, full_filename, ignore_date_in_file_path=False):
        # time.sleep(2)
        # print("=== Semaphore value: ", semaphore._value)
        # semaphore.acquire()
        # semaphore.acquire(blocking=True)
        # print("=== Semaphore value: ", semaphore._value)
        # get a sorted list of possible dates. position [0] being the oldest
        list_of_possible_dates = get_all_possible_dates(full_filename, ignore_date_in_file_path=ignore_date_in_file_path)

        if not list_of_possible_dates:
            # move this file to unsorted
            print("WARNING: Unable to find a date for this file.")
            media_obj = self.psMediaDictionary.get_media_object_by_filename(full_filename)
            if media_obj:
                print("Existing media object in dictionary has following oldest date: %s" % media_obj.oldest_date)
            # Tried removing media object below, but ends up deleting files (of same ps_key) that actually have a exif date
            # # remove any reference in the psMediaDictionary
            # self.psMediaDictionary.remove_media_object_by_filename(full_filename)
            if not self.regen_media_dict:
                print("Copying media to unsorted dir '%s'" % self.unsorted_dir)
                fileUtils.copy_media_to_unsorted_dir(full_filename, self.unsorted_dir)
            return

        # date[0] will contain the oldest date (as getAllPossibleDates returns a sorted list)
        year, month, day = list_of_possible_dates[0].split(" ")[0].split(":", 2)
        # print(year, month, day)

        media_oldest_date = "{}:{}:{}".format(year, month, day)
        dest_dir = ''
        if not self.regen_media_dict:
            dest_dir = os.path.join(self.sorted_dir, year, month, day)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
        # write the psHashMap
        self.psMediaDictionary.add(full_filename=full_filename, oldest_date_time=media_oldest_date, destination_dir=dest_dir, regenerate_media_dictionary=self.regen_media_dict)
        # semaphore.release()

    @_calculate_time_decorator
    def _main_media_sort(self):
        # reset reporting counters
        Reporting.reset()
        print(f"Parameters passed: ")
        print(f"\tMedia directory to be sorted: '{self.img_dir}'")
        print(f"\tOutput directory of sorted media: '{self.sorted_dir}'")
        # total number of files in directory and subdirectories
        cpt = sum([len(files) for r, d, files in os.walk(self.img_dir)])
        print("Total number of media files to sort: %i" % cpt)

        # load the dictionary file if it exists
        self.psMediaDictionary.load_dictionary_from_pickle_file()

        count = 0
        print("Max threads set to: ", self.max_threads_num)
        with ThreadPoolExecutor(max_workers=self.max_threads_num) as executor:

            for dir_path, dir_names, filenames in os.walk(self.img_dir):
                for filename in filenames:
                    count += 1
                    Reporting.total_num_of_files += 1

                    full_filename = os.path.join(dir_path, filename)
                    print("")
                    print("===============================")
                    print(f"Found file {count}:\t\t\t{full_filename}")

                    percent = count / cpt * 100
                    display = f"Processing file {count}/{cpt} ("
                    display += '{:.2f}%'.format(percent)
                    display += ")"
                    print(display)
                    # self._gui_instance.setProgress(int(percent))

                    # [ToDo] Match '~*~' format file extensions
                    file_extension = fileUtils.get_image_format(full_filename)
                    match file_extension.lower():
                        case 'crc' | 'bak' | 'ini' | '411' | 'thm' | 'htm' | 'html' | 'json' | 'txt' | 'db' | 'log' | 'tgz' | 'aae' | 'xcf' | 'zip' | 'pdf' | 'odt' | 'sla' | 'odg' | 'svg' | 'ora' | 'b64' | 'ind':
                            print("INFO: Ignoring file...")
                            Reporting.total_num_of_ignored_files += 1
                        case _:
                            # check if extension matches "~*~" format. If it matches, skip sort execution and ignore file
                            regex = re.compile(r"~\d*~")
                            if not regex.match(file_extension):
                                # self._sort_media(full_filename, ignore_date_in_file_path=IGNORE_DATE_IN_PATH)
                                # start a thread and add the resulting futures object (the result) to the futures list
                                # execute the task, passing the event
                                future = executor.submit(self._sort_media, full_filename, options.ignore_date_in_path)
                                futures.append(future)
                                # Main thread is counted by activeGThread() so removing 1 to the count
                                # print("Number of active threads: %d " % (threading.active_count() - 1))
                                # print(threading.enumerate())
                            else:
                                print("+++++++++++++++++++++++++++++++++++++++++++++ Ignoring extension: '%s'" % file_extension)

        done, not_done = wait(futures, return_when=ALL_COMPLETED)
        # print("Done: %s", "\n", "Not Done: %s" % (str(done), str(not_done)))

        print('===================================================================================================')
        print('Sort finished')
        print(self.psMediaDictionary)
        print('Saving dictionary...')
        self.psMediaDictionary.save_dictionary_to_pickle_file()
        print('Done.')

    @_calculate_time_decorator
    def generate_media_dictionary(self, ignore_date_in_path=False):
        Reporting.reset()
        self.ignore_date_in_path = ignore_date_in_path
        # rename existing pickle dictionary file
        fileUtils.backup_file(full_filename=options.DICTIONARY_PICKLE_FILE)

        # total number of files in directory and subdirectories
        cpt = sum([len(files) for r, d, files in os.walk(self.sorted_dir)])
        print("Total number of media files to check: %i" % cpt)

        count = 0
        print("Max threads: ", self.max_threads_num)
        with ThreadPoolExecutor(max_workers=self.max_threads_num) as executor:

            for dir_path, dir_names, filenames in os.walk(self.sorted_dir):
                for filename in filenames:
                    count += 1
                    Reporting.total_num_of_files += 1
                    full_filename = os.path.join(dir_path, filename)
                    print("")
                    print("===============================")

                    percent = count / cpt * 100
                    display = f"Processing file {count}/{cpt} ("
                    display += '{:.2f}%'.format(percent)
                    display += ")"
                    print(display)
                    print(f"\t\t{full_filename}")
                    print("")
                    file_extension = fileUtils.get_image_format(full_filename)

                    match file_extension.lower():
                        case 'crc' | 'bak' | 'ini' | '411' | 'thm' | 'htm' | 'html' | 'json' | 'txt' | 'db' | 'log' | 'tgz' | 'aae' | 'xcf' | 'zip' | 'pdf' | 'odt' | 'sla' | 'odg' | 'svg' | 'ora' | 'b64' | 'ind':
                            print("INFO: Ignoring file...")
                            Reporting.total_num_of_ignored_files += 1
                        case _:
                            regex = re.compile(r"~\d*~")
                            if not regex.match(file_extension):
                                print("Sorting file...")
                                # execute the task, passing the event
                                future = executor.submit(self._sort_media, full_filename, options.ignore_date_in_path)
                                futures.append(future)
                                # print("Number of active threads: %d " % (threading.activeCount() - 1))
                                # print(threading.enumerate())
                            else:
                                print("+++++++++++++++++++++++++++++++++++++++++++++ Ignoring extension: '%s'" % file_extension)

        done, not_done = wait(futures, return_when=ALL_COMPLETED)
        # print("Done: %s", "\n", "Not Done: %s" % (str(done), str(not_done)))

        print('===================================================================================================')
        print('Sort finished')
        print(self.psMediaDictionary)
        print('Saving dictionary...')
        self.psMediaDictionary.save_dictionary_to_pickle_file()
        print('Done.')


def main_call(**args_dict):
    img_sort = ImageSort(args_dict)
    # ToDo: following try-catch can be improved
    try:
        generate_exiftool_config()
        # removeSortedImgDir()
        create_sorted_img_dir()
    except (FileNotFoundError, OSError) as e:
        print(f'Caught {type(e)}: {e}')
    if args_dict['regen_media_dict'] and args_dict['cleanup_dictionary']:
        raise AssertionError(
            "Two flags/parameters (REGENERATE_MEDIA_DICTIONARY and CLEAN_UP_DICTIONARY) are mutually exclusive. Both "
            "are set to True")
    if args_dict['regen_media_dict']:
        print("Regenerating media dictionary...")
        # we need to know the UNSORTED_MEDIA_DIR and destination dir SORTED_MEDIA_DIR
        img_sort.regen_media_dict = True
        # img_sort.ignore_date_in_path = IGNORE_DATE_IN_PATH
        img_sort.generate_media_dictionary(ignore_date_in_path=args_dict['ignore_date_in_path'])
    elif args_dict['cleanup_dictionary']:
        print("Cleaning up media pickle dictionary...")
        # Instantiate MediaDictionary
        md = MediaDictionary()
        md.sorted_media_dir = args_dict['sorted_dir']
        md.unsorted_media_dir = args_dict['unsorted_dir']
        md.load_dictionary_from_pickle_file()
        md.cleanup_media_dictionary()
        md.save_dictionary_to_pickle_file()
    else:
        if not args_dict['img_dir']:
            raise LookupError("Options module is empty!?")
        # img_sort = ImageSort(img_dir=options.options.source_media_dir, sorted_dir=options.options.sorted_media_dir,
        # unsorted_dir=options.options.unsorted_media_dir, deep_mode_hash=options.options.deep_mode_hash)
        img_sort = ImageSort(args_dict)
        img_sort._main_media_sort()
        # cleanup the dictionary from entries that have no corresponding sorted file
        if img_sort.psMediaDictionary.is_cleanup_needed:
            img_sort.psMediaDictionary.cleanup_media_dictionary()
        # save media dictionary to pickle file
        img_sort.psMediaDictionary.save_dictionary_to_pickle_file()
    # notify_with_notifpy("pyPhotoSorter", "Finished sorting images.")
    print("=== END ===")
    print("")
    # print a report
    if img_sort:
        if not isinstance(img_sort.elapsed_time, int):
            Reporting.print_stdout_report()
        else:
            # print("Error with Reporting...")
            print("Elapsed time: %s" % str(img_sort.elapsed_time))
