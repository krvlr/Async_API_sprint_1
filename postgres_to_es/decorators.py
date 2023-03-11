from functools import wraps
from time import sleep

from loguru import logger


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor)
    до граничного времени ожидания (border_sleep_time)
    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    if start_sleep_time < 0.001:
        logger.warning("start_sleep_time менее 0.001. Устанавливаем минимум 0.001")
        start_sleep_time = 0.001

    if border_sleep_time < 1:
        logger.warning("border_sleep_time менее 1. Устанавливаем минимум 1")
        border_sleep_time = 1

    def decorator(func):
        @wraps(func)
        def retry(*args, **kwargs):
            n, t = 0, 0
            while True:
                t = (
                    start_sleep_time * factor**n
                    if t < border_sleep_time
                    else border_sleep_time
                )

                try:
                    n += 1
                    sleep(t)
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Ошибка {e}")
                    logger.exception(e)
                    logger.warning(
                        f"Ожидаем {t} секунд переда перезапуском функции {func.__name__}"
                    )

        return retry

    return decorator
