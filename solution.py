import json
from typing import List
from collections import defaultdict

FBS_TO_FREQ = {36: 164, 18: 84, 9: 48, 1: 1}

class Solution:
    def __init__(self, data_file_path: str, protocol_json_path: str):
        self.data_file_path = data_file_path
        self.protocol_json_path = protocol_json_path

    def parse_data_line(self, str_data_line):
        list_data_line = str_data_line.split(",")
        self.protocol_id = int(list_data_line[2], 16)
        self.massage_size = int(list_data_line[3].split()[0])
        self.massage_data = "".join(list_data_line[4:])

    # Question 1: What is the version name used in the communication session?
    def q1(self) -> str:
        return self.get_version()

    # Question 2: Which protocols have wrong messages frequency in the session compared to their expected frequency based on FPS?
    def q2(self) -> List[str]:
        massage_freq = self.count_massage_freq()
        version = self.get_version()
        return self.equal_expected_and_current_freq(version, massage_freq)

    # Question 3: Which protocols are listed as relevant for the version but are missing in the data file?
    def q3(self) -> List[str]:
        version = self.get_version()
        relevant_protocol_for_version, base = self.get_relevant_protocol_for_version_and_base(version)
        relevant_protocol_for_version = convert_to_int(relevant_protocol_for_version, base)
        protocol_in_data_file = self.get_protocol_in_data_file()
        return [protocol for protocol in relevant_protocol_for_version if protocol not in protocol_in_data_file]


    # Question 4: Which protocols appear in the data file but are not listed as relevant for the version?
    def q4(self) -> List[str]:
        version = self.get_version()
        relevant_protocol_for_version, base = self.get_relevant_protocol_for_version_and_base(version)
        protocol_in_data_file = self.get_protocol_in_data_file()
        relevant_protocol_for_version = convert_to_int(relevant_protocol_for_version, base)
        return [protocol for protocol in protocol_in_data_file if protocol not in relevant_protocol_for_version]

    # Question 5: Which protocols have at least one message in the session with mismatch between the expected size integer and the actual message content size?
    def q5(self) -> List[str]:
        result= set()
        with open(self.data_file_path, 'r') as f:
            for line in f:
                self.parse_data_line(line)
                data_len = len(bytes.fromhex(self.massage_data))
                if data_len != self.massage_size:
                    result.add(str(self.protocol_id))
        return list(result)

    # Question 6: Which protocols are marked as non dynamic_size in protocol.json, but appear with inconsistent expected message sizes Integer in the data file?
    def q6(self) -> List[str]:
        version = self.get_version()
        protocol_to_expected_size= {}
        dinamic_size_for_protocol = self.dinamic_size_for_protocol(version)
        result = set()
        with open(self.data_file_path, 'r') as f:
            for line in f:
                self.parse_data_line(line)
                if self.protocol_id in protocol_to_expected_size and protocol_to_expected_size[self.protocol_id] != self.massage_size:
                    if not dinamic_size_for_protocol[self.protocol_id]:
                        result.add(self.protocol_id)
                protocol_to_expected_size[hex(self.protocol_id)] = self.massage_size
        return list(result)

    def count_massage_freq(self):
        massage_freq = defaultdict(int)
        with open(self.data_file_path, 'r') as f:
            for line in f:
                self.parse_data_line(line)
                massage_freq[self.protocol_id] += 1
        return massage_freq

    def get_version(self):
        with open (self.data_file_path, 'r') as f:
            first_massage = f.readline()
        self.parse_data_line(first_massage)
        byte_array = bytes.fromhex(self.massage_data)
        ascii_version = byte_array.decode("ascii")
        return ascii_version

    def equal_expected_and_current_freq(self, version, massage_freq):
        worng_freq = []
        with open(self.protocol_json_path, 'r') as f:
            data = json.load(f)
        protocols_in_version, base = self.get_relevant_protocol_for_version_and_base(version)
        protocols_info = data['protocols']
        for protocol in protocols_in_version:
            if base == 10:
                protocol = hex(int(protocol))
            fps_for_protocol = protocols_info[protocol]['fps']
            freq_for_protocol = FBS_TO_FREQ[fps_for_protocol]
            if massage_freq.get(int(protocol, 16)) != freq_for_protocol:
                worng_freq.append(protocol)
        return worng_freq

    def get_relevant_protocol_for_version_and_base(self, version):
        with open(self.protocol_json_path, 'r') as f:
            data = json.load(f)
        base = 10 if data["protocols_by_version"][version]['id_type'] == 'dec' else 16
        return data["protocols_by_version"][version]['protocols'], base

    def get_protocol_in_data_file(self):
        protocols_in_data = set()
        with open(self.data_file_path, 'r') as f:
            for line in f:
                self.parse_data_line(line)
                protocols_in_data.add(self.protocol_id)
        return list(protocols_in_data)

    def dinamic_size_for_protocol(self, version):
        dinamic_size_for_protocol = {}
        with open(self.protocol_json_path, 'r') as f:
            data = json.load(f)
        protocols_in_version, base = self.get_relevant_protocol_for_version_and_base(version)
        protocols_info = data['protocols']
        for protocol in protocols_in_version:
            if base == 10:
                protocol = hex(int(protocol))
            dynamic_size = protocols_info[protocol]['dynamic_size']
            dinamic_size_for_protocol[protocol] = dynamic_size
        return dinamic_size_for_protocol



def convert_to_int(numbers, base):
    """
    Converts a list of number strings in the specified base to a list of integers.

    :param numbers: List of strings representing numbers.
    :param base: The base in which the numbers are represented (2 <= base <= 36).
    :return: List of integers converted from the input numbers.
    """
    if base < 2 or base > 36:
        raise ValueError("Base must be in the range 2 to 36")

    # Convert each number in the list to an integer with the specified base
    converted_numbers = []
    for number in numbers:
        try:
            converted_numbers.append(int(number, base))
        except ValueError:
            print(f"Warning: '{number}' is not a valid representation for base {base}. It will be skipped.")

    return converted_numbers





