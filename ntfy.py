import pwnagotchi.plugins as plugins
import requests
import logging

class ntfy(plugins.Plugin):
    __author__ = "retiolus"
    __version__ = '1.1.0'
    __license__ = 'GPL3'
    __description__ = '''A plugin for Pwnagotchi to send notifications and alerts to devices via ntfy service.
                    Don't forget to add the following options in your config (token, priority and icon are optional):
                    main.plugins.ntfy.enabled = true
                    main.plugins.ntfy.name = pwnagotchi
                    main.plugins.ntfy.serverlink = https://ntfy.sh/yourntfylink
                    main.plugins.ntfy.token = tk_yourntfytoken
                    main.plugins.ntfy.priority = 3
                    main.plugins.ntfy.icon = https://files.catbox.moe/1toze0.jpg
                    Enjoy!'''
        
    def on_loaded(self):
        try:
            self.name = self.options.get('name', 'pwnagotchi')
            self.serverlink = self.options['serverlink']
            self.token = self.options.get('token', None)
            self.priority = self.options.get('priority', '3')
            self.icon = self.options.get('icon', 'https://files.catbox.moe/1toze0.jpg')
            self.picture = '/root/pwnagotchi.png'

            self.internet_notification_sent = False
            self.unread_notification_sent = False
            self.prev_unread_count = 0
            
            logging.info(f"[ntfy] Plugin initialized with device name: '{self.name}' and server URL: {self.serverlink}")
        except Exception as e:
            logging.error(f"[ntfy] An issue occurred during plugin initialization: {str(e)}")

    def send_notification(self, title_text, message_text, file_path=None, tags=None):
        headers = {}
        headers["Title"] = title_text.encode(encoding='utf-8')
        headers["Priority"] = self.priority
        headers['Icon'] = self.icon
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        if tags:
            headers["Tags"] = tags
        
        if file_path:
            with open(file_path, 'rb') as file_data:
                data = file_data
                headers["Filename"] = file_path.split('/')[-1]
        else:
            data = message_text.encode(encoding='utf-8')
        
        try:
            response = requests.post(self.serverlink, data=data, headers=headers)
            
            if response.status_code == 200:
                logging.info(f"[ntfy] Notification sent successfully: '{message_text}'")
                return True
            else:
                logging.warning(f"[ntfy] Server responded with status code: {response.status_code}. Message might not have been delivered.")
                return False
        except requests.RequestException as e:
            logging.error(f"[ntfy] Failed to send notification due to: {e}")
            return False

    def on_internet_available(self, agent):
        if not self.internet_notification_sent:
            message = f'Congratulations! Your {self.name} is now connected to the Internet.'
            success = self.send_notification(title_text=self.name, message_text=message, tags="rotating_light")
            if success:
                self.internet_notification_sent = True
  
    def on_handshake(self, agent, filename, access_point, client_station):
        message = f'Your {self.name} has captured a new handshake from {client_station} via {access_point}.'
        self.send_notification(title_text=message, message_text=message, file_path=filename, tags="triangular_flag_on_post")

    def on_peer_detected(self, agent, peer):
        message = f'A new peer, {peer}, has been detected by your {self.name}!'
        self.send_notification(title_text=self.name, message_text=message, tags="revolving_hearts")

    def on_peer_lost(self, agent, peer):
        message = f'Your {self.name} lost connection with peer: {peer}.'
        self.send_notification(title_text=self.name, message_text=message, tags="broken_heart")
    
    def on_unread_messages(self, count, total):
        if not self.unread_notification_sent or count > self.prev_unread_count:
            plural = 's' if count > 1 else ''
            message = f'You have {count} new message{plural}!'
            success = self.send_notification(title_text=self.name, message_text=message, tags="envelope")
            if success:
                self.unread_notification_sent = True
        self.prev_unread_count = count

    # TODO

    # ISN'T ON_NEW_PEER = ON_PEER_DETECTED ?
    # def on_new_peer(self, peer):
    #     pass
    
    # def on_uploading(self, to):
    #     pass
