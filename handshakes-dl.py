import logging
import json
import os
import glob
import zipfile
from io import BytesIO

import pwnagotchi
import pwnagotchi.plugins as plugins

from flask import abort
from flask import send_from_directory, send_file
from flask import render_template_string

TEMPLATE = """
{% extends "base.html" %}
{% set active_page = "handshakes" %}

{% block title %}
    {{ title }}
{% endblock %}

{% block content %}
    <a class="ui-btn" href="/plugins/handshakes-dl/all">Download Zip</a>
    <ul id="list" data-role="listview" style="list-style-type:disc;">
        {% for handshake in handshakes %}
            <li class="file">
                <a href="/plugins/handshakes-dl/{{handshake}}">{{handshake}}</a>
            </li>
        {% endfor %}
    </ul>
{% endblock %}
"""

class HandshakesDL(plugins.Plugin):
    __author__ = 'me@sayakb.com'
    __version__ = '0.1.0'
    __license__ = 'GPL3'
    __description__ = 'Download handshake captures from web-ui.'

    def __init__(self):
        self.ready = False

    def on_loaded(self):
        logging.info("[HandshakesDL] plugin loaded")

    def on_ready(self, agent):
        self.config = agent.config()
        self.ready = True

    def on_internet_available(self, agent):
        self.config = agent.config()
        self.ready = True

    def on_webhook(self, path, request):
        if not self.ready:
            return "Plugin not ready"

        if path == "/" or not path:
            handshakes = glob.glob(os.path.join(self.config['bettercap']['handshakes'], "*.pcap"))
            handshakes = [os.path.basename(path)[:-5] for path in handshakes]
            return render_template_string(TEMPLATE,
                                    title="Handshakes | " + pwnagotchi.name(),
                                    handshakes=handshakes)    
        elif path == "all":
            logging.info(f"[HandshakesDL] creating Zip-File in memory")
            memory_file = BytesIO()
            with zipfile.ZipFile(memory_file, 'w') as zf:
                files = glob.glob(os.path.join(self.config['bettercap']['handshakes'], "*.pcap"))
                try:
                    for individualFile in files:
                        zf.write(individualFile)
                except Exception as e:
                    logging.error(f"[HandshakesDL] {e}")
                    abort(404)
            memory_file.seek(0)
            logging.info(f"[HandshakesDL] serving handshakes.zip")
            return send_file(memory_file, attachment_filename='handshakes.zip', as_attachment=True)
        else:
            dir = self.config['bettercap']['handshakes']
            try:
                logging.info(f"[HandshakesDL] serving {dir}/{path}.pcap")
                return send_from_directory(directory=dir, filename=path+'.pcap', as_attachment=True)
            except FileNotFoundError:
                abort(404)
