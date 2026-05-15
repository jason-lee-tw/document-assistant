import os
from datetime import datetime
from enum import StrEnum
from logging import DEBUG, ERROR, INFO, WARNING, getLogger


class CUSTOM_LOG_LEVEL(StrEnum):
  LOG = 'LOG'
  DEBUG = 'DEBUG'
  WARN = 'WARN'
  ERROR = 'ERROR'


class COLOUR(StrEnum):
  RESET = '\033[0m'
  GREEN = '\033[32m'
  AMBER = '\033[33m'
  PURPLE = '\033[35m'
  RED = '\033[31m'


class Logger:
  __tag: str
  __ENABLE_SIMPLE_LOG: bool

  def __init__(self, tag: str = 'No Tag'):
    self.__tag = tag
    self.__ENABLE_SIMPLE_LOG = os.getenv('ENABLE_SIMPLE_LOG', 'false').lower() == 'true'

  def log(self, message: str) -> None:
    self._emit(CUSTOM_LOG_LEVEL.LOG, message)

  def debug(self, message: str) -> None:
    self._emit(CUSTOM_LOG_LEVEL.DEBUG, message)

  def warn(self, message: str) -> None:
    self._emit(CUSTOM_LOG_LEVEL.WARN, message)

  def error(self, message: str) -> None:
    self._emit(CUSTOM_LOG_LEVEL.ERROR, message)

  def _emit(self, level: str, message: str) -> None:
    if not self.__ENABLE_SIMPLE_LOG:
      log_level = self._custom_log_level_to_python_log_level(level)
      logger = getLogger(self.__tag)
      logger.log(level=log_level, msg=message)
      return

    colour = self._get_colour(level)
    timestamp = datetime.now().isoformat(timespec='seconds')
    print(f'{colour}[{timestamp}] [{level}] [{self.__tag}] {message}{COLOUR.RESET}')

  def _custom_log_level_to_python_log_level(self, level: str) -> int:
    map: dict[str, int] = {
      CUSTOM_LOG_LEVEL.LOG: INFO,
      CUSTOM_LOG_LEVEL.DEBUG: DEBUG,
      CUSTOM_LOG_LEVEL.WARN: WARNING,
      CUSTOM_LOG_LEVEL.ERROR: ERROR,
    }

    logging_level = map.get(level)

    if not logging_level:
      raise Exception(f'Invalid log level: {level}')

    return logging_level

  def _get_colour(self, level: CUSTOM_LOG_LEVEL) -> str:
    if not isinstance(level, CUSTOM_LOG_LEVEL):
      raise Exception(f'Invalid log level: {level}')

    colour_map = {
      CUSTOM_LOG_LEVEL.LOG: COLOUR.GREEN,
      CUSTOM_LOG_LEVEL.DEBUG: COLOUR.PURPLE,
      CUSTOM_LOG_LEVEL.WARN: COLOUR.AMBER,
      CUSTOM_LOG_LEVEL.ERROR: COLOUR.RED,
    }

    return colour_map.get(level) or COLOUR.GREEN
