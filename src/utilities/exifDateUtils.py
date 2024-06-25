import os
import re
import datetime
import struct

import exifread
import exiftool
from exifread.heic import NoParser
from exiftool.exceptions import ExifToolExecuteError

from dateutil import parser
from dateutil.parser import ParserError

from src.options.settings import EXIFTOOL_CONFIG_FILE
from src.utilities.file import fileUtils


# [ToDo] Implement testing for all methods!!

def _get_date_in_filename(ff_name):
    filename = os.path.basename(ff_name)
    regex1 = re.compile(r"(\d{8})")  # regex pattern to capture possible date
    match_array = regex1.findall(filename)
    if not match_array:
        return False
    date = match_array[0]
    year = date[0:4]
    month = date[4:6]
    day = date[6:8]
    print("Possible date from filename:", date)
    print("\t", year, month, day)
    result = year + ':' + month + ':' + day
    return result


def __get_hour_min_sec(time):
    # if time is empty, return zeros
    if not time:
        return '00', '00', '00'
    h = time.split(':')[0]
    if len(h) < 2:
        h = '0' + h
    m = time.split(':')[1]
    if len(m) < 2:
        m = '0' + m
    try:
        s = time.split(':')[2]
    except IndexError as er:
        # print('No seconds present in date/time field...')
        s = '00'
    if len(s) < 2:
        s = '0' + s
    return h, m, s


def __is_alphanumeric_date(date_time):
    """
    Returns True if date is of format: 'Mon dd, YYYY' e.g.: jun 11, 2014 6:33:30
    Note: this method just checks the date format, it does not check the time portion
    :param date_time:
    :return: boolean
    """
    result = False
    if date_time.count(':') == 2 \
            and date_time.count(',') == 1 \
            and not date_time[0].isnumeric() \
            and not date_time[1].isnumeric() \
            and not date_time[2].isnumeric():
        result = True
    return result


