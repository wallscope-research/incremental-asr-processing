from __future__ import division
import json
import os

import yaml
from ibm_watson.websocket import AudioSource, RecognizeCallback

try:
    from Queue import Queue, Full
except ImportError:
    from queue import Queue, Full


from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


class IBMCloud:

    def __init__(self):
        data_path = os.path.join(os.getcwd().replace('/eval', '/data'), 'config')
        _ibm_cloud_speech_credentials = os.path.join(data_path, 'ibm_speech_credentials.json')
        print('_ibm_cloud_speech_credentials: {}'.format(_ibm_cloud_speech_credentials))
        with open(_ibm_cloud_speech_credentials) as credentials_file:
            ibm_credentials = json.load(credentials_file)

            authenticator = IAMAuthenticator(apikey=ibm_credentials.get('apikey'))
            self.speech_to_text = SpeechToTextV1(authenticator=authenticator)
            self.speech_to_text.set_service_url(ibm_credentials.get('url'))

        with open(os.path.join(data_path, 'config', 'watson_config.yaml')) as alana_yaml:
            self._config = yaml.load(alana_yaml, Loader=yaml.FullLoader)

    def get_service(self):
        return self.speech_to_text

    def listen(self, audio_file: str, callback: RecognizeCallback):
        with open(audio_file, 'rb') as audio_file:
            audio_source = AudioSource(audio_file)
            self.speech_to_text.recognize_using_websocket(audio=audio_source,
                                                          content_type=self._config.get('content_type'),
                                                          recognize_callback=callback,
                                                          interim_results=self._config.get('interim_results'),
                                                          timestamps=self._config.get('timestamps'),
                                                          speaker_labels=self._config.get('speaker_labels'),
                                                          model=self._config.get('model'),
                                                          max_alternatives=self._config.get('max_alternatives'),
                                                          profanity_filter=self._config.get('profanity_filter'))