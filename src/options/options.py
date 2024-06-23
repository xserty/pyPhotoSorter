import os
import pickle

'''
Do we need a singleton?
Can it be implemented in a module?
If so, can data be saved and loaded to and from disk?
'''


source_media_dir = ''
sorted_media_dir = ''
unsorted_media_dir = ''
deep_mode_hash = True
regenerate_media_dictionary = False
cleanup_dictionary = False
ignore_date_in_path = False
max_num_of_threads = 4 * os.cpu_count()

HOME_DIR = os.path.expanduser("~")
OPTIONS_PICKLE_FILE = os.path.join(HOME_DIR, '.pyPhotoSorter_options.dat')
DICTIONARY_PICKLE_FILE = os.path.join(sorted_media_dir, 'psMediaDictionary.dat')
DELETED_ITEMS_PICKLE_FILE = os.path.join(sorted_media_dir, 'deleted_items.dat')


def save_to_disk():
    options_dict = {"source_media_dir": source_media_dir, "sorted_media_dir": sorted_media_dir, "unsorted_media_dir": unsorted_media_dir, "deep_mode_hash": deep_mode_hash, "regenerate_media_dictionary": regenerate_media_dictionary, "cleanup_dictionary": cleanup_dictionary, "ignore_date_in_path": ignore_date_in_path, "max_num_of_threads": max_num_of_threads}

    with open(OPTIONS_PICKLE_FILE, 'wb') as file:
        print("saving: ", OPTIONS_PICKLE_FILE)
        pickle.dump(options_dict, file)


def load_from_disk():
    """try load self.name.txt"""
    with open(OPTIONS_PICKLE_FILE, 'rb') as file:
        global source_media_dir, sorted_media_dir, unsorted_media_dir, deep_mode_hash, regenerate_media_dictionary, cleanup_dictionary, ignore_date_in_path, max_num_of_threads
        print("loading: ", OPTIONS_PICKLE_FILE)
        options_dict = pickle.load(file)
        source_media_dir = options_dict["source_media_dir"]
        sorted_media_dir = options_dict["sorted_media_dir"]
        unsorted_media_dir = options_dict["unsorted_media_dir"]

        deep_mode_hash = options_dict["deep_mode_hash"]
        regenerate_media_dictionary = options_dict["regenerate_media_dictionary"]
        cleanup_dictionary = options_dict["cleanup_dictionary"]
        ignore_date_in_path = options_dict["ignore_date_in_path"]
        max_num_of_threads = options_dict["max_num_of_threads"]
