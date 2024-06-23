import os
import pickle

from utilities.file import fileUtils
from utilities.reporting import Reporting
from options import options
# from settings import DICTIONARY_PICKLE_FILE


class MediaObject:
    def __init__(self, ps_key='', full_source_filename='', file_size='', hash_val='', oldest_date='',
                 destination_dir=''):
        self.ps_key = ps_key
        self.full_source_filename = full_source_filename
        self.file_size = file_size
        self.hash_val = hash_val
        self.oldest_date = oldest_date
        self.destination_dir = destination_dir
        self.full_dest_filename = os.path.join(destination_dir, os.path.basename(full_source_filename))
        self.destination_dir = destination_dir

    def __str__(self):
        # print("MediaObject: __str__")
        return "[{}, {}, {}, {}, {}, {}]".format(self.ps_key, self.full_source_filename, self.hash_val, self.file_size,
                                                 self.oldest_date, self.full_dest_filename)

    def __repr__(self):
        # print("MediaObject: __repr__")
        result = "[{}, {}, {}, {}, {}]".format(self.full_source_filename, self.hash_val, self.file_size,
                                               self.oldest_date, self.full_dest_filename)
        # result = "[{}, {}, {}, {}, {}, {}]".format(self.ps_key, self.full_source_filename, self.hash_val,
        #                                            self.file_size, self.oldest_date, self.full_dest_filename)
        # print("Result: %s " % result)
        return result

    def __eq__(self, other):
        """
        Two MediaObjects are equal if they have the same MD5 value, are the same size and have the same oldest date
        :param other: Other MediaObject instance to compare
        :return: True if they are the same, False otherwise
        """
        if other:
            # return self.hash_val == other.hash_val and self.file_size == other.file_size
            return self.hash_val == other.hash_val and self.file_size == other.file_size and self.oldest_date == other.oldest_date
        raise TypeError("Can't compare these types")

    def __ge__(self, other):
        return self.oldest_date >= other.oldest_date

    def __gt__(self, other):
        return self.oldest_date > other.oldest_date

    def __lt__(self, other):
        return self.oldest_date < other.oldest_date

    def __le__(self, other):
        return self.oldest_date <= other.oldest_date


