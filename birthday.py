import os
import json
import logging
import datetime

import pwnagotchi
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


class Birthday(plugins.Plugin):
    __author__ = 'nullm0ose'
    __version__ = '1.0.1'
    __license__ = 'MIT'
    __description__ = 'A plugin that shows the age and birthday of your Pwnagotchi.'

    def __init__(self):
        self.born_at = 0

    def on_loaded(self):
        data_path = '/root/brain.json'
        self.load_data(data_path)

    def on_ui_setup(self, ui):
        if self.options['show_age']:
            ui.add_element('Age', LabeledValue(color=BLACK, label=' ♥ Age ', value='',
                                               position=(int(self.options['age_x_coord']),
                                                         int(self.options['age_y_coord'])),
                                               label_font=fonts.Bold, text_font=fonts.Medium))
        elif self.options['show_birthday']:
            ui.add_element('Birthday', LabeledValue(color=BLACK, label=' ♥ Born: ', value='',
                                                    position=(int(self.options['age_x_coord']),
                                                              int(self.options['age_y_coord'])),
                                                    label_font=fonts.Bold, text_font=fonts.Medium))

    def on_unload(self, ui):
        if self.options['show_age']:
            with ui._lock:
                ui.remove_element('Age')
        elif self.options['show_birthday']:
            with ui._lock:
                ui.remove_element('Birthday')

    def on_ui_update(self, ui):
        if self.options['show_age']:
            age = self.calculate_age()
            age_labels = []
            if age[0] == 1:
                age_labels.append(f'{age[0]}Yr')
            elif age[0] > 1:
                age_labels.append(f'{age[0]}Yrs')
            if age[1] > 0:
                age_labels.append(f'{age[1]}m')
            if age[2] > 0:
                if age[0] < 1:
                    age_labels.append(f'{age[2]} days')
                else:
                    age_labels.append(f'{age[2]}d')
            age_string = ' '.join(age_labels)
            ui.set('Age', age_string)
        elif self.options['show_birthday']:
            born_date = datetime.datetime.fromtimestamp(self.born_at)
            birthday_string = born_date.strftime('%b %d \'%y')
            ui.set('Birthday', birthday_string)

    def load_data(self, data_path):
        if os.path.exists(data_path):
            with open(data_path) as f:
                data = json.load(f)
                self.born_at = data['born_at']

    def calculate_age(self):
        born_date = datetime.datetime.fromtimestamp(self.born_at)
        today = datetime.datetime.now()
        age = today - born_date
        days = age.days
        months = days // 30
        years = months // 12
        months %= 12
        days %= 30
        return years, months, days
