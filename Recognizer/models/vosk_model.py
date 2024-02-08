from vosk import Model
from Recognizer.utils.pre_start_init import paths


vosk_models = {
    'vosk_small': Model(str(paths.get("model_dir_small"))),
#     'vosk_full': Model(str(paths.get("model_dir_complete"))),
    #'vosk_adapted': ""
}