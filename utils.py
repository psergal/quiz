import argparse
from pathlib import Path
import random


def get_args():
    parser = argparse.ArgumentParser(description='Launching VK chat bot')
    parser.add_argument('-m', '--memcached_server', default='redis-12388.c52.us-east-1-4.ec2.cloud.redislabs.com',
                        help='Set the server to store and retrieve questions and answers. Redislabs set default')
    parser.add_argument('-c', '--memcached_charset', default='utf-8',
                        help='Set the charset  for the stored values. utf-8 set default')
    arguments = parser.parse_args()
    return arguments


def get_quiz_questions():
    local_path = Path('.')
    quiz_path = local_path / 'quiz-questions'
    quiz_files = list(quiz_path.glob('*.*'))
    quiz_file = random.choice(quiz_files)
    quiz_lines = quiz_file.read_text(encoding='KOI8-R').splitlines()
    question_lines_dict = {line_number: file_quiz_line
                           for line_number, file_quiz_line in enumerate(quiz_lines, start=1)
                           if file_quiz_line.startswith('Вопрос') and file_quiz_line.endswith(':')}
    for quiz_question in question_lines_dict:
        question_text, answer_text = '', ''
        q_flag = True
        for quiz_text_line in quiz_lines[quiz_question::]:
            if quiz_text_line and q_flag:
                question_text = f'{question_text}{quiz_text_line} '
            elif q_flag:
                q_flag = False
                continue
            if not quiz_text_line and not q_flag:
                break
            elif quiz_text_line.startswith('Ответ:'):
                continue
            elif not q_flag:
                answer_text = f'{answer_text}{quiz_text_line} '
        question_lines_dict[quiz_question] = [question_lines_dict.get(quiz_question),
                                              {'q': question_text, 'a': answer_text}]
    return question_lines_dict
