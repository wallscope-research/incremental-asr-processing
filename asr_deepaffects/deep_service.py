import io
import os

import requests
import base64

import yaml


class DeepAffectsCloud:

    def __init__(self):
        data_path = os.path.join(os.getcwd().replace('/eval', '/data'), 'config')
        with open(os.path.join(data_path, 'google_config.yaml')) as config_yaml:
            config = yaml.load(config_yaml, Loader=yaml.FullLoader)
        self._url = config.get('url')
        self._querystring = config.get('querystring')
        self._payload = config.get('payload')

    def listen(self, stream_file: str):
        with io.open(stream_file, 'rb') as audio_file:
            audio_content = audio_file.read()
        self._payload["content"] = base64.b64encode(audio_content).decode('utf-8')
        headers = {
            'Content-Type': "application/json",
        }
        response = requests.post(self._url, json=self._payload, headers=headers, params=self._querystring)
        return response