# [ToDo] Implement testing for at least this method!!
def __format_date(date_time_str):
    result = ''
    # first remove any trailing spaces
    dt = str(date_time_str).strip()
    # remove any timezone if present
    if '+' in dt:
        # print("Ignoring timezone in date")
        dt = dt.split('+')[0]
    elif '-' in dt:
        # print("Ignoring timezone in date")
        dt = dt.split('-')[0]
    # 2006.09.17  15:32:15
    # ----------^^
    # handle cases where datetime is like '    :  :     :  :  ' or empty ''
    # Actually, the line above has been dealt with in .ExifTool_config!
    if len(dt.replace(' ', '')) <= 4:
        # not a valid date
        # return an empty string
        pass
    elif 14 <= len(dt) <= 18:
        # fix this format: '2010:06:03 08:03:2' (len between 14 and 18)
        date = dt.split(" ")[0]
        time = ''
        try:
            time = dt.split(" ")[1]
        except IndexError as er:
            print("# No time found in date: %s" % dt)
        # split the date
        dd, mm, yy = get_year_month_day(date)
        # split the time
        hh, mm, ss = __get_hour_min_sec(time)
        result = yy + ':' + mm + ':' + dd + ' ' + hh + ':' + mm + ':' + ss
    elif len(dt) == 22 and dt[19] == '.':
        # [ToDo] Insert proper checks to see if there are milliseconds in date-time format
        # we might have this type of date-time format: '2008:11:29 14:47:12.06'
        # lets 'just' truncate any milliseconds later the date-time:
        # '2008:11:29 14:47:12.06' becomes '2008:11:29 14:47:12'
        dt = dt[0:19]
        result = get_correct_date_format(dt)
    elif len(dt) >= 23:
        # handle this date format: '2010 :09 :20 16 :20 :51'
        if dt[4] == ' ' and dt[8] == ' ' and dt[12] == ' ' and dt[15] == ' ' and dt[19] == ' ':
            result = str(dt[:4] + dt[5:8] + dt[9:13] + dt[13:15] + dt[16:19] + dt[20:23])
    elif 20 <= len(dt) <= 21:
        # length = 20
        # 2006.09.17  15:32:15	(valid, but with double spaces)
        # 'jun 11, 2014 6:33:30'	(valid)
        # 'jun 11, 2014 16:33:30'	(valid)
        # '2010:9:22:1:57     2'    (invalid time - maybe valid date)
        # '2013:10:21 13:19:01Z'    (valid)
        #  -------------------^     Time zone?

        # catch these invalid dates: '2010:9:22:1:57     2'
        # catch these invalid dates: '2007:1227:27 13:27:3'
        if __is_alphanumeric_date(dt):
            # Most likely it's a date in this format: 'jun 11, 2014 6:33:30'
            # [ToDo] Remove the use of external parser!
            result = parser.parse(dt)
            print("\t\tParsed this: %s" % result)
            result = get_correct_date_format(result.strftime("%Y:%d/%m %H:%M:%S"))
            print("\t\tGot this --> %s" % result)
        elif '  ' in dt:
            # lets check for this date: 2006.09.17  15:32:15	(valid, but with double spaces for some reason!)
            #                           ----------^^
            # remove double spaces
            dt = dt.replace('  ', ' ')
            try:
                result = get_correct_date_format(dt)
            except ParserError:
                # if a ParserError was raised, then can be something like this: '2010:9:22:1:57     2'
                yy, mm, dd = get_year_month_day(dt)
                result = yy + ':' + mm + ':' + dd + ' 00:00:00'
                if len(result) != 19:
                    # If getYearMonthDay went wrong, return an empty date-time
                    result = ''
        elif '?' in dt:
            # date format: '????????????????????'
            print("ERROR: Could not find a matching pattern for this date: %s " % dt)
            # If getYearMonthDay went wrong, return an empty date-time
            result = ''
        elif ' ' in dt and (len(dt.split(' ')[1]) > 8):
            # [ToDo] Insert checks to see if there is a time-zone that can be truncated
            # we might have these kinda dates:
            # '2013:10:21 13:19:01Z'    (valid)
            #  -------------------^     Time zone?
            # lets 'just' truncate any time zone later the date-time:
            # '2013:10:21 13:19:01Z' becomes '2013:10:21 13:19:01'
            dt = dt[0:19]
            result = get_correct_date_format(dt)
        else:
            y, m, d = ('',) * 3
            if len(dt.split(':')[0]) == len(dt.split(':')[1]):
                y = dt.split(':')[0]
                m = dt.split(':')[1][0:2]
                d = dt.split(':')[1][2:4]
                if d not in dt.split(':')[2].split(' ')[0]:
                    print("WARNING: Format may be wrong... %s " % dt)
                    print("May not be expected date format 'YYYY:mmdd:dd': %s" % dt)
                result = y + ':' + m + ':' + d + ' 00:00:00'
                if len(result) != 19:
                    print("ERROR: Could not find a matching pattern for this date: %s " % dt)
                    # If getYearMonthDay went wrong, return an empty date-time
                    result = ''
            else:
                # [ToDo] Ambiguous dates... never came across it yet...
                # could be something like this: '2007:127:27 13:26:3'? where year = 2007, month = 1, day = 27?
                # could be something like this: '2007:127:27 13:26:3'? where year = 2007, month = 12, day = 7?
                print("ERROR: Ambiguous date. Could not find a matching pattern for this date: %s " % dt)
                # If getYearMonthDay went wrong, return an empty date-time
                result = ''
    elif len(dt) == 10:
        # Maybe we only got a date, no time
        dt = dt + ' 00:00:00'
        result = get_correct_date_format(dt)
    elif len(dt) == 19:
        # we should have a correct date here...
        # except for this: 'jun 1, 2014 6:33:30' 	(valid)
        # [ToDo] parse 'jun 1, 2014 6:33:30' (valid date)
        result = get_correct_date_format(dt)
    else:
        # WARNING: IF WE GET TO THIS POINT, WE MISSED SOMETHING!!
        # [ToDo] not sure what we get here at this stage!!!
        # got this: "b'\\xa4\\n'"
        # also got this: '29 16:13:49'
        print("WARNING: Unable to read this date-time: '%s'; length: %s" % (str(dt), len(dt)))
    if result:
        # print(" ==> Formatted date: %s" % result)
        pass
    return result


