import os
import logging
import httpx

from Recognizer.utils.pre_start_init import paths


async def getting_audiofile(file_url) -> bool:
    res = False
    file_name = file_url.path.split('/')[-1]
    if 'mp3' in file_name:
        temp_file_path = paths.get("audio_archive_folder") / file_name
        get_file_url = file_url.unicode_string()
    else:
        return res

    if temp_file_path.exists():
        logging.info(f"Файл {file_url.path.split('/')[-1]} уже получен, будет использован ранее полученный файл.")
        res = temp_file_path
    else:
        async with httpx.AsyncClient() as sess:
            try:
                response = await sess.get(
                    url=get_file_url
                )
                file_data = response.content
            except Exception as e:
                logging.error(f'Ошибка получения файла из ЕРП - {e}')
            else:
                try:
                    with open(temp_file_path, "wb") as temp_file:
                        temp_file.write(file_data)
                except Exception as e:
                    logging.error(e)
                else:
                    # Тут может быть ошибка
                    res = temp_file_path
    return res


async def del_audio_file(file_url=None, filepath=None) -> bool:
    if file_url:
        temp_file_path = paths.get("audio_archive_folder") / file_url.path.split('/')[-1]
    elif filepath:
        temp_file_path = filepath
    else:
        temp_file_path = None

    if temp_file_path:
        try:
            os.remove(temp_file_path)
        except Exception as e:
            logging.error(f"не смог удалить файл {temp_file_path}. Ошибка: {e}")
            return False
        else:
            logging.debug(f"Удалил файл {temp_file_path}.")
    return True
