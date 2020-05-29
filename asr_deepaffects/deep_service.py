import io
import json
import os

import requests
import base64
import yaml

OK_CODE = 202
HTTP_HEADER = {
    "Content-Type": "application/json"
}


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
        response = requests.post(url=self._url, json=self._payload, headers=headers, params=self._querystring)
        if response.status_code == OK_CODE:
            _response = requests.post(url=self._querystring['webhook'], headers=HTTP_HEADER)
            print('response: {}'.format(response.json()))
            if _response.status_code == OK_CODE:
                print('response JSON: {}'.format(_response.json()))
            else:
                print(
                    'something wrong with your connection: {}, {}'.format(_response.status_code, _response.reason))

        return response


if __name__ == '__main__':
    recogniser = DeepAffectsCloud()
    responses = recogniser.listen('/Users/yy165/Yanchao_Yu/Job/HW/SPRING/Code/incremental-asr-evaluation/data/avdiar/audios/Seq06-2P-S1M0.wav')
    print("responses: {}".format(responses.content))
    print("responses: {}".format(responses.status_code))
    print("responses: {}".format(responses.json()))
    print("responses: {}".format(responses.text))
