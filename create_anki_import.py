## workon anki_importer

import re
import sys
import argparse
import requests
import shutil
import urllib

FORVO_STANDARD_PRONUNCIATION_URL = 'https://apifree.forvo.com/key/{key}/format/json/action/standard-pronunciation/word/{greek}/language/el'

RAW_RECORDINGS_PATH = '/Users/sophia/greek/raw_recordings/{greek}.mp3'
ANKI_MEDIA_PATH = '/Users/sophia/Library/Application Support/Anki2/User 1/collection.media/{english}.mp3'

ANKI_IMPORT_LINE = "{english}, {greek}, [sound:{english}.mp3]\n"

FAILURES = []

def _read_key():
    with open('SECRET_KEY', 'r') as f:
        return f.read().strip()

def parse_vocab_pairs_from_file(input_file):
    vocab_pairs = []
    with open(input_file, 'r') as f:
        entries = f.readlines()

    for line in entries:
        clean = line.strip()
        eng, greek = clean.split(',')
        processed = (eng.strip(), greek.strip())
        print('Processed:{}'.format(processed))
        vocab_pairs.append(processed)

    return vocab_pairs


def download_pronunciation_to_anki(english, greek):
    greek_wo_article = re.sub('^(η|το|ο) ', '', greek)
    escaped_utf8_greek = urllib.parse.quote(greek_wo_article.encode('utf-8'))
    res = requests.get(FORVO_STANDARD_PRONUNCIATION_URL.format(key=_read_key(), greek=escaped_utf8_greek))
    forvo_data = res.json()
    print('Downloading pronunciation info from Forvo with status {}'.format(res.status_code))

    mp3_url = forvo_data['items'][0]['pathmp3']
    raw_recording_path = RAW_RECORDINGS_PATH.format(greek=greek)

    print('Downloading {} to {}'.format(mp3_url, raw_recording_path))
    mp3_content = requests.get(mp3_url).content
    with open(raw_recording_path, 'wb') as f:
        f.write(mp3_content)

    anki_recording_path = ANKI_MEDIA_PATH.format(english=english)
    shutil.copyfile(raw_recording_path, anki_recording_path)
    print('Copying {} to {}'.format(raw_recording_path, anki_recording_path))


def generate_anki_import(input_file, output_file=None):
    if output_file is None:
        output_file = 'anki_' + input_file
    entries = parse_vocab_pairs_from_file(input_file)
    for english, greek in entries:
        anki_path = None
        try:
            download_pronunciation_to_anki(english, greek)
        except Exception as e:
            print('--------> Failed to get recording for {} -- {} ({})'.format(english, greek, e))
            FAILURES.append((english, greek))
        with open(output_file, 'a') as f:
            f.write(ANKI_IMPORT_LINE.format(english=english, greek=greek))

    print('Failed: {} words'.format(len(FAILURES)))
    for pair in FAILURES:
        print('{},'.format(pair))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make Anki cards w pronunciations')
    parser.add_argument('input_file', help='')
    parser.add_argument('--output-file', help='')

    args = parser.parse_args()

    generate_anki_import(args.input_file, args.output_file)

    # manual fixes:
    # imports & vars & download_pronunciation_to_anki into shell
    # fix eng/greek in anki_import... file
    # download_pronunciation_to_anki('andyou', 'εσένα')


## FIX RIGHT
