import telegram
import configparser
import logging
import requests
import json
import redis
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from newscatcherapi import NewsCatcherApiClient
from telegram import Update

q = ""
result = ""
global redis1


def main():
    # Load your token and create an Updater for your Bot
    # config = configparser.ConfigParser()
    # config.read('config.ini')
    updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    global redis1
    redis1 = redis.StrictRedis(host=(os.environ['HOST']), port=(os.environ['REDISPORT']),
                      password=(os.environ['PASSWORD']), ssl=True)

    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    dispatcher.add_handler(CommandHandler("collect", collect))
    dispatcher.add_handler(CommandHandler("collections", collections))

    # To start the bot:
    updater.start_polling()
    updater.idle()


def echo(update, context):
    try:
        # config = configparser.ConfigParser()
        # config.read('config.ini')
        query = update.message.text

        newscatcherapi = NewsCatcherApiClient(x_api_key=os.environ['API_KEY'])

        all_articles = newscatcherapi.get_search(q=query,
                                            lang='en',
                                            countries='CA',
                                            page_size=100)
        title = all_articles['articles'][0]['title']
        author = all_articles['articles'][0]['author']
        published_date = all_articles['articles'][0]['published_date']
        link = all_articles['articles'][0]['link']
        
        res ="Title : " + str(title)+'\nAuthor : ' + str(author)+'\nPublished date : ' + str(published_date)+'\nLink : '+str(link)
        
        global q
        q = query

        global result
        result = res

        context.bot.send_message(chat_id=update.effective_chat.id, text=res)
    except (IndexError, ValueError):
        update.message.reply_text('No content, please try other keyword!')

def collect(update: Update, context: CallbackContext) -> None:
    try: 
        global redis1
        _res = redis1.set(q, result)
        print("SET Message returned : " + str(_res))
        update.message.reply_text("collect sucess!")
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

def collections(update: Update, context: CallbackContext) -> None:
    global redis1
    keys = redis1.keys('*')
    for key in keys:
        val = redis1.get(key)
        print("GET Message returned : " + val.decode("utf-8"))

        update.message.reply_text(val.decode("utf-8"))

if __name__ == '__main__':
    main()
