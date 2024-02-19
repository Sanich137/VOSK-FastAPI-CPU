# -*- coding: utf-8 -*-
from datetime import datetime
import logging

# import wave  # создание и чтение аудиофайлов формата wav
# from sys import platform

import ujson  # работа с json-файлами и json-строками

from pydub import AudioSegment

# import soundfile
from vosk import Model, KaldiRecognizer

from Recognizer.models.vosk_model import vosk_models
from Recognizer.utils.pre_start_init import paths
from Recognizer.utils.db_api.db_worker import db
from Recognizer.utils.pre_start_init import punctuation_model

from transformers import logging as logg
logg.set_verbosity_error()


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
        # samples = sound.get_array_of_samples()
        logging.info(f' общая продолжительность аудиофайла {sound.duration_seconds} сек.')
        # фреймрейт на входе
        logging.debug(f'Исходный фреймрейт аудио - {sound.frame_rate}')

        # Меняем фреймрейт на 16кГц
        sound = sound.set_frame_rate(16000)
        logging.debug(f'Изменённый фреймрейт аудио - {sound.frame_rate}')
        # frame_rate = sound.frame_rate
        # Разбиваем звук по каналам
        channels = sound.channels
        separate_channels = sound.split_to_mono()

        logging.debug(f'Используем модель - {model_type}')
        offline_recognizer = KaldiRecognizer(vosk_models[model_type], sound.frame_rate, )
        offline_recognizer.SetWords(True)
        # offline_recognizer.GPUInit()
        offline_recognizer.SetNLSML(enable_nlsml=True)
        logging.debug(f"Инициировали Kadli")

        try:
            for channel in range(channels):
                logging.debug(f'Передаём аудио на распознавание канал № {channel+1}')
                # Основная функция - принимаем весь файл. Возможно, будут траблы на больших файлах.
                offline_recognizer.Reset()
                logging.debug(f'сбросили состояние')
                offline_recognizer.AcceptWaveform(separate_channels[channel].raw_data,)

                # Основная функция - c разбивкой на сэмплы (возможно, уменьшает нагрузку на ОЗУ)
                # _from = 0
                # _step = 4096
                # _to = _step
                # while _from < len(separate_channels[channel].raw_data):
                #     offline_recognizer.AcceptWaveform(separate_channels[channel].raw_data[_from:_to])
                #     _from = _to
                #     _to += _step

                logging.debug(f"Обработали аудио канал № {channel+1} за {datetime.now() - time_rec_start} сек.")

                # raw_data = ujson.loads(offline_recognizer.Result())
                # Попробовать перевести в async
                temp_raw = offline_recognizer.FinalResult()
                logging.debug(f'Получили результат из offline_recognizer в строку')
                raw_data = ujson.loads(temp_raw)
                logging.debug(f'Получили результат из строки в json')

                json_text_data = raw_data['result']
                recognized_text = raw_data['text']
                logging.debug(f"Результат распознавания текста - {recognized_text}")
                json_raw_data.append(json_text_data)
                full_text.append(recognized_text)

        except Exception as e:
            state.request_data[task_id]['state'] = f'recognition error - {e}'
        else:
            # Добавляем пунктуацию
            punctuated_text = offline_punctuation(full_text)

            if not is_async:
                logging.debug(f'Передал распознанный текст в response')
                return punctuated_text
            else:
                # logging.debug(state.request_data)
                state.request_data[task_id]['recognised_text'] = full_text
                state.request_data[task_id]['punctuated_text'] = punctuated_text
                state.request_data[task_id]['json_raw_data'] = json_raw_data
                state.request_data[task_id]['state'] = 'text_successfully_recognised'

            # Сохраняем результат в БД
            db.add_raw_recognition_to_base(task_id).get('state')

            if not state.request_data[task_id]['reuse']:
                state.request_data.pop(task_id)
                logging.debug(f'Заказ № {task_id} удалён из списка отслеживаемых')

            logging.debug(f'На обработку файла затрачено - {datetime.now() - time_rec_start} сек.')


def offline_punctuation(full_text):
    predictor = punctuation_model
    full_res = list()
    for text in full_text:
        tokens = list(enumerate(predictor.tokenize(text)))

        results = ""
        for token, case_label, punc_label in predictor.predict(tokens, lambda x: x[1]):
            prediction = predictor.map_punc_label(predictor.map_case_label(token[1], case_label), punc_label)
            # Лишний пробел перед всем кроме точки и зпт.
            if token[1][0] != '#':
                results = results + ' ' + prediction
            else:
                results = results + prediction

        punct_rec = str(results.strip())
        logging.debug(f'Текст с пунктуацией - {punct_rec}')
        full_res.append(punct_rec)

    return full_res

if __name__ == '__main__':

    data = offline_recognition('')



"https://proglib.io/p/reshaem-zadachu-perevoda-russkoy-rechi-v-tekst-s-pomoshchyu-python-i-biblioteki-vosk-2022-06-30"
"https://stackoverflow.com/questions/29547218/remove-silence-at-the-beginning-and-at-the-end-of-wave-files-with-pydub"
"https://habr.com/ru/articles/735480/"
