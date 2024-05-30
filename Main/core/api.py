import json
from urllib import request
import requests

from Main.core.FileParser import File


class BackendAPI:
    def __init__(self, url=None):
        self.user = None
        self.authentication = None
        self.base_url = "https://ocr-rag.services.synapse-analytics.io/"
        if url:
            self.base_url = url

    def login(self, username, password):
        """
        attempt login
        :return:
        """
        credentials = {
            "username": username,
            "password": password
        }
        endpoint = 'accounts/login/'
        r = requests.post(url=self.base_url + endpoint, data=credentials)
        if r.status_code == 200:
            self.user = username
            token = json.loads(r.content)
            self.authentication = {
                'Authorization': f'Token {token.get("token", "")}',
                'Accept': 'application/json'
            }
            return True

        return False

    def is_authenticated(self):
        if self.authentication is None:
            return False
        return True

    def get_files(self):
        if not self.is_authenticated():
            return False
        endpoint = 'data/files/'
        r = requests.get(url=self.base_url + endpoint, headers=self.authentication,
                         params={})
        if r.status_code == 200:
            output = json.loads(r.content)
            return output
        return None

    def upload(self, file_name, file, tags=[], ocr=False):
        if not self.is_authenticated():
            return False
        endpoint = 'data/files/'
        data = {'name': file_name,
                'tags': tags,
                'ocr': ocr}
        r = requests.post(url=self.base_url + endpoint, files={'file': file}, data=data, headers=self.authentication)
        if r.status_code == 201:
            return
        pass

    def load(self, id):
        if not self.is_authenticated():
            return False

        endpoint = f'data/download-file/{id}/parsed/'
        r = requests.get(url=self.base_url + endpoint, headers=self.authentication,
                         params={})
        if r.status_code == 200:
            parsed_response = json.loads(r.content)
            file_response = requests.get(parsed_response.get('file_url', ''))

            output = File.load(file_response.content)
            return output
        return None

    def download(self, id):
        if not self.is_authenticated():
            return False
        endpoint = f'data/download-file/{id}/original/'
        r = requests.get(url=self.base_url + endpoint, headers=self.authentication,
                         params={})
        if r.status_code == 200:
            parsed_response = json.loads(r.content)
            file_response = requests.get(parsed_response.get('file_url', ''))
            return file_response.content
        return None

    def filter(self):
        if not self.is_authenticated():
            return False

        pass
