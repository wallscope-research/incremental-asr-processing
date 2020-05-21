from __future__ import division

import io
import os
import wave

import yaml
from google.cloud import speech_v1p1beta1
from google.cloud.speech_v1p1beta1 import types
from google.cloud.speech_v1p1beta1.gapic import enums
from google.oauth2 import service_account


class GoogleCloud:

    def __init__(self):
        data_path = os.path.join(os.getcwd().replace('/eval', '/data').replace('/asr_google', '/data'), 'config')
        _google_cloud_speech_credentials = os.path.join(data_path, 'google_credentials.json')
        credentials = service_account.Credentials.from_service_account_file(_google_cloud_speech_credentials)

        with open(os.path.join(data_path, 'google_config.yaml')) as config_yaml:
            self._google_config = yaml.load(config_yaml, Loader=yaml.FullLoader)
        self._google_config['config']['encoding'] = enums.RecognitionConfig.AudioEncoding.LINEAR16
        self._client = speech_v1p1beta1.SpeechClient(credentials=credentials)

    def listen(self, stream_file: str):
        # [START speech_python_migration_streaming_request]
        with io.open(stream_file, 'rb') as audio_file:
            content = audio_file.read()
        stream = [content]
        requests = (types.StreamingRecognizeRequest(audio_content=chunk)
                    for chunk in stream)
        wf = wave.open(stream_file, mode="rb")
        self._google_config['config']['sample_rate_hertz'] = wf.getframerate()
        self._google_config['config']['audio_channel_count'] = wf.getnchannels()

        _responses = self._client.streaming_recognize(self._google_config, requests)
        return _responses


if __name__ == '__main__':
    google_recogniser = GoogleCloud()
    responses = google_recogniser.listen('/Users/yy165/Yanchao_Yu/Job/HW/SPRING/Code/incremental-asr-evaluation/data/swb/audios/Seq06-2P-S1M0.wav')
    for response in responses:
        if not response.results:
            continue
        for result in response.results:
            if result.is_final:
                # First alternative has words tagged with speakers
                alternative = result.alternatives[0]

                for word in alternative.words:
                    print(u"Word: {}".format(word))

