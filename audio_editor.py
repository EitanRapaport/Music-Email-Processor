# pylint: disable=missing-function-docstring,missing-module-docstring

import re
import os
from time import time
import glob
import cyrtranslit
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.effects import compress_dynamic_range
from google_classifier import Classifier
from classification_results import ClassificationResults
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

SILENCE_AT_BEGINNING_AND_END_MS = 3000

def get_file_list():
    return glob.glob("*.wav")


def normalize_all_filenames(log):
    files = get_file_list()
    log.info("3. Normalizing all file names")
    for file in files:
        normalize_filename(file, log)


def normalize_filename(file: str, log):
    if not file.endswith('.wav'):
        return
    new_name = file.replace("：", "")
    new_name = file.replace(":", "")
    log.info(f"3.1 Normalizing {file}")
    #fix cyrillic characters
    new_name = re.sub(r'\W+', ' ', cyrtranslit.to_latin(file, "ru"))
    new_name = re.sub(' wav', ".wav", new_name)
    os.replace(file, new_name)
    log.info(f"3.2 Replaced. Old file name: {file}, New file name: {new_name}")
    return new_name


def compress_file(file, log):
    if not file.endswith('.wav'):
        pass
    else:
        start = time()
        log.info(f'4.1 Compressing: -- {file}')
        raw_sound = AudioSegment.from_file(file)
        compressed_sound = compress_dynamic_range(raw_sound, -20, 6)
        new_file = re.sub(r"\.wav", "_C.wav", file)
        compressed_sound.export(new_file , format='wav')

        log.info("4.2 Deleting -- " + file)
        os.remove(file)
        end = time()
        elapsed = end - start
        log.info(f"4.3 Compressed -- {new_file} took {elapsed} seconds")
        return new_file


def normalize_audio_file(file, log):
    if not file.endswith('.wav'):
        pass

    else:
        log.info(f"5.1 Normalizing -- {file}")
        start = time()
        raw_sound = AudioSegment.from_file(file)
        normalized_file = normalize(raw_sound, 0.1)
        new_file_name = re.sub(r"\.wav", "N.wav", file)
        normalized_file.export(new_file_name, format='wav')

        log.info("5.2 Deleting -- " + file)
        os.remove(file)
        end = time()
        elapsed = end - start
        log.info(f"5.3 Normalized -- {new_file_name} took {elapsed} seconds")
        return new_file_name


def add_silence_to_file(file, log):
    log.info(f"6.1 Adding silence to file -- {file}")
    start = time()
    raw_sound = AudioSegment.from_file(file)
    sample = raw_sound[:SILENCE_AT_BEGINNING_AND_END_MS]
    sample = sample - 70
    output = sample + raw_sound + sample
    new_file = re.sub(r"\.wav", "S.wav", file)
    output.export(new_file, format='wav')

    log.info("6.2 Deleting -- " + file)
    os.remove(file)
    end = time()
    elapsed = end - start
    log.info(f"6.3 Added silence to -- {new_file} took {elapsed} seconds")
    return new_file


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
        files = get_file_list()
        log.info("7.1 CLASSIFYING FILES")
        for _, file in enumerate(files):
            results = classify_single_audio_file(file)
            cr = ClassificationResults(file, results["Silence"], results["Applause"],
                                       results["Speech"], results["Length"])
            classification_results.append(cr)
        log.info("7.2 END CLASSIFYING")
        log_classification_results(classification_results, log)
    return classification_results
