import os
import logging
from pwnagotchi.voice import Voice
import pwnagotchi.plugins as plugins
try:
    from mastodon import Mastodon
except ImportError:
    logging.error('[mastodon] Could not import mastodon')

class MastodonStatus(plugins.Plugin):
    __author__ = 'retiolus'
    __version__ = '2.0.0'
    __license__ = 'GPL3'
    __description__ = '''
                    Periodically post status updates. Based on original Mastodon plugin by siina@siina.dev.
                    To use this plugin make sure Mastodon.py library is installed using "sudo pip install Mastodon.py"
                    Don't forget do add the following options in your config:
                    main.plugins.mastodon.enabled = True
                    main.plugins.mastodon.instance_url = https://your-instance.com
                    main.plugins.mastodon.token = your-generated-token
                    main.plugins.mastodon.visibility = unlisted
                    Enjoy!'''

    def on_loaded(self):
        try:
            logging.info("[mastodon] mastodon plugin loaded.")
        except Exception as e:
            logging.error("[mastodon] Error loading plugin: %s" % str(e))

    def post_to_mastodon(self, agent, last_session, api_base_url, token, visibility):
        try:
            picture = '/root/pwnagotchi.png'
            display = agent.view()
            config = agent.config()
            display.on_manual_mode(last_session)
            display.image().save(picture, 'png')
            display.update(force=True)

            try:
                logging.info('[mastodon] Connecting to Mastodon API')
                mastodon = Mastodon(
                    access_token=token,
                    api_base_url=api_base_url
                )
                message = Voice(lang=config['main']['lang']).on_last_session_tweet(last_session)
                logging.info("[mastodon] Posting status on Mastodon")
                mastodon.status_post(
                    message,
                    media_ids=mastodon.media_post(picture),
                    visibility=visibility
                )

                last_session.save_session_id()
                logging.info("[mastodon] Posted: %s" % message)
                display.set('status', 'Posted!')
                display.update(force=True)
            except Exception as mastodon_exception:
                logging.error("[mastodon] Error while posting to Mastodon: %s" % str(mastodon_exception))
        except Exception as post_exception:
            logging.error("[mastodon] Error while posting: %s" % str(post_exception))

    # Called when there's available internet
    def on_internet_available(self, agent):
        try:
            config = agent.config()
            last_session = agent.last_session
            api_base_url = self.options['instance_url']
            token = self.options['token']
            visibility = self.options['visibility']
            
            if last_session.is_new() and last_session.handshakes > 0:
                logging.info("[mastodon] Detected internet and new activity: time to post!")

                try:
                    self.post_to_mastodon(agent, last_session, api_base_url, token, visibility)
                except Exception as post_exception:
                    logging.error("[mastodon] Error while posting: %s" % str(post_exception))
        except Exception as on_internet_available:
                    logging.error("[mastodon] Error while initiating on_internet_available: %s" % str(on_internet_available))
