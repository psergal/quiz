import logging
import telegram.ext
import requests
import time


class TelegramLogsHandler(logging.Handler):
    """Redefine Telegram logger class  for output to telegram instead of stdout."""
    def __init__(self, svc_tlg_token, svc_chat_id, file):
        super().__init__()
        self.telegram_token = svc_tlg_token
        self.telegram_chat_id = svc_chat_id
        self.telegram_bot = telegram.Bot(self.telegram_token)
        self.module = file.split('/')[-1]
        self.telegram_bot.send_message(chat_id=self.telegram_chat_id,
                                       text=f'Telegram bot has started at {time.ctime()} from:  {self.module}')

    def emit(self, record):
        """Log service messages to telegram chat."""
        log_entry = self.format(record)
        if isinstance(record.exc_info, tuple) and record.exc_info[0] == requests.exceptions.ConnectionError:
            return
        else:
            self.telegram_bot.send_message(chat_id=self.telegram_chat_id, text=f'{log_entry}')


class TlgFilter(logging.Filter):
    def filter(self, record):
        return record.df_intent


def create_logger_config(svc_tlg_token, svc_chat_id, file):
    logger_config = {
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {
            'std_format': {
                'format': '{asctime} - {levelname} - {name} - {module}:{funcName}:{lineno}- {message}',
                'style': '{'
            }
        },
        'handlers': {
            'stdout_handler': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'std_format'
            },
            'tlg_handler': {
                '()': TelegramLogsHandler,
                'svc_tlg_token': svc_tlg_token,
                'svc_chat_id': svc_chat_id,
                'file': file,
                'level': 'INFO',
                'formatter': 'std_format',
                'filters': ['tlg_filter']
            }
        },
        'loggers': {
            'bot_logger': {
                'level': 'INFO',
                'handlers': ['stdout_handler', 'tlg_handler']
            }
        },
        'filters': {
            'tlg_filter': {
                '()': TlgFilter
            }
        },
    }

    return logger_config
