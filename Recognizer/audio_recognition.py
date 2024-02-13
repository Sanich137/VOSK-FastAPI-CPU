# -*- coding: utf-8 -*-
from datetime import datetime
import logging

import wave  # создание и чтение аудиофайлов формата wav
from sys import platform

import json  # работа с json-файлами и json-строками

from pydub import AudioSegment

# import soundfile
from vosk import Model, KaldiRecognizer

from Recognizer.models.vosk_model import vosk_models

from Recognizer.utils.pre_start_init import paths
from Recognizer.utils.db_api.db_worker import db


def offline_recognition(file_name, model_type, is_async=False, task_id=None, state=None):
    time_rec_start = datetime.now()
    json_raw_data = list()
    full_text = list()

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
        logging.info(f' общая продолжительность аудиофайла {sound.duration_seconds} сек.')
        # Разбиваем звук по каналам
        channels = sound.channels

        separate_channels = sound.split_to_mono()
        frame_rate = sound.frame_rate
        logging.debug(f'Используем модель - {model_type}')
        offline_recognizer = KaldiRecognizer(vosk_models[model_type], frame_rate, )
        offline_recognizer.SetWords(enable_words=True)
        # offline_recognizer.GPUInit()
        offline_recognizer.SetNLSML(enable_nlsml=True)
        logging.debug(f"Инициировали Kadli")

        try:
            for channel in range(channels):
                logging.debug(f'Передаём аудио на распознавание канал № {channel+1}')
                # Основная функция - принимаем весь файл. Возможно, будут траблы на больших файлах.
                offline_recognizer.AcceptWaveform(separate_channels[channel].raw_data)

                # Основная функция - c разбивкой на сэмплы (возможно, уменьшает нагрузку на ОЗУ)
                # _from = 0
                # _step = 4096
                # _to = _step
                # while _from < len(separate_channels[channel].raw_data):
                #     offline_recognizer.AcceptWaveform(separate_channels[channel].raw_data[_from:_to])
                #     _from = _to
                #     _to += _step

                logging.debug(f"Обработали аудио канал № {channel+1}")

                raw_data = json.loads(offline_recognizer.Result())
                json_text_data = raw_data['result']
                recognized_text = raw_data['text']
                logging.debug(f"Результат распознавания текста - {recognized_text}")
                json_raw_data.append(json_text_data)
                full_text.append(recognized_text)

        except Exception as e:
            state.request_data[task_id]['state'] = f'recognition error - {e[:100]}'
        else:
            logging.debug(f'На обработку файла затрачено - {datetime.now()-time_rec_start} сек.')

            # Добавляем пунктуацию
            # cased = subprocess.check_output('python3 recasepunc/recasepunc.py predict recasepunc/checkpoint', shell=True,
            #                                  text=True, input=recognized_text)
            #
            # logging.debug(f"Результат распознавания текста - {cased}")

            if not is_async:
                logging.debug(f'Передал распознанный текст в response')
                return full_text
            else:
                logging.debug(state.request_data)
                state.request_data[task_id]['recognised_text'] = full_text
                state.request_data[task_id]['json_raw_data'] = json_raw_data

                state.request_data[task_id]['state'] = 'text_successfully_recognised'

            if db.add_raw_recognition_to_base(task_id).get('state'):
                if not state.request_data[task_id]['reuse']:
                    state.request_data.pop(task_id)
                    logging.debug(f'Заказ № {task_id} удалён из списка отслеживаемых')
            else:
                logging.error(f'Не удалось сохранить результат распознавания - '
                              f'{db.add_raw_recognition_to_base(task_id).get("Error")}')

if __name__ == '__main__':

    data = offline_recognition('')


"https://proglib.io/p/reshaem-zadachu-perevoda-russkoy-rechi-v-tekst-s-pomoshchyu-python-i-biblioteki-vosk-2022-06-30"
"https://stackoverflow.com/questions/29547218/remove-silence-at-the-beginning-and-at-the-end-of-wave-files-with-pydub"
"https://habr.com/ru/articles/735480/"
