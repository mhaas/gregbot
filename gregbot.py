#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import feed
import time
import random
import secret

last_wod = 0
interval = 10

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

shops = []
shops.append(u"Der BCAA Drink aus dem Box Shop bringt euch ganz nach vorne!")
shops.append(u"Macht euch Tape um die Daumen.. gibt's im Box Shop!")
shops.append(u"Kaltes Kokoswasser aus dem Box Shop.. richtig gut für die Recovery, Leute!")
shops.append(u"Kein Wunder, dass ihr keine Double Unders könnt. Kauft euch ein Seil aus dem Box Shop! #doubleundergarantie")
shops.append(u"Rope Climbs! Zieht eure Handschuhe an.. gibt's im Box Shop!")
shops.append(u"Du willst endlich so cool wie dein Coach aussehen? Schnapp dir die neuen Sance socks")
shops.append(u"Neu im Box Shop: Shirts in Schmedium!")
shops.append(u"Du bist der totale Versager im wod? Zieh dir ein Focus bcaa - wodden bis der Arzt kommt")
shops.append(u"Neu im Box Shop: wechselunterhose für max out squats")
shops.append(u"Neu im Box Shop: Tempos für mimimi Mittwoch")
shops.append(u"Neu im Box Shop: der Bestseller: die einstuhlung")
shops.append(u"Neu im Box Shop: kotztüten")
shops.append(u"Neu im Box Shop: Gregors Bestseller: Motivation durch Provokation")
shops.append(u"Jetzt neu im Box Shop: Drei weitere Fragen für captain Chaos")

motivations = []
motivations.append(u"Wenigstens hast du dich hübsch angezogen.")
motivations.append(u"Mach dir nichts draus. Die Hose kannst du waschen.")
motivations.append(u"Wer sich nicht einstuhlt hat aufgegeben!")
motivations.append(u"Lass gut sein, das wird heut nicht besser...")
motivations.append(u"Gas geben ihr Lappen!")

cakes = [u"\U0001F370", u"\U0001F382", u"\U0001F369", u"\U0001F36A" ]

unknown_msg = "Keine Ahnung! Vivi?! Ist das schon gepostet?"

drivel = {"shop" : shops, "motivation": motivations, "kuchen": cakes, "start": ["Hi!"], "help": ["Vivi?!"],
"werdasanklicktistneugierigundeinspielkind": ["So sieht's wohl aus.", "Komm du mal lieber ins Training."], "lappen": ["Hi!"]}

spam_msgs = []
spam_msgs.append(u"Hab' ich doch gerade schon geschrieben. Scroll halt mal hoch!")
spam_msgs.append(u"Steht doch oben. Geschwätzt ist halt schnell!")
spam_msgs.append(u"Komm am besten nach der Stunde kurz zu mir")
spam_msgs.append(u"Da würde ich dir ein Personal Training empfehlen.")
spam_msgs.append(u"Die Vivi kümmert sich drum!")

def spam(timeout=30):
    spam_state = {}
    def spam_decorator(func):
        def func_wrapper(bot, update):
            key = "%s" % (update.message.chat_id,)
            if key not in spam_state:
                spam_state[key] = { "last_message_ts": 0, "annoyed": 0}
            if spam_state[key]["last_message_ts"] > time.time() - timeout:
                # called again too quickly
                if not spam_state[key]["annoyed"]:
                    bot.sendMessage(update.message.chat_id, text=random.choice(spam_msgs))
                # we are annoyed and stay quiet till timeout
                spam_state[key]["annoyed"] = 1
            else:
                spam_state[key]["annoyed"] = 0
                spam_state[key]["last_message_ts"] = time.time()
                return func(bot, update)
        return func_wrapper
    return spam_decorator


# same decorator as wod
@spam(timeout=600)
def wodtoday(bot, update):
    wod(bot, update)

def wod_handler(msg, bot, update):
    if msg:
        msg = msg[2]
    else:
        msg = unknown_msg
    bot.sendMessage(update.message.chat_id, text=msg)

@spam(timeout=600)
def wod(bot, update):
    wod_handler(feed.get_today(), bot, update)

@spam(timeout=600)
def wodtomorrow(bot, update):
    wod_handler(feed.get_tomorrow(), bot, update)

@spam(timeout=600)
def pbplan(bot, update):
    wod_handler(feed.get_today(wod="Competition"), bot, update)

@spam(timeout=600)
def pbplantomorrow(bot, update):
    wod_handler(feed.get_tomorrow(wod="Competition"), bot, update)

def pounds(bot, update, args):
    kg = float(args[0])
    if kg < 0:
        bot.sendMessage(update.message.chat_id, text='Negatives Gewicht oder wie?')
    else:
        bot.sendMessage(update.message.chat_id, text="%s kg sind %.2f Pfund!" % (kg, kg * 2.20462))

def kilos(bot, update, args):
    pounds = float(args[0])
    if pounds < 0:
        bot.sendMessage(update.message.chat_id, text='Negatives Gewicht oder wie?')
    else:
        bot.sendMessage(update.message.chat_id, text="%s Pfund sind %.2fkg!" % (pounds, pounds / 2.20462))

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(secret.secret)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # hook up drivel
    for command in drivel:
        data = drivel[command]

        def make_callback(d):
            # wrapper needed to bind data properly
            @spam(timeout=1200)
            def callback(bot, update):
                msg = random.choice(d)
                bot.sendMessage(update.message.chat_id, text=msg)
            return callback

        # TODO: disabled
        dp.add_handler(CommandHandler(command, make_callback(data)))

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("wod", wod))
    dp.add_handler(CommandHandler("wodtomorrow", wodtomorrow))
    dp.add_handler(CommandHandler("pbplan", pbplan))
    dp.add_handler(CommandHandler("pbplantomorrow", pbplantomorrow))
    dp.add_handler(CommandHandler("pounds", pounds, pass_args=True))
    dp.add_handler(CommandHandler("kilos", kilos, pass_args=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()



if __name__ == '__main__':
    main()
