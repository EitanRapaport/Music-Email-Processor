# pylint: disable=missing-function-docstring,missing-module-docstring

import re
import os
from time import time
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.effects import compress_dynamic_range
from google_classifier import Classifier
from classification_results import ClassificationResults
from file_manager import get_file_list

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
SILENCE_AT_BEGINNING_AND_END_MS = 3000


def shorten_file(file, end_timestamp, log):
    audio = AudioSegment.from_file(file, format='wav')
    current_length = audio.duration_seconds
    timestamp_in_seconds = end_timestamp * 1000
    added_ten_seconds = timestamp_in_seconds + 10 * 1000
    new_audio_segment = audio[:added_ten_seconds]
    new_length = new_audio_segment.duration_seconds
    log.info(f"Shortened {file} from {current_length} to {new_length}")
    new_audio_segment.export(file, format='wav')


def compress_file(file, log):
    if not file.endswith('.wav'):
        pass
    else:
        start = time()
        log.info(f'4.1 Compressing: -- {file}')
        new_file_name = generate_new_file_name(file, "_C")
        compress_audio_file(file, new_file_name)
        os.remove(file)
        elapsed = measure_time(start)
        log.info(f"4.2 Compressed -- {new_file_name} took {elapsed} seconds")
        return new_file_name

def compress_audio_file(file, new_file_name):
    raw_sound = AudioSegment.from_file(file)
    compressed_sound = compress_dynamic_range(raw_sound, -20, 6)
    compressed_sound.export(new_file_name , format='wav')


def normalize_audio_file(file, log):
    if not file.endswith('.wav'):
        pass
    else:
        log.info(f"5.1 Normalizing -- {file}")
        start = time()
        new_file_name = generate_new_file_name(file, "N")
        normalize_audio(file, new_file_name)
        os.remove(file)
        elapsed = measure_time(start)
        log.info(f"5.2 Normalizing -- {new_file_name} took {elapsed} seconds")
        return new_file_name


def generate_new_file_name(file, prefix):
    """
    Generate a new file name by adding a prefix to the file name
    N stands for normalized
    S stands for silence
    C stands for compressed
    """
    return re.sub(r"\.wav", f"{prefix}.wav", file)

def normalize_audio(file, new_file_name):
    raw_sound = AudioSegment.from_file(file)
    normalized_file = normalize(raw_sound, 0.1)
    normalized_file.export(new_file_name, format='wav')


def add_silence_to_file(file, log):
    log.info(f"6.1 Adding silence to file -- {file}")
    start = time()
    new_file = generate_new_file_name(file, "S")
    add_silence_to_audio(file, new_file)
    os.remove(file)
    elapsed = measure_time(start)
    log.info(f"6.2 Added silence to -- {new_file} took {elapsed} seconds")
    return new_file


def measure_time(start):
    end = time()
    return end - start

def add_silence_to_audio(file, new_file):
    raw_sound = AudioSegment.from_file(file)
    sample = raw_sound[:SILENCE_AT_BEGINNING_AND_END_MS]
    sample = sample - 70
    output = sample + raw_sound + sample
    output.export(new_file, format='wav')


def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)


def convert_to_mp3(log):
    files = get_file_list()
    for file in files:
        audio = AudioSegment.from_wav(file)
        filename = file.replace("wav","mp3")
        audio.export(filename,format='mp3')
        log.info("Deleting -- %s", file)
        os.remove(file)


def classify_single_audio_file(audio_file):
    classifier = Classifier(audio_file)
    return classifier.identify()


def log_classification_results(classification_results, log):
    for cr in classification_results:
        log.info("""
                 Classification results for %s:
                 Silence: %s, 
                 Applause: %s,
                 Speech: %s,
                 Length: %s
                 """, cr.name, cr.silence, cr.applause, cr.speech, cr.length)


def classify_all_audio_files_if_needed(arguments, log):
    classification_results = []
    if arguments.no_classification is False:
        classify_audio_files(log, classification_results)
    return classification_results

def classify_audio_files(log, classification_results):
    files = get_file_list()
    log.info("7.1 CLASSIFYING FILES")
    for _, file in enumerate(files):
        results = classify_single_audio_file(file)
        cr = ClassificationResults(file, results["Silence"], results["Applause"],
                                       results["Speech"], results["Length"])
        classification_results.append(cr)
    log.info("7.2 END CLASSIFYING")
    log_classification_results(classification_results, log)
