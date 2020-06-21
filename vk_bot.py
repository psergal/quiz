from dotenv import load_dotenv
import logging.config
import os
import redis
import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
import tg_log_class
from utils import get_args, get_quiz_questions

logger = logging.getLogger("bot_logger")


if __name__ == "__main__":
    args = get_args()
    memcached_server = args.memcached_server
    memcached_charset = args.memcached_charset
    load_dotenv()
    service_tlg_token = os.environ['SVC_TLG_TOKEN']
    service_chat_id = os.environ['TLG_CHAT_ID']
    vk_api_key = os.environ['VK_API']
    vk_group_id = os.environ['VK_GROUP']
    redis_password = os.environ['REDIS_PASSWORD']
    redis_port = os.environ['REDIS_PORT']

    logger_config = tg_log_class.create_logger_config(service_tlg_token, service_chat_id, __file__)
    logging.config.dictConfig(logger_config)

    redis_client = redis.Redis(host=memcached_server, port=redis_port, password=redis_password,
                               charset=memcached_charset, decode_responses=True, )
    redis_client.flushdb()

    vk_session = vk_api.VkApi(token=vk_api_key)
    vk_api = vk_session.get_api()
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.PRIMARY)
    quiz = get_quiz_questions()
    long_poll = VkLongPoll(vk_session, group_id=vk_group_id)
    for event in long_poll.listen():
        if not (event.type == VkEventType.MESSAGE_NEW and event.to_me):
            continue
        if event.text == 'Новый вопрос':
            quiz_line, quiz_content = random.choice(list(quiz.items()))
            redis_client.rpush(event.user_id, quiz_line, quiz_content[1]['q'], quiz_content[1]['a'])
            vk_api.messages.send(user_id=event.user_id, message=f'{quiz_content[0]}\n{quiz_content[1]["q"]}',
                                 random_id=random.randint(1, 1000), keyboard=keyboard.get_keyboard())
        elif event.text == 'Сдаться':
            if redis_client.llen(event.user_id) > 0:
                answer = redis_client.lrange(event.user_id, -1, -1)[0]
                vk_api.messages.send(user_id=event.user_id, random_id=get_random_id(),
                                     keyboard=keyboard.get_keyboard(), message=f'Правильный ответ\n{answer}')
                redis_client.delete(event.user_id, 0, -1)
        elif event.text == 'Старт':
            vk_api.messages.send(user_id=event.user_id, random_id=get_random_id(),
                                 keyboard=keyboard.get_keyboard(), message='Давай начнем викторину')
        else:
            if redis_client.llen(event.user_id) != 0:
                question, answer = redis_client.lrange(event.user_id, 1, 2)
                if len(event.text) <= 2:
                    vk_api.messages.send(user_id=event.user_id, random_id=get_random_id(),
                                         keyboard=keyboard.get_keyboard(),
                                         message=f'Это читерство!\n Повторяю вопрос\n{question}')
                elif event.text.lower() in answer.lower():
                    vk_api.messages.send(user_id=event.user_id, random_id=get_random_id(),
                                         keyboard=keyboard.get_keyboard(),
                                         message=f'Правильно! Поздравляю!\n{answer}')
                    redis_client.delete(event.user_id, 0, -1)
                else:
                    vk_api.messages.send(user_id=event.user_id, random_id=get_random_id(),
                                         keyboard=keyboard.get_keyboard(),
                                         message='Неправильно\n Попробуешь ещё раз?')
            vk_api.messages.send(user_id=event.user_id, random_id=get_random_id(),
                                 keyboard=keyboard.get_keyboard(), message='Нет заданных вопросов по id')
