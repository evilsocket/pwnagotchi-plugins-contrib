import logging
import json
import os
import glob

import pwnagotchi
import pwnagotchi.plugins as plugins

from flask import abort
from flask import send_from_directory
from flask import render_template_string

TEMPLATE = """
{% extends "base.html" %}
{% set active_page = "passwordsList" %}

{% block title %}
    {{ title }}
{% endblock %}

{% block meta %}
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, user-scalable=0" />
{% endblock %}

{% block styles %}
{{ super() }}
    <style>

        #searchText {
            width: 100%;
        }

        table {
            table-layout: auto;
            width: 100%;
        }

        table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
        }

        th, td {
            padding: 15px;
            text-align: left;
        }

        table tr:nth-child(even) {
            background-color: #eee;
        }

        table tr:nth-child(odd) {
            background-color: #fff;
        }

        table th {
            background-color: black;
            color: white;
        }

        @media screen and (max-width:700px) {
            table, tr, td {
                padding:0;
                border:1px solid black;
            }

            table {
                border:none;
            }

            tr:first-child, thead, th {
                display:none;
                border:none;
            }

            tr {
                float: left;
                width: 100%;
                margin-bottom: 2em;
            }

            table tr:nth-child(odd) {
                background-color: #eee;
            }

            td {
                float: left;
                width: 100%;
                padding:1em;
            }

            td::before {
                content:attr(data-label);
                word-wrap: break-word;
                background-color: black;
                color: white;
                border-right:2px solid black;
                width: 20%;
                float:left;
                padding:1em;
                font-weight: bold;
                margin:-1em 1em -1em -1em;
            }
        }
    </style>
{% endblock %}
{% block script %}
    var searchInput = document.getElementById("searchText");
    searchInput.onkeyup = function() {
        var filter, table, tr, td, i, txtValue;
        filter = searchInput.value.toUpperCase();
        table = document.getElementById("tableOptions");
        if (table) {
            tr = table.getElementsByTagName("tr");

            for (i = 0; i < tr.length; i++) {
                td = tr[i].getElementsByTagName("td")[0];
                if (td) {
                    txtValue = td.textContent || td.innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        tr[i].style.display = "";
                    }else{
                        tr[i].style.display = "none";
                    }
                }
            }
        }
    }

{% endblock %}

{% block content %}
    <input type="text" id="searchText" placeholder="Search for ..." title="Type in a filter">
    <table id="tableOptions">
        <tr>
            <th>SSID</th>
            <th>BSSID</th>
            <th>Client station</th>
            <th>Password</th>
        </tr>
        {% for p in passwords %}
            <tr>
                <td data-label="SSID">{{p["ssid"]}}</td>
                <td data-label="BSSID">{{p["bssid"]}}</td>
                <td data-label="Client station">{{p["clientStation"]}}</td>
                <td data-label="Password">{{p["password"]}}</td>
            </tr>
        {% endfor %}
    </table>
{% endblock %}
"""

class WpaSecList(plugins.Plugin):
    __author__ = '37124354+dbukovac@users.noreply.github.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'List cracked passwords from wpa-sec'

    def __init__(self):
        self.ready = False

    def on_loaded(self):
        logging.info("[Wpa-sec-list] plugin loaded")

    def on_config_changed(self, config):
        self.config = config
        self.ready = True

    def on_webhook(self, path, request):
        if not self.ready:
            return "Plugin not ready"

        if path == "/" or not path:
            try:
                passwords = []
                with open(self.config['bettercap']['handshakes'] + "/wpa-sec.cracked.potfile") as file_in:
                    for line in file_in:
                        fields = line.split(":")
                        password = {
                            "ssid": fields[2],
                            "bssid": fields[0],
                            "clientStation": fields[1],
                            "password": fields[3]
                        }
                        passwords.append(password)
                return render_template_string(TEMPLATE,
                                        title="Passwords list",
                                        passwords=passwords)
            except Exception as e:
                logging.error("[wpa-sec-list] error while loading passwords: %s" % e)
                logging.debug(e, exc_info=True)