def get_correct_date_format(date_time):
    if len(date_time) != 19:
        raise ParserError('Expected date-time length 19, get %s' % len(date_time))
    new_date_str = []
    result = ''
    i = 1
    for x in date_time:
        # fix this date type: '2011: 2: 5  0:13:27'
        # --------------------------^--^--^
        if (i == 6 or i == 9 or i == 12) and x == ' ':
            new_date_str += '0'
        elif (i == 5 or i == 8 or i == 14 or i == 17) and ':' not in x:
            # fix this date type: '2009/07/28 10:37.37' or any combination of separators
            # fix this date type: '2009-07-28 10:37.37' or any combination of separators
            # -------------------------^--^-----^--^
            new_date_str += ':'
        elif x == ':' and i == 11:
            # fix this date type: '2009:07:28:10:37:37'
            # -------------------------------^
            new_date_str += ' '
        else:
            new_date_str += x

        result = ''.join(str(x) for x in new_date_str)
        i += 1
    return result


def get_year_month_day(date):
    y, m, d = ("",) * 3
    y = date.split(':')[0]
    if len(y) < 4:
        print("Year found is not valid: %s " % y)
    m = date.split(':')[1]
    if len(m) < 2:
        m = '0' + m
    d = date.split(':')[2]
    if len(d) < 2:
        d = '0' + d
    return d, m, y


def __get_oldest_exif_date(exif_array):
    date_array = []
    for prop in exif_array:
        tag_name = prop[0]
        if "date" in tag_name.lower() and 'DateStampMode'.lower() not in tag_name.lower():
            date_time = prop[1]
            # print(f"=== Found a date tag: {tag_name}: {date_time}")
            # Handle weird cases like '2011: 2: 5  0:13:27' or '2009:07:28:10:37:37' or ''
            new_date = __format_date(date_time)
            if len(new_date) == 0:
                print("Empty date field.")
                continue
            # print("t\Date:", new_date)
            if len(new_date) > 10:
                # [ToDo] catching this date here: 'jun 11, 2014 6:33:30' as not caught in formatDate() method
                # test variable contains time
                new_date = new_date.split(' ')[0]
            date_array.append(new_date)
    if not date_array:
        print("WARNING: No dates found in exif tags...")
        # print("List of exif data:")
        # for exif in exif_array:
        #     if exif[0] == 'JPEGThumbnail':
        #         continue
        #     print(f"\t{exif[0]}: {exif[1]}")
        return ""

    # sort list of dates (in place, sort() returns None)
    date_array.sort()
    # date_array.sort(key=lambda x: list(x.values())[0])
    # key, date = date_array[0].popitem()
    # print("Oldest Exif date: %s" % date_array[0])
    return date_array[0]


