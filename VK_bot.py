import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
import os
from pathlib import Path

import redis
from dotenv import load_dotenv

import logging.config
import TG_log_class

logger = logging.getLogger("bot_logger")


def quiz():
    p = Path('.')
    quiz_path = p / 'arc' / 'quiz-questions'
    quiz_files = list(quiz_path.glob('*.*'))
    quiz_file = random.choice(quiz_files)
    quiz_lines = quiz_file.read_text(encoding='KOI8-R').splitlines()
    quiz_questions = {line_number: file_quiz_line
                      for line_number, file_quiz_line in enumerate(quiz_lines, start=1)
                      if file_quiz_line.startswith('Вопрос') and file_quiz_line.endswith(':')}
    for quiz_question in quiz_questions:
        founded_question, founded_answer = '', ''
        q_flag = True
        for quiz_line in quiz_lines[quiz_question::]:
            if quiz_line and q_flag:
                founded_question = founded_question + quiz_line + '\n'
            elif q_flag:
                q_flag = False
                continue
            if quiz_line and not q_flag:
                if quiz_line.startswith('Ответ:'):
                    continue
                founded_answer = founded_answer + quiz_line + '\n'
            elif not quiz_line and not q_flag:
                break
        quiz_questions[quiz_question] = [quiz_questions.get(quiz_question), {'q': founded_question, 'a': founded_answer}]
    return quiz_questions


if __name__ == "__main__":
    load_dotenv()
    service_tlg_token = os.environ['SVC_TLG_TOKEN']
    service_chat_id = os.environ['TLG_CHAT_ID']
    logger_config = TG_log_class.create_logger_config(service_tlg_token, service_chat_id, __file__)
    logging.config.dictConfig(logger_config)

    vk_api_key = os.environ['VK_API']
    vk_group_id = os.environ['VK_GROUP']

    redis_password = os.environ['REDIS_PASSWORD']
    r_client = redis.Redis(host='redis-12388.c52.us-east-1-4.ec2.cloud.redislabs.com',
                           port=12388, password=redis_password,
                           charset="utf-8", decode_responses=True, )
    r_client.flushdb()

    vk_session = vk_api.VkApi(token=vk_api_key)
    vk_api = vk_session.get_api()
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.PRIMARY)
    quiz = quiz()
    long_poll = VkLongPoll(vk_session, group_id=vk_group_id)
    for event in long_poll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Новый вопрос':
                quiz_line, quiz_content = random.choice(list(quiz.items()))
                r_client.rpush(event.user_id, quiz_line, quiz_content[1]['q'], quiz_content[1]['a'])
                vk_api.messages.send(user_id=event.user_id, message=quiz_content[0] + '\n' + quiz_content[1]['q'],
                                     random_id=random.randint(1, 1000),  keyboard=keyboard.get_keyboard())
            elif event.text == 'Сдаться':
                if r_client.llen(event.user_id) > 0:
                    answer = r_client.lrange(event.user_id, -1, -1)[0]
                    vk_api.messages.send(user_id=event.user_id, random_id=get_random_id(),
                                         keyboard=keyboard.get_keyboard(), message='Правильный ответ' + '\n' + answer)
                    r_client.delete(event.user_id, 0, -1)
            elif event.text == 'Старт':
                vk_api.messages.send(user_id=event.user_id, random_id=get_random_id(),
                                     keyboard=keyboard.get_keyboard(), message='Давай начнем викторину')
            else:
                if r_client.llen(event.user_id) == 0:
                    vk_api.messages.send(user_id=event.user_id, random_id=get_random_id(),
                                         keyboard=keyboard.get_keyboard(), message='Нет заданных вопросов по id')
                else:
                    question, answer = r_client.lrange(event.user_id, 1, 2)
                    if len(event.text) <= 2:
                        vk_api.messages.send(user_id=event.user_id, random_id=get_random_id(),
                                             keyboard=keyboard.get_keyboard(),
                                             message='Это читерство!\n Повторяю вопрос' + '\n' + question)
                    elif event.text.lower() in answer.lower():
                        vk_api.messages.send(user_id=event.user_id, random_id=get_random_id(),
                                             keyboard=keyboard.get_keyboard(),
                                             message='Правильно! Поздравляю!' + '\n' + answer)
                        r_client.delete(event.user_id, 0, -1)
                    else:
                        vk_api.messages.send(user_id=event.user_id, random_id=get_random_id(),
                                             keyboard=keyboard.get_keyboard(),
                                             message='Неправильно\n Попробуешь ещё раз?')







