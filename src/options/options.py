import os
import pickle
import threading

'''
Python loads a module only once per program, so instances created in a
module are effectively singletons when used elsewhere in the program.
'''

# ------------------- internal lock -------------------
_lock = threading.RLock()

# ------------------- static state -------------------
source_media_dir = ''
sorted_media_dir = ''
unsorted_media_dir = ''
# flags
deep_mode_hash = True
regenerate_media_dictionary = False
cleanup_dictionary = False
ignore_date_in_path = False
# performance
max_num_of_threads = 4 * (os.cpu_count() or 1)
# paths
HOME_DIR = os.path.expanduser("~")
# derived paths
OPTIONS_PICKLE_FILE = os.path.join(HOME_DIR, '.pyPhotoSorter_options.dat')
def get_dictionary_pickle_file():
    """Return the path for the media dictionary pickle file.

    The file is stored in `sorted_media_dir` when set, otherwise falls back to the
    current working directory.
    """
    if sorted_media_dir:
        return os.path.join(sorted_media_dir, '.psMediaDictionary.dat')
    return os.path.join(os.getcwd(), '.psMediaDictionary.dat')


def get_deleted_items_pickle_file():
    """Return the path for the deleted-items pickle file.

    Stored next to the media dictionary inside `sorted_media_dir` when available.
    """
    if sorted_media_dir:
        return os.path.join(sorted_media_dir, 'deleted_items.dat')
    return os.path.join(os.getcwd(), 'deleted_items.dat')

def save_to_disk():
    with _lock:
        data = {
            "source_media_dir": source_media_dir,
            "sorted_media_dir": sorted_media_dir,
            "unsorted_media_dir": unsorted_media_dir,
            "deep_mode_hash": deep_mode_hash,
            "regenerate_media_dictionary": regenerate_media_dictionary,
            "cleanup_dictionary": cleanup_dictionary,
            "ignore_date_in_path": ignore_date_in_path,
            "max_num_of_threads": max_num_of_threads,
        }

    with open(OPTIONS_PICKLE_FILE, "wb") as f:
        pickle.dump(data, f)

def load_from_disk():
    global source_media_dir, sorted_media_dir, unsorted_media_dir
    global deep_mode_hash, regenerate_media_dictionary
    global cleanup_dictionary, ignore_date_in_path, max_num_of_threads

    if not os.path.exists(OPTIONS_PICKLE_FILE):
        return False

    with open(OPTIONS_PICKLE_FILE, "rb") as f:
        data = pickle.load(f)

    with _lock:
        source_media_dir = data.get("source_media_dir", "")
        sorted_media_dir = data.get("sorted_media_dir", "")
        unsorted_media_dir = data.get("unsorted_media_dir", "")
        deep_mode_hash = data.get("deep_mode_hash", True)
        regenerate_media_dictionary = data.get("regenerate_media_dictionary", False)
        cleanup_dictionary = data.get("cleanup_dictionary", False)
        ignore_date_in_path = data.get("ignore_date_in_path", False)
        max_num_of_threads = data.get("max_num_of_threads", max_num_of_threads)

    return True
