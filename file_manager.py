# pylint: disable=missing-function-docstring,missing-module-docstring

import os
import re
import glob
import cyrtranslit
from file_info import FileInfo

def normalize_all_filenames(log):
    files = get_file_list()
    log.info("3. Normalizing all file names")
    for file in files:
        normalize_filename(file, log)


def normalize_filename(file: str, log):
    if not file.endswith('.wav'):
        return
    log.info(f"3.1 Normalizing {file}")
    new_name = replace_known_bad_chars(file)
    os.replace(file, new_name)
    log.info(f"3.2 Replaced. Old file name: {file}, New file name: {new_name}")
    return new_name


def replace_known_bad_chars(file):
    new_name = remove_colons_from_filename(file)
    new_name = remove_cyrillic_letters(file)
    return new_name


def remove_cyrillic_letters(file):
    new_name = re.sub(r'\W+', ' ', cyrtranslit.to_latin(file, "ru"))
    new_name = re.sub(' wav', ".wav", new_name)
    return new_name


def remove_colons_from_filename(file):
    new_name = file.replace("：", "")
    new_name = file.replace(":", "")
    return new_name


def get_file_list():
    return glob.glob("*.wav")


def get_new_file_name(previous_files: list[FileInfo]) -> str:
    current_files = get_file_list()
    for file in previous_files:
        if file.name in current_files:
            current_files.remove(file.name)
    return current_files[0]
