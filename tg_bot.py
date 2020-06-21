from dotenv import load_dotenv
import logging.config
import os
import random
import redis

from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
import tg_log_class
from utils import get_args, get_quiz_questions

logger = logging.getLogger("bot_logger")

CHOOSE_QUEST, TYPING_REPLY, CHOOSE_SURRENDER = range(3)
reply_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def quiz_callback(update: Update, context):
    """Ask new question """
    client_redis = context.bot_data['r']
    if update.message.text == 'Новый вопрос':
        quiz_line, quiz_content = random.choice(list(quiz.items()))
        context.bot.send_message(chat_id=update.message.chat_id, text=quiz_content[0])
        context.bot.send_message(chat_id=update.message.chat_id, text=quiz_content[1]['q'])
        client_redis.rpush(update.effective_user.id, quiz_line, quiz_content[1]['q'], quiz_content[1]['a'])
    elif update.message.text == 'Сдаться':
        context.bot.send_message(chat_id=update.message.chat_id, text='Правильный ответ')
        answer = client_redis.lrange(update.effective_user.id, -1, -1)[0]
        context.bot.send_message(chat_id=update.message.chat_id, text=answer)
        client_redis.delete(update.effective_user.id, 0, -1)
        update.message.reply_text('Bye! I hope we can talk again some day.',
                                  reply_markup=ReplyKeyboardRemove())
    else:
        answer = client_redis.lrange(update.effective_user.id, -1, -1)[0]
        if update.message.text.lower() in answer.lower():
            context.bot.send_message(chat_id=update.message.chat_id, text='Правильно! Поздравляю!')
            context.bot.send_message(chat_id=update.message.chat_id, text=answer)
            client_redis.delete(update.effective_user.id, 0, -1)
            return
        context.bot.send_message(chat_id=update.message.chat_id, text='Неправильно\n Попробуешь ещё раз?"')


def start_quiz(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.message.chat_id, text="I'm a quiz bot, Let's play with me!",
                             reply_markup=markup)
    return CHOOSE_QUEST


def handle_new_question_request(update: Update, context: CallbackContext):
    client_redis = context.bot_data['r']
    quiz_line, quiz_content = random.choice(list(quiz.items()))
    context.bot.send_message(chat_id=update.message.chat_id, text=quiz_content[0])
    context.bot.send_message(chat_id=update.message.chat_id, text=quiz_content[1]['q'], reply_markup=markup)
    client_redis.rpush(update.effective_user.id, quiz_line, quiz_content[1]['q'], quiz_content[1]['a'])
    return TYPING_REPLY


def handle_surrender(update: Update, context: CallbackContext):
    client_redis = context.bot_data['r']
    if client_redis.llen(update.effective_user.id) > 0:
        answer = client_redis.lrange(update.effective_user.id, -1, -1)[0]
        context.bot.send_message(chat_id=update.message.chat_id, text='Правильный ответ')
        context.bot.send_message(chat_id=update.message.chat_id, text=answer)
        client_redis.delete(update.effective_user.id, 0, -1)
    update.message.reply_text('Не унывай!',
                              reply_markup=markup)
    return CHOOSE_QUEST


def handle_solution_attempt(update: Update, context: CallbackContext):
    client_redis = context.bot_data['r']
    answer = client_redis.lrange(update.effective_user.id, -1, -1)[0]
    if len(update.message.text) <= 2:
        context.bot.send_message(chat_id=update.message.chat_id, text='Это читерство!\n Попробуешь ещё раз?',
                                 reply_markup=markup)
        return TYPING_REPLY
    elif update.message.text.lower() in answer.lower():
        context.bot.send_message(chat_id=update.message.chat_id, text='Правильно! Поздравляю!',
                                 eply_markup=markup)
        context.bot.send_message(chat_id=update.message.chat_id, text=answer)
        client_redis.delete(update.effective_user.id, 0, -1)
        return CHOOSE_QUEST
    context.bot.send_message(chat_id=update.message.chat_id, text='Неправильно\n Попробуешь ещё раз?',
                             reply_markup=markup)
    return TYPING_REPLY


def handle_score(update: Update, context):
    # logger.warning('Update "%s" caused error "%s"', update, context.error, extra={'Update_err': True})
    context.bot.send_message(chat_id=update.message.chat_id, text='Счета пока нет')
    # закрыть редис? в логгер записать кто поиграл?
    return ConversationHandler.END


def log_error(update: Update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error, extra={'Update_err': True})


def call_bot(telegram_token, redis_cnn):
    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.bot_data = {'r': redis_cnn}
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_quiz)],

        states={
            CHOOSE_QUEST: [MessageHandler(Filters.regex('^Новый вопрос$'), handle_new_question_request),
                           MessageHandler(Filters.regex('^Сдаться$'), handle_surrender)
                           ],
            TYPING_REPLY: [MessageHandler(Filters.regex('^Мой счет$'), handle_score),
                           MessageHandler(Filters.regex('^Сдаться$'), handle_surrender),
                           MessageHandler(Filters.text, handle_solution_attempt)
                           ],
            CHOOSE_SURRENDER: [MessageHandler(Filters.regex('^Сдаться$'), handle_surrender)],
        },
        fallbacks=[MessageHandler(Filters.regex('^Мой счет$'), handle_score)]
    )

    dispatcher.add_handler(conversation_handler)
    dispatcher.add_error_handler(log_error)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    args = get_args()
    memcached_server = args.memcached_server
    memcached_charset = args.memcached_charset
    load_dotenv()
    tlg_token = os.environ['TLG_TOKEN']
    service_tlg_token = os.environ['SVC_TLG_TOKEN']
    service_chat_id = os.environ['TLG_CHAT_ID']
    redis_password = os.environ['REDIS_PASSWORD']
    redis_port = os.environ['REDIS_PORT']
    quiz = get_quiz_questions()
    logger_config = tg_log_class.create_logger_config(service_tlg_token, service_chat_id, __file__)

    logging.config.dictConfig(logger_config)
    redis_client = redis.Redis(host=memcached_server, port=redis_port, password=redis_password,
                               charset=memcached_charset, decode_responses=True, )
    redis_client.flushdb()
    call_bot(tlg_token, redis_client)
