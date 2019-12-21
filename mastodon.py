import os
import logging
from pwnagotchi.voice import Voice
import pwnagotchi.plugins as plugins
try:
    from mastodon import Mastodon
except ImportError:
    logging.error('Could not import mastodon')


class MastodonStatus(plugins.Plugin):
    __author__ = 'siina@siina.dev'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'Periodically post status updates. Based on twitter plugin by evilsocket'

    def on_loaded(self):
        logging.info("mastodon plugin loaded.")

    # Called when there's available internet
    def on_internet_available(self, agent):
        config = agent.config()
        display = agent.view()
        last_session = agent.last_session
        api_base_url = self.options['instance_url']
        email = self.options['email']
        password = self.options['password']
        visibility = self.options['visibility']
        client_cred = '/root/.mastodon.client.secret'
        user_cred = '/root/.mastodon.user.secret'

        if last_session.is_new() and last_session.handshakes > 0:
            logging.info("Detected internet and new activity: time to post!")

            if not os.path.isfile(user_cred) or not os.path.isfile(client_cred):
                # Runs only if there are any missing credential files
                Mastodon.create_app(
                    config['main']['name'],
                    api_base_url=api_base_url,
                    to_file=client_cred
                )
            picture = '/root/pwnagotchi.png'
            display.on_manual_mode(last_session)
            display.image().save(picture, 'png')
            display.update(force=True)

            try:
                logging.info('Connecting to Mastodon API')
                mastodon = Mastodon(
                    client_id=client_cred,
                    api_base_url=api_base_url
                )
                mastodon.log_in(
                    email,
                    password,
                    to_file=user_cred
                )
                mastodon = Mastodon(
                    access_token=user_cred,
                    api_base_url=api_base_url
                )
                message = Voice(lang=config['main']['lang']).on_last_session_tweet(last_session)
                mastodon.status_post(
                    message,
                    media_ids=mastodon.media_post(picture),
                    visibility=visibility
                )

                last_session.save_session_id()
                logging.info("posted: %s" % message)
                display.set('status', 'Posted!')
                display.update(force=True)
            except Exception:
                logging.exception("error while posting")
