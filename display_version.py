from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
import pwnagotchi
import logging


class PwnagotchiVersion(plugins.Plugin):
    __author__ = 'https://github.com/Teraskull/'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'A plugin that will add the Pwnagotchi version to the left of the current mode.'

    def on_loaded(self):
        logging.info('Pwnagotchi Version Plugin loaded.')

    def on_ui_setup(self, ui):
        ui.add_element(
            'version',
            LabeledValue(
                color=BLACK,
                label='',
                value='v0.0.0',
                position=(185, 110),
                label_font=fonts.Small,
                text_font=fonts.Small
            )
        )

    def on_ui_update(self, ui):
        ui.set('version', f'v{pwnagotchi.__version__}')
