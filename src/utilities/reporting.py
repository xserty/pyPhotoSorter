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
        print(f"""
        ##################################################
        # Total number of files processed:    {Reporting.total_num_of_files:>10}
        # Total number of sorted files:       {Reporting.total_num_of_sorted_files:>10}
        # Total number of unsorted files:     {Reporting.total_num_of_unsorted_files:>10}
        # Total number of deleted files:      {Reporting.total_num_of_deleted_files:>10}
        # Total number of ignored files:      {Reporting.total_num_of_ignored_files:>10}
        # Total number of duplicate files:    {Reporting.total_num_of_duplicate_files:>10}
        ##################################################
        """)
        print("Elapsed time: %s" % str(Reporting.dt_elapsed_time))
        if Reporting.dt_elapsed_time:
            print("Sorting took: %d days %02dh:%02dmin:%02dsec" % (Reporting.dt_elapsed_time.days, Reporting.dt_elapsed_time.seconds // 3600, Reporting.dt_elapsed_time.seconds // 60 % 60, Reporting.dt_elapsed_time.seconds % 60))

    @staticmethod
    def print_todo_list():
        print("""
        ToDo List:
        --------------------------------------------------
        - Cleanup options.settings module

        * Implement various command line options:
            - Option to copy or move media files
            - Option to pass .ExifTool_config file location via parameter

        * Implement date priorities:
            - Date in filename
            - Date in path
            - EXIF CreateDate / DateTimeOriginal
            - Other metadata fallbacks

        * GUI features:
            - Progress bar
            - "Find Duplicates" feature
            - Let user choose where to store:
                - options.OPTIONS_PICKLE_FILE
                - options.DICTIONARY_PICKLE_FILE
                - options.DELETED_ITEMS_PICKLE_FILE
        --------------------------------------------------
        """)
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
