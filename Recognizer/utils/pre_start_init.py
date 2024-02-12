# -*- coding: utf-8 -*-
import logging
from ast import literal_eval as le
import re
import json
import os
from sys import platform
from pathlib import Path
import uuid
from datetime import datetime as dt
from config import buffer_size

auth_token = os.environ.get("AUTH_TOKEN")  # Не очень безопасно. Не для промышленного использования.

unix_db = Path(os.environ.get("DB_PATH", ''))  # linux
Win_base_dir = Path(__file__).resolve().parent.parent

if platform == "linux" or platform == "linux2":
    db = unix_db / 'recogniser.db'
elif platform == "darwin":
    pass
elif platform == "win32":
    db = Win_base_dir / 'recogniser.db'

paths = {
    "BASE_DIR": Win_base_dir,
    "test_file": Win_base_dir / 'content' / 'g_audio.mp3',
    "trash_folder": Win_base_dir / 'trash',
    "audio_archive_folder": Win_base_dir.parent / 'Audio_archive_folder',
    "model_dir_small": Win_base_dir.parent / 'vosk_models_files' / 'vosk-model-small-ru-0.22',
    "model_dir_complete": Win_base_dir.parent / 'vosk_models_files' / 'vosk-model-ru-0.42',
    "db": db,
}

#
# class StateAudioClassifier:
#     def __init__(self):
#         self.request_limit = buffer_size
#         self.request_data = dict()
#
#
# State = StateAudioClassifier()
#
