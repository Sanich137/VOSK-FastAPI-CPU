# -*- coding: utf-8 -*-
import logging
from ast import literal_eval as le
import re
import json
import os
from pathlib import Path
import uuid
from datetime import datetime as dt
from config import buffer_size


auth_token = os.environ.get("AUTH_TOKEN")  # Не очень безопасно. Не для промышленного использования.

BASE_DIR = Path(__file__).resolve().parent.parent
paths = {
    "BASE_DIR": BASE_DIR,
    "test_file": BASE_DIR / 'content' / 'g_audio.mp3',
    "trash_folder": BASE_DIR / 'trash',
    "audio_archive_folder": BASE_DIR.parent / 'Audio_archive_folder',
    "model_dir_small": BASE_DIR.parent / 'vosk_models_files' / 'vosk-model-small-ru-0.22',
    "model_dir_complete": BASE_DIR.parent / 'vosk_models_files' / 'vosk-model-ru-0.42',
}

class StateAudioClassifier:
    def __init__(self):
        self.request_limit = buffer_size
        self.request_data = dict()


State = StateAudioClassifier()

