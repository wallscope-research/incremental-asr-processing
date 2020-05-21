import io
import os

import requests
import base64
import yaml

from webhooks import webhook


class DeepAffectsCloud:

    def __init__(self):
        data_path = os.path.join(os.getcwd().replace('/eval', '/data').replace('/asr_deepaffects', '/data'), 'config')
        with open(os.path.join(data_path, 'deep_config.yaml')) as config_yaml:
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


if __name__ == '__main__':
    recogniser = DeepAffectsCloud()
    responses = recogniser.listen('/Users/yy165/Yanchao_Yu/Job/HW/SPRING/Code/incremental-asr-evaluation/data/avdiar/audios/Seq06-2P-S1M0.wav')
    print("responses: {}".format(responses.content))
    print("responses: {}".format(responses.status_code))
    print("responses: {}".format(responses.json()))
