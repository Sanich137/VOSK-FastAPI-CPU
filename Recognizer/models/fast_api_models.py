from pydantic import BaseModel, HttpUrl
from typing import Union, Annotated
from fastapi import Query


# class TxtRequest(BaseModel):
#     auth: str  # token
#     question: str
#     variants: Union[int, None] = 3
#
#
# class AudioRequest(BaseModel):
#     auth: str  # token
#     AudioFileUrl: HttpUrl
#     variants: Union[int, None] = 3


class AsyncAudioRequestNewTask(BaseModel):
    """model_type = ['vosk_small', 'vosk_full', 'vosk_adapted']"""
    auth: str  # token
    AudioFileUrl: HttpUrl
    variants: Union[int, None] = 3
    use_model: str = "vosk_small"


class AsyncAudioRequestGetResult(BaseModel):
    """Если reuse = True, то результат запроса можно получить ещё раз. Если False, то запрос придётся делать вновь """
    auth: str  # token
    task_id: str
    reuse: Union[bool, None] = False  # оставлять ли сведения о запросе на будущее.

