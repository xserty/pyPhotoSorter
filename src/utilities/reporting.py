class Reporting:
    # static variables needed for reporting
    dt_elapsed_time = 0
    total_num_of_files = 0
    total_num_of_sorted_files = 0
    total_num_of_unsorted_files = 0
    total_num_of_deleted_files = 0
    total_num_of_ignored_files = 0
    total_num_of_duplicate_files = 0

    @staticmethod
    def print_stdout_report():
        Reporting.print_todo_list()
        print("")
        print("")
        print("###############################################")
        print("# Total numbers of files processed:    %s" % Reporting.total_num_of_files)
        print("# Total numbers of sorted files:       %s" % Reporting.total_num_of_sorted_files)
        print("# Total numbers of unsorted files:     %s" % Reporting.total_num_of_unsorted_files)
        print("# Total numbers of deleted files:      %s" % Reporting.total_num_of_deleted_files)
        print("# Total numbers of ignored files:      %s" % Reporting.total_num_of_ignored_files)
        print("# Total numbers of duplicate files:    %s" % Reporting.total_num_of_duplicate_files)
        print("###############################################")
        print("")
        print("Elapsed time: %s" % str(Reporting.dt_elapsed_time))
        if Reporting.dt_elapsed_time:
            print("Sorting took: %d days %02dh:%02dmin:%02dsec" % (Reporting.dt_elapsed_time.days, Reporting.dt_elapsed_time.seconds // 3600, Reporting.dt_elapsed_time.seconds // 60 % 60, Reporting.dt_elapsed_time.seconds % 60))

    @staticmethod
    def print_todo_list():
        print("ToDo List:")
        print("-\t Cleanup options.settings module")
        print("")
        print("* Implement various command line options like:")
        print("\t- Option to copy or move media files")
        print("\t- Option to pass .ExifTool_config file location through parameter")
        print("* Implement date priorities (date in filename, date in path, date in CreateDate exif, etc.)")
        print("")
        print("* GUI features")
        print("\t- Progress bar")
        print("\t- Find Duplicates")
        print("\t- Cleanup and let user decide where to store files: options.OPTIONS_PICKLE_FILE")
        print("\t- Cleanup and let user decide where to store files: options.DICTIONARY_PICKLE_FILE")
        print("\t- Cleanup and let user decide where to store files: options.DELETED_ITEMS_PICKLE_FILE")

    @staticmethod
    def reset():
        """ reset all reporting counters """
        Reporting.dt_elapsed_time = 0
        Reporting.total_num_of_files = 0
        Reporting.total_num_of_sorted_files = 0
        Reporting.total_num_of_unsorted_files = 0
        Reporting.total_num_of_deleted_files = 0
        Reporting.total_num_of_ignored_files = 0
        Reporting.total_num_of_duplicate_files = 0
