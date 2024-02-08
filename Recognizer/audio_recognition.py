# -*- coding: utf-8 -*-
import logging

import wave  # создание и чтение аудиофайлов формата wav
from sys import platform

import json  # работа с json-файлами и json-строками

from pydub import AudioSegment

# import soundfile
from vosk import Model, KaldiRecognizer

from Recognizer.models.vosk_model import vosk_models

from Recognizer.utils.pre_start_init import paths


def offline_recognition(file_name, model_type, is_async=False, task_id=None, state=None):

    if not file_name:
        file_path = paths.get('test_file')
    else:
        file_path = paths.get('audio_archive_folder') / file_name

    try:
        sound = AudioSegment.from_file(str(file_path))
    except Exception as e:
        print(e)
    else:
        logging.debug(f'Файл принят в работу')
        samples = sound.get_array_of_samples()

        # Разбиваем звук на два канала

        # todo - получать в запросе данные по аудио (моно/стерео)
        channels = sound.channels

        if channels != 1:
            separate_channels = sound.split_to_mono()

            client_channel = separate_channels[0]
            lawyer_channel = separate_channels[1]
            frame_rate = lawyer_channel.frame_rate
            # Делаем звук в моно
            mono = lawyer_channel.set_channels(1)
        else:
            frame_rate = sound.frame_rate
            # Делаем звук в моно
            mono = sound.set_channels(1)
            frame_rate = mono.frame_rate
        logging.debug(f"разобрались с каналами")

        offline_recognizer = KaldiRecognizer(vosk_models[model_type], frame_rate, )
        offline_recognizer.SetWords(enable_words=True)
        # offline_recognizer.GPUInit()
        offline_recognizer.SetNLSML(enable_nlsml=True)
        logging.debug(f'Передаём аудио на распознавание')
        offline_recognizer.AcceptWaveform(mono.raw_data)
        logging.debug(f"Обработали аудио")

        # для дальнейшей разработки с разбивкой по словам
        # raw_data = json.loads(offline_recognizer.Result())

        recognized_text = json.loads(offline_recognizer.Result())['text'] + ' '
        logging.debug(f"Результат распознавания текста - {recognized_text}")
        # Добавляем пунктуацию
        # cased = subprocess.check_output('python3 recasepunc/recasepunc.py predict recasepunc/checkpoint', shell=True,
        #                                  text=True, input=recognized_text)
        #
        # logging.debug(f"Результат распознавания текста - {cased}")

        if not is_async:
            logging.debug(f'Передал распознанный текст в response')
            return recognized_text
        else:
            logging.debug(state.request_data)
            state.request_data[task_id]['recognised_text'] = recognized_text
            state.request_data[task_id]['state'] = 'text_successfully_recognised'

if __name__ == '__main__':
    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    # file = Path("Classifier/content/2723.mp3").is_file()

    data = offline_recognition('')


"https://proglib.io/p/reshaem-zadachu-perevoda-russkoy-rechi-v-tekst-s-pomoshchyu-python-i-biblioteki-vosk-2022-06-30"
"https://stackoverflow.com/questions/29547218/remove-silence-at-the-beginning-and-at-the-end-of-wave-files-with-pydub"
"https://habr.com/ru/articles/735480/"
