import json
from urllib import request
import requests

from Main.core.FileParser import File


class BackendAPI:
    """
    API class to interface with OCR-RAG backend
    """
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
        """
        Check if authenticated
        :return:
        """
        if self.authentication is None:
            return False
        return True

    def get_files(self):
        """
        get all user files and their status in the database
        :return:
        """
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
        """
        upload a file, and indigate its tags and whether it needs OCR to be parsed or not
        """
        if not self.is_authenticated():
            return False
        endpoint = 'data/files/'
        data = {'name': file_name,
                'tags': tags,
                'ocr': ocr}
        r = requests.post(url=self.base_url + endpoint, files={'file': file}, data=data, headers=self.authentication)
        if r.status_code == 201:
            return

    def load(self, id):
        """
        Load parsed file by id
        """
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

    def delete(self, id):
        """
        delete file by id
        """
        if not self.is_authenticated():
            return False

        endpoint = f'data/files/{id}/'
        r = requests.delete(url=self.base_url + endpoint, headers=self.authentication,
                         params={})
        if r.status_code == 204:
            return True
        return False

    def download(self, id):
        """
        download raw file as uploaded
        """
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

    def get_tags(self):
        """
        get all user tags
        """
        if not self.is_authenticated():
            return False
        endpoint = "/data/tags/"
        r = requests.get(url=self.base_url + endpoint, headers=self.authentication,
                         params={})
        if r.status_code == 200:
            return r.content
        return None
