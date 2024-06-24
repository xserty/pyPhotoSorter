import re
import sys

file_extension = "~5~"  # can can also be like '~12~'
regex = re.compile(r"~\d*~")

match file_extension:
    case "~*~" | '*~*':
        print("String match!")  # Not matching here
    # case regex.match(ext):  # TypeError: called match pattern must be a class
    #     print("Regex match!")
    case _:
        if regex.match(file_extension):
            print("Regex matched!")
        else:
            print("Regex not match!")