def __split_all(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


def _get_date_in_file_path(ff_name):
    path = os.path.split(ff_name)[0]
    parts = __split_all(path)
    # print("\tParts:", parts)
    i = 0
    for part in parts:
        # Following is used for debugging only
        # if 'TestImages' in part:
        #     i += 1
        #     continue

        # skip if any part of the three part path is not numeric or not None
        try:
            if not part.isnumeric() or not parts[i + 1].isnumeric() or not parts[i + 2].isnumeric():
                i += 1
                continue
        except IndexError:
            continue

        # print("\t\t===== Numeric path with possible date found:", part, parts[i + 1], parts[i + 2], "=====")
        # [1800...2024] / [1...12] / [1...31]
        # if ((1800 <= int(str(part)) <= datetime.date.today().year) and (1 <= int(str(parts[i + 1]) <= 12)) and (1 <= int(str(parts[i + 2]) <= 31))):
        if (1800 <= int(part) <= datetime.date.today().year) and (1 <= int(parts[i + 1]) <= 12) and (
                1 <= int(parts[i + 2]) <= 31):
            # we (most likely) found a date in the path
            # if month only contains one digit, prepend digit '0'
            if len(parts[i + 1]) == 1:
                month = '0' + parts[i + 1]
            else:
                month = parts[i + 1]
            # if day only contains one digit, prepend digit '0'
            if len(parts[i + 2]) == 1:
                day = '0' + parts[i + 2]
            else:
                day = parts[i + 2]

            result = part + ':' + month + ':' + day
            print(result)
            return result
        i += 1
    return None


def _get_tags_with_exif_tool(ff_name):
    """
    Uses ExifTool to get exif tags from image file
    :param ff_name: image file
    :return: Array of exif key-value tuples
    """
    # Create an empty array
    __exif_result_array = []
    tags = []
    exiftool_path = fileUtils.find_prog("exiftool").decode("utf-8")
    os.environ['EXIFTOOL_PATH'] = exiftool_path
    # Open image to collect EXIF data
    # [ToDo] load config file not working... picking up '0000:00:00' dates. Maybe incompatible versions?
    exiftool.ExifTool.config_file = EXIFTOOL_CONFIG_FILE
    # with exiftool.ExifToolHelper(config_file=main.EXIFTOOL_CONFIG_FILE) as ex:
    #     print("Using: %s" % exiftool.ExifTool.config_file)
    with exiftool.ExifToolHelper() as ex:
        try:
            tags = ex.get_metadata(ff_name)
        except UnicodeDecodeError as er:
            print("UnicodeDecodeError: %s" % er.reason)
        except ExifToolExecuteError as er:
            print("ExifToolExecuteError: %s" % er)

    if not tags:
        print(f"################ NO TAGS FOUND: ####################")
        # [ToDo] Try to find alternative way to read exif data...
        return __exif_result_array

    # Compile array from tags dict
    # for i in tags[0]:
    for (k, v) in tags[0].items():
        try:
            if isinstance(v, str):
                # [ToDo] We got this '0000:00:00' date even though should be excluded from the .ExifTool_config file
                if "0000:00:00" in v:
                    print("WARNING: Skipping tag (%s: %s)" % (k, v))
                else:
                    tag_compile = k, str(v)
                    __exif_result_array.append(tag_compile)
        except TypeError as er:
            print("Error parsing tag %s: %s" % (k, v))
            print(str(er))

    return __exif_result_array


def _get_tags_with_exifread(ff_name):
    """
    Uses exifread to get exif tags from image file
    :param ff_name: image file
    :return: Array of exif key-value tuples
    """
    # Create an empty array
    __exif_result_array = []
    # Open image to collect EXIF data
    with open(ff_name, 'rb') as f:
        tags = []
        try:
            # https://pypi.org/project/ExifRead/
            # Supported formats: TIFF, JPEG, PNG, Webp, HEIC
            # For ExifTool check this:0https://stackoverflow.com/questions/77038678/how-to-extract-metadata-from-heic-image-files-on-windows-11-with-python
            tags = exifread.process_file(f)
        except (struct.error, IndexError, NoParser) as err:
            print(f"ERROR: Unable to process this file. Unexpected {err=}, {type(err)=}")
        except KeyError as err:
            # [ToDo] to be implemented: Big Endian exif data loading
            #  we get this error when the exif data is saved as big endian
            print(f"ERROR: Unable to process this file. Unexpected {err=}, {type(err)=}")
            print("NOTE: File might be in Big Endian format")
            print("ERROR: Unable to process this file. (KeyError. Exception caught: '%s')" % err)

        if not tags:
            # no tags found with exifread
            print("####### NO TAGS FOUND")
            # [ToDo] Try to find alternative way to read exif data: use ExifTool!
            #           If ExifTool does not find tags, there are none.
            return __exif_result_array

        # [ToDo] can this loop be removed/avoided? (maybe subsequent code needs to be adjusted)
        # Compile array from tags dict
        for i in tags:
            tag = tags[i]
            try:
                # print(tag)
                tag_compile = i, str(tag)
                __exif_result_array.append(tag_compile)
            except TypeError as er:
                print("Error parsing tag %s: %s" % (i, str(er)))
    return __exif_result_array


def get_all_possible_dates(ff_name, ignore_date_in_file_path=False):
    result = []

    if not ignore_date_in_file_path:
        # check if path contains a date
        date = _get_date_in_file_path(ff_name)
        if date:
            # print("getDateInFilePath: %s" % date)
            result.append(date)
    else:
        print("WARNING: Ignoring dates in file path (e.g.: /1999/08/27/)")

    # check if filename contains a date
    date = _get_date_in_filename(ff_name)
    if date:
        print("getDateInFilename: %s" % date)
        result.append(date)
    exif_array = _get_tags_with_exif_tool(ff_name)
    exif_array_2 = _get_tags_with_exifread(ff_name)
    if len(exif_array) < len(exif_array_2):
        print("======= WARNING: len(exif_array) = %s, len(exif_array_2) = %s" % (len(exif_array), len(exif_array_2)))
        print("=======          Exifread contains more tags")
    # print('exifArray:')
    # print(exif_array)
    # now we have exif_array full of date tags
    date = __get_oldest_exif_date(exif_array)
    if date:
        result.append(date)
    # sort the list so that the oldest date is first
    result.sort()
    print('')
    print("List of dates considering: %s" % result)
    return result
