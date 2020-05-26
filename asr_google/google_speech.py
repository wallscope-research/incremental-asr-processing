from __future__ import division

import io
import os
import wave

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

import yaml
from google.cloud import speech
from google.cloud.speech import types
from google.cloud.speech import enums
from google.oauth2 import service_account


class GoogleCloud:

    def __init__(self):
        data_path = os.path.join(os.getcwd().replace('/eval', '/data').replace('/asr_google', '/data'), 'config')
        _google_cloud_speech_credentials = os.path.join(data_path, 'google_credentials.json')
        credentials = service_account.Credentials.from_service_account_file(_google_cloud_speech_credentials)

        with open(os.path.join(data_path, 'google_config.yaml')) as config_yaml:
            self._google_config = yaml.load(config_yaml, Loader=yaml.FullLoader)
        self._google_config['config']['encoding'] = enums.RecognitionConfig.AudioEncoding.FLAC
        self._client = speech.SpeechClient(credentials=credentials)

    def transcribe_streaming(self, stream_file: str):
        """Streams transcription of the given audio file."""

        # [START speech_python_migration_streaming_request]
        with io.open(stream_file, 'rb') as audio_file:
            content = audio_file.read()

        stream = [content]

        requests = (types.StreamingRecognizeRequest(audio_content=chunk)
                    for chunk in stream)

        wf = wave.open(stream_file, mode="rb")

        diarization_config = types.SpeakerDiarizationConfig(
            enable_speaker_diarization=self._google_config.get('config').get('diarization_config').get('enable_speaker_diarization'),
            max_speaker_count=self._google_config.get('config').get('diarization_config').get('max_speaker_count'),
            min_speaker_count=self._google_config.get('config').get('diarization_config').get('min_speaker_count')
        )

        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=wf.getframerate(),
            model=self._google_config.get('config').get('model'),
            use_enhanced=self._google_config.get('config').get('use_enhanced'),
            enable_word_time_offsets=self._google_config.get('config').get('enable_word_time_offsets'),
            language_code=self._google_config.get('config').get('language_code'),
            diarization_config=diarization_config,
            audio_channel_count=wf.getnchannels()
        )

        streaming_config = types.StreamingRecognitionConfig(
            config=config,
            interim_results=self._google_config.get('interim_results')
        )

        responses = self._client.streaming_recognize(streaming_config, requests)
        return responses


if __name__ == '__main__':
    google_recogniser = GoogleCloud()
    google_recogniser.transcribe_streaming('/Users/yy165/Yanchao_Yu/Job/HW/SPRING/Code/incremental-asr-evaluation/data/avdiar/audios/Seq01-1P-S0M1.wav')
