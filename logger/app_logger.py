import json
import sys
import inspect
import os
import time
from datetime import datetime

from loguru import logger
from tqdm import tqdm
import html
import logging
import re
import traceback

from settings import settings

logger_format = "<green>{time}</green> | <level>{level: <8}</level> | {extra[logger_context]} | <level>{message}</level>"
logger.remove()

log_level="INFO"
# Get current epoch time
current_epoch_time = datetime.now().timestamp() * 1000
log_file_name = settings.APP_NAME
logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True, format=logger_format, backtrace=True, diagnose=True,
               enqueue=True, level=log_level)
logger.add(log_file_name, format=logger_format, rotation="10 MB", backtrace=True, diagnose=True, enqueue=True,
               level=log_level)
custom_logger = None
html_tags_regex = re.compile(r'(<[^>]*>)')

HTML_TAGS_REGEX = re.compile('<.*?>')
def cleanhtml(raw_html):
  cleantext = re.sub(HTML_TAGS_REGEX, '', raw_html)
  return cleantext


# redirect all logging to loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # from pdb import set_trace; set_trace()
        custom_logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
        # log_message(record.getMessage(), level=level)


# Define a function that adds contextual information to the logger
def add_logger_context(log_level="INFO", **kwargs):
    global custom_logger

    custom_logger = logger.bind(logger_context=kwargs).opt(colors=True)
    handler = InterceptHandler()
    logging.basicConfig(handlers=[handler], level=log_level)


def colorize_filename(filename):
    # Colorize only the filename portion of the path
    filename_parts = filename.split(os.sep)
    filename_parts[-1] = f"<cyan>{filename_parts[-1]}</cyan>"
    return os.sep.join(filename_parts)


def format_to_str(data):
    data = repr(data)[1:-1]
    if isinstance(data, str):
        return data
    elif isinstance(data, bool):
        return str(data).lower()
    elif isinstance(data, (int, float)):
        return str(data)
    elif isinstance(data, list):
        return "[" + ", ".join(format_to_str(item) for item in data) + "]"
    elif isinstance(data, tuple):
        return "(" + ", ".join(format_to_str(item) for item in data) + ")"
    elif isinstance(data, set):
        return "{" + ", ".join(format_to_str(item) for item in data) + "}"
    elif isinstance(data, dict):
        return "{" + ", ".join(f"{format_to_str(key)}: {format_to_str(value)}" for key, value in data.items()) + "}"
    else:
        return str(data)


def log_message(message, *args, **kwargs):
    # message = repr(html.escape(message, quote=True))[1:-1]
    global custom_logger
    if not custom_logger:
        custom_logger = logger.bind(logger_context=kwargs).opt(colors=True)
    message = repr(message)[1:-1]

    level = kwargs.pop("level", "info")
    if isinstance(level, str):
        level = level.lower()

    # if logging._nameToLevel.get(level, -1) <= logging.root.level:
    #     return

    # Get the frame of the caller
    frame = inspect.currentframe().f_back

    # Get the caller's filename relative to the project root
    filename = os.path.relpath(inspect.getfile(frame.f_code), start=os.getcwd())

    # Get the caller's function name and line number
    func_name = frame.f_code.co_name
    line_no = frame.f_lineno

    # message can contain HTML tags. do NOT escape it by using html.escape
    # loguru expects all html tags to be prepended with a '\' in order to be escaped

    message = cleanhtml(message)

    message = re.sub(html_tags_regex, r'\\\1', message)
    func_name = re.sub(html_tags_regex, r'\\\1', func_name)
    args = re.sub(html_tags_regex, r'\\\1', ' '.join(map(format_to_str, args)))

    # Format the log message with the filename, function name, and line number
    message = f"{colorize_filename(filename)}::<b><e>{func_name}</e></b> (<y>{line_no}</y>) - {message} {args}"

    # Use the logger to log the message

    level_mapping = {
        "debug": custom_logger.debug,
        logging.DEBUG: custom_logger.debug,

        "info": custom_logger.info,
        logging.INFO: custom_logger.info,

        "warn": custom_logger.warning,
        "warning": custom_logger.warning,
        logging.WARNING: custom_logger.warning,

        "error": custom_logger.error,
        logging.ERROR: custom_logger.error,

        "critical": custom_logger.critical,
        logging.CRITICAL: custom_logger.critical,

        "fatal": custom_logger.critical,
        logging.FATAL: custom_logger.critical,
    }

    try:
        level_mapping[level](message, **kwargs)
    except Exception:
        # TODO: pls fix
        traceback.print_exc()
        print(message, flush=True)
        return


if __name__ == "__main__":
    add_logger_context(logger_context="test")
    log_message("test message")
    log_message("test message", level="debug")
    log_message("test message", level="warning")
    log_message("test message", level="error")
    log_message("test message", level="critical")
    log_message("test message", level="fatal")

    log_message("test message", level=logging.DEBUG)
    log_message("test message", level=logging.INFO)
    log_message("test message", level=logging.WARNING)
    log_message("test message", level=logging.ERROR)
    log_message("test message", level=logging.CRITICAL)
    log_message("test message", level=logging.FATAL)

    log_message("test message", level="debug", extra={"logger_context": "test"})
    log_message("test message", level="warning", extra={"logger_context": "test"})
    log_message("test message", level="error", extra={"logger_context": "test"})
    log_message("test message", level="critical", extra={"logger_context": "test"})
    log_message("test message", level="fatal", extra={"logger_context": "test"})

    log_message("test message", level=logging.DEBUG, extra={"logger_context": "test"})
    log_message("test message", level=logging.INFO, extra={"logger_context": "test"})
    log_message("test message", level=logging.WARNING, extra={"logger_context": "test"})
    log_message("test message", level=logging.ERROR, extra={"logger_context": "test"})
    log_message("test message", level=logging.CRITICAL, extra={"logger_context": "test"})
    log_message("test message", level=logging.FATAL, extra={"logger_context": "test"})

    log_message("test message", level="debug", extra={"logger_context": "test"}, a=1, b=2)
    log_message("test message", level="warning", extra={"logger_context": "test"}, a=1, b=2)
    log_message("test message", level="error", extra={"logger_context": "test"}, a=1, b=2)
    log_message("test message", level="critical", extra={"logger_context": "test"}, a=1, b=2)
    log_message("test message", level="fatal", extra={"logger_context": "test"}, a=1, b=2)
