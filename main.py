import config
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, BackgroundTasks
import base64

from Recognizer.utils.db_api.db_worker import db
from Recognizer.utils.logging import logging

from Recognizer.get_audio_file import getting_audiofile
from Recognizer.get_audio_file import del_audio_file
from Recognizer.audio_recognition import offline_recognition

from Recognizer.utils.pre_start_init import auth_token
from Recognizer.models import AsyncAudioRequestNewTask, AsyncAudioRequestGetResult
from Recognizer.LongTimeWorker import State


# Сервер от FastAPI ниже декораторы, для отлавливания событий его сервера

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on_start
    # logging.info("Приложение запущено")
    # await state_audio_classifier.infinity_worker()
    yield  # on_stop
    # logging.info("Приложение завершено") Например, чистить папку с мусором

app = FastAPI(lifespan=lifespan,
              version="0.1",
              docs_url='/docs',
              root_path='/Vosk_Recognizer',
              title='Сервис для распознавания аудио на основе Vosk'
              )


@app.get("/is_alive")
async def check_if_service_is_alive():
    """Не уверен, что нужная вещь. Пока всегда отдаёт, что ошибок нет."""
    # Todo - запустить проверку сервиса - направить запрос и получить ответ. Сверить с ожидаемым ответом и, если ОК,
    #  Возвращать True
    logging.debug('GET_is_alive')
    logging.info(f'В работе {len(State.request_data)} задач')
    return {"error": False,
            "error_description": None,
            "data": State.request_data}


@app.post("/async_audio_recognise/add_task")
async def async_audio_recognise_new_task(new_async_task: AsyncAudioRequestNewTask, background_tasks: BackgroundTasks):
    """
    Работаем в два этапа
     1. Ставим задачу в работу
     2. Получаем результат или текущий статус
    """
    logging.debug('enter_async_audio_classify')
    auth_state = False
    correct_model = False
    task_id = None
    have_file = False
    error_description = None
    error = True

    if new_async_task.auth != auth_token:
        error_description = "wrong auth data"
    else:
        auth_state = True

    if new_async_task.model_type not in ['vosk_small', 'vosk_full', 'vosk_adapted']:
        error_description = "wrong model type chosen"
    else:
        correct_model = True

    if auth_state and correct_model:
        reg_new_task = await State.reg_new_request(
            new_async_task.AudioFileUrl,
            variants=new_async_task.variants)
        if reg_new_task.get('error') != "0":
            error_description = reg_new_task.get('error_description')
        else:
            task_id = reg_new_task.get('data')
            get_new_file = await getting_audiofile(new_async_task.AudioFileUrl)
            if get_new_file:
                have_file = True
                # State.request_data[task_id]['temp_file_path'] = get_new_file
                State.request_data[task_id]['state'] = 'received_file_to_recognise'
            else:
                State.request_data[task_id]['state'] = 'failed_to_receive_file_to_recognise'
                error_description = State.request_data[task_id]['state']
    if have_file:
        # В функции не забыть удалить файл
        background_tasks.add_task(offline_recognition,
                                  new_async_task.AudioFileUrl.path.split('/')[-1],
                                  new_async_task.model_type,
                                  is_async=True,
                                  task_id=task_id,
                                  state=State)
        State.request_data[task_id]['error'] = False
        await db.add_order_to_base(task_id)
        error = False

    response = {"error": error,
                "error_description": error_description,
                "data": State.request_data.get(task_id)
                }

    logging.debug(f'response data - {response}')

    return response

@app.post("/async_audio_recognise/get_result")
async def async_audio_recognise_get_result(get_res_async_task: AsyncAudioRequestGetResult):
    logging.debug('enter_async_audio_classify')
    auth_state = False
    task_id = get_res_async_task.task_id
    error_description = None
    error = True
    data = None
    reuse = get_res_async_task.reuse

    if get_res_async_task.auth != auth_token:
        error_description = "wrong auth data"
    else:
        auth_state = True

    if auth_state:
        question = State.request_data[task_id].get('recognised_text', '')
        if len(question) > 0:
            cat_ids, cat_names = await define_category(question, State.request_data[task_id].get('variants'))
            data = {
                'cat_ids': cat_ids,
                'cat_names': cat_names,
                'recognised_text': question
                }

    # Удалить файл
    file_to_delete = State.request_data[task_id].get('file_url')
    if file_to_delete:
        await del_audio_file(file_url=file_to_delete)

    if not reuse:
        State.request_data.pop(task_id)
        logging.debug(f'Заказ № {task_id} удалён из списка отслеживаемых')

    response = {"error": error,
                "error_description": error_description,
                "data": data
                }

    logging.debug(f'response data - {data}')

    return response

@app.get("/")
async def root():
    return {"error": True,
            "data": "No_service_selected",
            "available_services": ["Vosk_Recognizer"]}


if __name__ == '__main__':
    uvicorn.run(app, host=config.host, port=config.port)