class MediaDictionary(dict):
    def __init__(self, *arg, **kw):
        super(MediaDictionary, self).__init__(*arg, **kw)
        self.is_cleanup_needed = False
        self.deepModeHash = True
        self.sorted_media_dir = ''
        self.unsorted_media_dir = ''

    def __getitem__(self, key):
        # print("__getitem__")
        media_ojb = dict.get(self, key)
        return media_ojb

    def __setitem__(self, key, value):
        # print("__setitem__")
        if isinstance(value, MediaObject):
            dict.__setitem__(self, key, value)
        else:
            print("Object type not recognised: ('%s': '%s')" % (key, value))
            raise ValueError("Value type is not a MediaObject")

    def __str__(self):
        print("")
        print("psMediaDictionary:")
        print("size: %s " % len(self))

        count = 1
        result = ''
        value: MediaObject
        # for key, value in self.items():
        for value in self.values():
            result += str(count) + ': '
            result += repr(value)
            result += '\n'
            count += 1
        return result

    def _insert(self, new_media_object=None, override=False):
        key = new_media_object.ps_key
        print("Key = %s " % key)
        # Get the media_object corresponding to key
        existing_media_object: MediaObject = self._get(key)
        if existing_media_object is None or override:
            # there is no media_object instance in the bucket
            # insert/update media object
            # self.hashtable[key] = new_media_object
            self.__setitem__(key, new_media_object)

    def _get(self, ps_key=''):
        # Get the bucket corresponding to key
        media_obj = None
        try:
            # media_obj = self.hashtable[hashed_key]
            media_obj = self.__getitem__(ps_key)
            print("Loading saved media object: %s" % media_obj)
            if media_obj and not os.path.exists(media_obj.full_dest_filename):
                print("Found dictionary entry, but not the destination file")
                print("MediaObject: %s " % media_obj)
                print("WARNING: Forcing dictionary cleanup!")
                self.is_cleanup_needed = True
                media_obj = None
        except KeyError:
            pass
        return media_obj

    def _get_media_hash_key(self, full_media_filename):
        file_stats = os.stat(full_media_filename)
        size = file_stats.st_size
        # hash can be calculated in a deep or shallow mode
        #   deep: file is opened and read fully to calculate MD5 hash
        #   shallow: file is not opened and hash is based on filename and size
        if self.deepModeHash:
            # Open,close, read file and calculate MD5 on its contents
            md5 = fileUtils.generate_file_md5(full_media_filename)
            # return "{},{}".format(md5, size)
            return md5, size
        else:
            # shallow mode enabled
            # compare only by file name and size
            filename = os.path.basename(full_media_filename)
            # return "{},{}".format(filename, size)
            return filename, size

    def add(self, full_filename='', oldest_date_time='', destination_dir='', regenerate_media_dictionary=False):
        md5, size = self._get_media_hash_key(full_filename)
        ps_key = "{},{}".format(md5, size)
        file_size = str(size)
        new_media_obj = MediaObject(ps_key=ps_key, full_source_filename=full_filename, file_size=file_size,
                                    hash_val=md5, oldest_date=oldest_date_time, destination_dir=destination_dir)

        existing_media_obj = self._get(ps_key=ps_key)

        if not existing_media_obj:
            self._insert(new_media_obj, override=False)
            if not regenerate_media_dictionary:
                fileUtils.copy_file(full_filename, destination_dir)
            Reporting.total_num_of_sorted_files += 1
            return

        # print("Found existing media obj %s" % existing_media_obj)
        print("New media obj: %s" % new_media_obj)

        if existing_media_obj == new_media_obj:
            # update the counters
            Reporting.total_num_of_duplicate_files += 1
            print("Duplicate.")
            # print("INFO: Existing media has same md5, size and oldest date (%s)" % existing_media_obj)
            # print("INFO: They must have different file names or file paths")
        elif existing_media_obj > new_media_obj:
            # Sorting media
            Reporting.total_num_of_sorted_files += 1
            print(existing_media_obj.oldest_date + ">=" + oldest_date_time)
            print("SORT NEEDED: Sorting dates of the two files differ... Need to update file location")
            self._insert(new_media_obj, override=True)
            if not regenerate_media_dictionary:
                # Copy photo in correct sorted dir
                fileUtils.copy_file(full_filename, destination_dir)
                # Delete old media in the wrong sorted dir
                fileUtils.delete_file(existing_media_obj.full_dest_filename)
        else:
            # Duplicate media with more recent oldest date-time
            Reporting.total_num_of_duplicate_files += 1
            # existing_media_obj < new_media_obj:
            print("Nothing to sort: duplicate with more recent oldest date-time")

        if existing_media_obj.full_source_filename.startswith(self.unsorted_media_dir):
            print("WARNING: Existing media is in unsorted directory. Inserting new found media in sorted directory and removing old unsorted media.")
            # Copy photo in correct sorted dir
            fileUtils.copy_file(full_filename, destination_dir)
            # Delete old media in the wrong sorted dir
            fileUtils.delete_file(existing_media_obj.full_dest_filename)

    def remove_media_object_by_filename(self, full_filename):
        md5, size = self._get_media_hash_key(full_filename)
        ps_key = "{},{}".format(md5, size)
        # check if there is an existing dictionary entry
        existing_media_obj = self._get(ps_key=ps_key)
        if existing_media_obj:
            print("Found existing media obj %s" % existing_media_obj)
            # remove existing media file
            fileUtils.delete_file(existing_media_obj.full_dest_filename)
            old_media_obj = self.pop(ps_key)
            print("Removed following from dictionary: %s" % old_media_obj)
            Reporting.total_num_of_deleted_files += 1
        else:
            print("Nothing to remove. Given filename = %s, ps_key = %s" % (full_filename, ps_key))

    def get_media_object_by_filename(self, full_filename):
        md5, size = self._get_media_hash_key(full_filename)
        ps_key = "{},{}".format(md5, size)
        # check if there is an existing dictionary entry
        return self._get(ps_key=ps_key)

    def save_dictionary_to_pickle_file(self):
        with open(options.DICTIONARY_PICKLE_FILE, 'wb') as f:
            pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)
        print("Saved dictionary. Size: %s " % len(self))

    def load_dictionary_from_pickle_file(self):

        # create a backup of the dictionary file first
        fileUtils.backup_file(full_filename=options.DICTIONARY_PICKLE_FILE)

        print("Attempting to load dictionary file %s" % options.DICTIONARY_PICKLE_FILE)
        is_existing_dict_file_from_different_sort_dir = False
        sorted_media_dir_loaded_from_dictionary = ''
        try:
            with open(options.DICTIONARY_PICKLE_FILE, 'rb') as f:
                content = pickle.load(f)

                # check if dictionary belongs to some other sorted media directory
                if self.sorted_media_dir != content.sorted_media_dir:
                    is_existing_dict_file_from_different_sort_dir = True
                    sorted_media_dir_loaded_from_dictionary = content.sorted_media_dir

                    # set the dictionary items to this MediaDictionary instance
                for key, value in content.items():
                    self.__setitem__(key, value)
                # set the rest of the properties
                print('deepModeHash: %s' % content.deepModeHash)
                self.deepModeHash = content.deepModeHash
                # print('sorted_media_dir: %s' % content.sorted_media_dir)
        except FileNotFoundError as err:
            print("No saved dictionary found: %s" % err.strerror)
            return

        print("Total number of dictionary entries: %s" % len(self))

        if is_existing_dict_file_from_different_sort_dir:
            print("WARNING: Loaded dictionary file references a different sorted directory (%s)" % sorted_media_dir_loaded_from_dictionary)
            print("Clearing dictionary items...")
            # clear the dictionary entries (all the media objects)
            self.clear()
            self.is_cleanup_needed = False

    def cleanup(self):
        # [ToDo] check this cleanup if it's doing a good job

        print("")
        print("Cleaning up media dictionary...")
        print("Current MediaDictionary size: %s " % len(self))

        # create a new MediaObject dictionary to backup deleted media entries
        mediaObj: MediaObject
        media_dict_items_to_be_removed = MediaDictionary()
        media_dict_items_to_be_removed.sorted_media_dir = self.sorted_media_dir
        media_dict_items_to_be_removed.unsorted_media_dir = self.unsorted_media_dir
        media_dict_items_to_be_removed.deepModeHash = self.deepModeHash

        count = 0
        # loop to find all keys with no file associated and put in 'media_dict_items_to_be_removed' list
        for key, mediaObj in self.items():
            if not os.path.exists(self.get(key).full_dest_filename):
                # [ToDo] Is the fact that the file exists enough? Should we check the hash as well?
                count += 1
                print("%d: File not found: %s" % (count, mediaObj.full_dest_filename))
                media_dict_items_to_be_removed._insert(new_media_object=mediaObj)

        # go through the list and remove keys with no existing file associated from the MediaDictionary
        removed = 0
        for key, value in media_dict_items_to_be_removed.items():
            removed += 1
            # add this item to be deleted to the media_dict_items_to_be_removed dictionary for backup purposes
            print("%d: Removing: %s" % (removed, self.get(key).full_dest_filename))
            self.pop(key)

        if removed > 0:
            print("Cleanup done! Total number of entries removed from dictionary: %d" % removed)
            print("New dictionary size: %s " % len(self))
            # save the list of items that have been deleted

            fileUtils.backup_file(options.DELETED_ITEMS_PICKLE_FILE)
            with open(options.DELETED_ITEMS_PICKLE_FILE, 'wb') as f:
                pickle.dump(media_dict_items_to_be_removed, f, protocol=pickle.HIGHEST_PROTOCOL)
            print("Deleted items list has been saved in %s" % options.DELETED_ITEMS_PICKLE_FILE)
            print("Deleted items list size: %s " % len(media_dict_items_to_be_removed))
        else:
            print("MediaDictionary was clean. No entries removed")
