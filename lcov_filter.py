from enum import Enum
import re
import os
import sys


class NoCOVType(Enum):
    NONE = 1
    LCOV = 2
    GCOVR = 3


class NumberRange:
    start = 0
    end = 0


class SourceFilter:

    def __init__(self, source_path):
        source_file = open(source_path)
        source_lines = source_file.readlines()
        source_file.close()

        line_number = 0
        self.__no_cov_list = []
        no_cov_range = NumberRange()
        no_cov_type = NoCOVType.NONE
        for source_line in source_lines:
            line_number += 1
            no_cov_pair_found = False
            if "LCOV_EXCL_START" in source_line:
                if (no_cov_type != NoCOVType.NONE):
                    raise Exception(
                        "LCOV_EXCL_START flag mismatch at line {0}".format(line_number))
                no_cov_range.start = line_number
                no_cov_type = NoCOVType.LCOV
            elif "GCOVR_EXCL_START" in source_line:
                if (no_cov_type != NoCOVType.NONE):
                    raise Exception(
                        "GCOVR_EXCL_START flag mismatch at line {0}".format(line_number))
                no_cov_range.start = line_number
                no_cov_type = NoCOVType.GCOVR
            elif "LCOV_EXCL_STOP" in source_line:
                if no_cov_type != NoCOVType.LCOV:
                    raise Exception(
                        "LCOV_EXCL_STOP flag mismatch at line {0}".format(line_number))
                else:
                    no_cov_pair_found = True
            elif "GCOVR_EXCL_STOP" in source_line:
                if no_cov_type != NoCOVType.GCOVR:
                    raise Exception(
                        "GCOVR_EXCL_STOP/STOP flag mismatch at line {0}".format(line_number))
                else:
                    no_cov_pair_found = True

            if no_cov_pair_found:
                no_cov_range.end = line_number
                self.__no_cov_list.append(no_cov_range)
                no_cov_range = NumberRange()
                no_cov_type = NoCOVType.NONE

    def is_no_cov(self, line_number):
        low = 0
        high = len(self.__no_cov_list) - 1

        while low <= high:

            mid = low + (high - low)//2
            no_cov_range = self.__no_cov_list[mid]
            if (line_number > no_cov_range.start) and (line_number < no_cov_range.end):
                return True
            elif no_cov_range.end <= line_number:
                low = mid + 1
            else:
                high = mid - 1

        return False


if (len(sys.argv) < 2):
    raise Exception("no lcov file input")

lcov_file_path = sys.argv[1]

lcov_dir_name = os.path.dirname(lcov_file_path)

lcov_file_name_list = os.path.splitext(os.path.basename(lcov_file_path))

lcov_file = open(lcov_file_path)

lcov_lines = lcov_file.readlines()

lcov_file.close()

lcov_out_path = os.path.join(
    lcov_dir_name, "{0}_filtered{1}".format(lcov_file_name_list[0], lcov_file_name_list[1]))

lcov_out_file = open(lcov_out_path, "w")

source_filter = None

for line in lcov_lines:
    filter_out = False

    if line.startswith("SF:"):
        source_path = line[3:-1]
        source_filter = SourceFilter(source_path)
    else:
        result = re.search('^(BR)?DA:(\d+),*', line)
        if (result != None):
            line_number_str = result.group(2)
            line_number = int(line_number_str)
            assert source_filter != None
            filter_out = source_filter.is_no_cov(line_number)

    if (not filter_out):
        lcov_out_file.write(line)

lcov_out_file.close()
