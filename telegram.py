import logging
from pwnagotchi.voice import Voice
import pwnagotchi.plugins as plugins


class Telegram(plugins.Plugin):
    __author__ = 'djerfy@gmail.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'Periodically sent messages to Telegram about the recent activity of pwnagotchi'

    def on_loaded(self):
        logging.info("telegram plugin loaded.")

    # called when there's available internet
    def on_internet_available(self, agent):
        config = agent.config()
        display = agent.view()
        last_session = agent.last_session

        if last_session.is_new() and last_session.handshakes > 0:

            try:
                import telegram
            except ImportError:
                logging.error("Couldn't import telegram")
                return

            logging.info("Detected new activity and internet, time to send a message!")

            picture = '/root/pwnagocthi.png'
            display.on_manual_mode(last_session)
            display.image().save(picture, 'png')
            display.update(force=True)

            try:
                logging.info("Connecting to Telegram...")

                message = Voice(lang=config['main']['lang']).on_last_session_tweet(last_session)

                bot = telegram.Bot(self.options['bot_token'])
                bot.sendPhoto(chat_id=self.options['chat_id'], photo=open(picture, 'rb'))
                bot.sendMessage(chat_id=self.options['chat_id'], text=message, disable_web_page_preview=True)

                last_session.save_session_id()
                logging.info("telegram: %s" % message)
                display.set('status', 'Message sent!')
                display.update(force=True)
            except Exception:
                logging.exception("Error while sending on Telegram")
