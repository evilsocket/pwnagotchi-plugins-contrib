import pwnagotchi.plugins as plugins
import requests
import logging

class ntfy(plugins.Plugin):
    __author__ = "retiolus"
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = '''A plugin for Pwnagotchi to send notifications and alerts to devices via ntfy service.
                    Don't forget to add the following options in your config (token is optional):
                    main.plugins.ntfy.enabled = true
                    main.plugins.ntfy.name = pwnagotchi
                    main.plugins.ntfy.serverlink = https://ntfy.sh/yourntfylink
                    main.plugins.ntfy.token = tk_yourntfytoken
                    Enjoy!'''
        
    def on_loaded(self):
        try:
            self.name = self.options.get('name', 'pwnagotchi')
            self.serverlink = self.options['serverlink']
            self.token = self.options.get('token', None)
            self.picture = '/root/pwnagotchi.png'
            
            logging.info(f"[ntfy] Plugin initialized with device name: '{self.name}' and server URL: {self.serverlink}")
        except Exception as e:
            logging.error(f"[ntfy] An issue occurred during plugin initialization: {str(e)}")

    def send_notification(self, message_text, file_path=None):
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        data = {'message': message_text}
        files = {}
        
        if file_path:
            with open(file_path, 'rb') as file_data:
                files["file"] = (file_path.split('/')[-1], file_data)
        
        try:
            response = requests.post(self.serverlink, data=data, files=files, headers=headers)
            
            if response.status_code == 200:
                logging.info(f"[ntfy] Notification sent successfully: '{message_text}'")
            else:
                logging.warning(f"[ntfy] Server responded with status code: {response.status_code}. Message might not have been delivered.")
        except requests.RequestException as e:
            logging.error(f"[ntfy] Failed to send notification due to: {e}")

    # def on_internet_available(self, agent):
    #     message = f'Congratulations! Your {self.name} is now connected to the Internet.'
    #     self.send_notification(message, self.picture)
  
    def on_handshake(self, agent, filename, access_point, client_station):
        message = f'Your {self.name} has captured a new handshake from {client_station} via {access_point}.'
        self.send_notification(message, filename)

    def on_peer_detected(self, agent, peer):
        message = f'A new peer, {peer}, has been detected by your {self.name}!'
        self.send_notification(message, self.picture)

    def on_peer_lost(self, agent, peer):
        message = f'Your {self.name} lost connection with peer: {peer}.'
        self.send_notification(message, self.picture)
    
    # TODO
    def on_unread_messages(self, count, total):
        pass
